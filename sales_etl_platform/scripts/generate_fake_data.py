import pandas as pd
from datetime import datetime, timedelta
import uuid
import random
from pathlib import Path


def generate_fake_data(
    days_back: int = 0,
    num_stores: int = 15,
    num_transactions: int = 250
):
    """
    Generate fake stores and sales data for testing.
    Files are always written to the project-level inbox folder.
    """

    # Project root directory
    root_dir = Path(__file__).resolve().parent.parent

    # Inbox directory
    inbox_path = root_dir / "inbox"
    inbox_path.mkdir(exist_ok=True)

    # Batch date
    batch_date = (
        datetime.now() - timedelta(days=days_back)
    ).strftime("%Y%m%d")

    print(f"\nGenerating fake data for batch date: {batch_date}")

    # ======================================================
    # STORES DATA
    # ======================================================

    stores_data = []

    for i in range(num_stores):

        store_token = str(uuid.uuid4())

        stores_data.append(
            {
                "store_group": f"{random.randint(0, 0xFFFFFFFF):08X}",
                "store_token": store_token,
                "store_name": (
                    f"Store {str(i + 1).zfill(6)} - "
                    f"{random.choice(['Downtown', 'Mall', 'Beach', 'Market', 'Plaza'])}"
                ),
            }
        )

    stores_df = pd.DataFrame(stores_data)

    stores_file = (
        inbox_path /
        f"stores_{batch_date}.csv"
    )

    stores_df.to_csv(
        stores_file,
        index=False
    )

    print(
        f"Created Stores file: "
        f"{stores_file.name} "
        f"({len(stores_df)} rows)"
    )

    # ======================================================
    # SALES DATA
    # ======================================================

    sales_data = []

    base_time = datetime.strptime(
        batch_date,
        "%Y%m%d"
    )

    for _ in range(num_transactions):

        store = random.choice(stores_data)

        tx_time = base_time + timedelta(
            hours=random.randint(8, 22),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        sales_data.append(
            {
                "store_token": store["store_token"],
                "transaction_id": str(uuid.uuid4()),
                "receipt_token": "".join(
                    random.choices(
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                        k=random.randint(5, 12),
                    )
                ),
                "transaction_time": tx_time.strftime(
                    "%Y%m%dT%H%M%S.000"
                ),
                "amount": round(
                    random.uniform(8.50, 299.99),
                    2,
                ),
                "user_role": random.choice(
                    [
                        "Cashier",
                        "Manager",
                        "Seller",
                        "Trainee",
                    ]
                ),
            }
        )

    sales_df = pd.DataFrame(sales_data)

    sales_file = (
        inbox_path /
        f"sales_{batch_date}.csv"
    )

    sales_df.to_csv(
        sales_file,
        index=False
    )

    print(
        f"Created Sales file: "
        f"{sales_file.name} "
        f"({len(sales_df)} rows)"
    )

    print("\nFake data generation completed successfully!")
    print(f"Files created in: {inbox_path.resolve()}")

    print("\nGenerated files:")
    print(f" - {stores_file.name}")
    print(f" - {sales_file.name}")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("FAKE DATA GENERATOR FOR SALES ETL TEST")
    print("=" * 60)

    generate_fake_data(
        days_back=0,
        num_stores=18,
        num_transactions=320,
    )

    # Example:
    #
    # Generate last 5 days
    #
    # for i in range(5):
    #     generate_fake_data(days_back=i)