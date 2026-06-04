import yaml
from pathlib import Path
import snowflake.connector
import shutil


def load_config():
    with open("/opt/airflow/config/config.yaml") as f:
        return yaml.safe_load(f)


def ingest_files(**kwargs):

    config = load_config()

    conn = snowflake.connector.connect(
        **config["snowflake"]
    )

    inbox = Path(config["paths"]["inbox"])
    archive_base = Path(config["paths"]["archive"])

    files = (
        list(inbox.glob("stores_*.csv"))
        + list(inbox.glob("sales_*.csv"))
    )

    processed = 0

    try:

        for file_path in files:

            file_name = file_path.name
            batch_date = file_path.stem.split("_")[1]

            file_type = (
                "STORES"
                if "stores" in file_name.lower()
                else "SALES"
            )

            stage_path = f"@SALES_DB.STAGING.SALES_STAGE/{batch_date}"

            put_sql = f"""
            PUT file://{file_path.absolute()}
            {stage_path}
            AUTO_COMPRESS=TRUE
            OVERWRITE=TRUE
            """

            # ---------------------------
            # COPY INTO (dynamic per type)
            # ---------------------------
            if file_type == "STORES":

                copy_sql = f"""
                COPY INTO SALES_DB.RAW.STORES
                (
                    STORE_GROUP,
                    STORE_TOKEN,
                    STORE_NAME,
                    BATCH_DATE,
                    SOURCE_FILE,
                    LOAD_TIMESTAMP
                )
                FROM (
                    SELECT
                        $1,
                        $2,
                        $3,
                        TO_DATE('{batch_date}','YYYYMMDD'),
                        '{file_name}',
                        CURRENT_TIMESTAMP()
                    FROM {stage_path}
                )
                PATTERN='.*stores.*'
                FILE_FORMAT = (
                    TYPE = CSV
                    SKIP_HEADER = 1
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                )
                FORCE = FALSE
                ON_ERROR = ABORT_STATEMENT
                """

            else:

                copy_sql = f"""
                COPY INTO SALES_DB.RAW.SALES
                (
                    STORE_TOKEN,
                    TRANSACTION_ID,
                    RECEIPT_TOKEN,
                    TRANSACTION_TIME,
                    AMOUNT,
                    USER_ROLE,
                    BATCH_DATE,
                    SOURCE_FILE,
                    LOAD_TIMESTAMP
                )
                FROM (
                    SELECT
                        $1,
                        $2,
                        $3,
                        $4,
                        REPLACE($5,'$',''),
                        $6,
                        TO_DATE('{batch_date}','YYYYMMDD'),
                        '{file_name}',
                        CURRENT_TIMESTAMP()
                    FROM {stage_path}
                )
                PATTERN='.*sales.*'
                FILE_FORMAT = (
                    TYPE = CSV
                    SKIP_HEADER = 1
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                )
                FORCE = FALSE
                ON_ERROR = ABORT_STATEMENT
                """

            with conn.cursor() as cur:

                print(f"\nUploading {file_name}")

                # ---------------------------
                # PUT FILE INTO STAGE
                # ---------------------------
                cur.execute(put_sql)
                put_results = cur.fetchall()

                for row in put_results:
                    print(row)

                print(f"Loading {file_type} into RAW")

                # ---------------------------
                # COPY INTO RAW
                # ---------------------------
                cur.execute(copy_sql)
                copy_results = cur.fetchall()

                rows_loaded = sum(
                    row[3]
                    for row in copy_results
                    if row[1] == "LOADED"
                )

                # ---------------------------
                # FILE AUDIT
                # ---------------------------
                audit_sql = f"""
                INSERT INTO SALES_DB.RAW.FILE_AUDIT
                (
                    FILE_NAME,
                    FILE_TYPE,
                    BATCH_DATE,
                    LOAD_TIMESTAMP,
                    ROWS_LOADED,
                    STATUS
                )
                VALUES
                (
                    '{file_name}',
                    '{file_type}',
                    TO_DATE('{batch_date}','YYYYMMDD'),
                    CURRENT_TIMESTAMP(),
                    {rows_loaded},
                    'SUCCESS'
                )
                """

                cur.execute(audit_sql)

            # ---------------------------
            # ARCHIVE STEP (ONLY AFTER SUCCESS)
            # ---------------------------
            archive_dir = archive_base / file_type.lower() / batch_date
            archive_dir.mkdir(parents=True, exist_ok=True)

            shutil.move(
                str(file_path),
                str(archive_dir / file_name)
            )

            processed += 1

            print(f"Loaded + Archived {file_name} ({rows_loaded} rows)")

        print(f"\nIngestion completed. Files processed: {processed}")

        return processed

    finally:
        conn.close()