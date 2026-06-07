import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import asyncio
import random
from datetime import datetime, timedelta

from app.database import db


async def load_demo_data():

    asset_id = "6d5f04cf-5085-45f3-b5da-b2b40b82c915"

    data_source_id = "f3c8fe6c-582a-4b34-8d88-076a015e0be2"

    start_date = datetime(2025, 1, 1)

    records = []

    current_price = 190

    for i in range(365):

        current_date = start_date + timedelta(days=i)

        open_price = current_price

        high_price = open_price + random.uniform(0, 5)

        low_price = open_price - random.uniform(0, 5)

        close_price = random.uniform(low_price, high_price)

        volume = random.randint(
            10000000,
            100000000
        )

        records.append({
            "asset_id": asset_id,
            "data_source_id": data_source_id,

            "business_date": current_date,
            "business_date_string": current_date.date().isoformat(),

            "business_year": current_date.year,

            "system_time": datetime.utcnow(),

            "values": {
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            },

            "attributes": {
                "currency": "USD",
                "frequency": "daily"
            },

            "is_deleted": False,

            "provenance": {
                "provider": data_source_id,
                "source": "demo_loader"
            }
        })

        current_price = close_price

    result = await db["time_series_points"].insert_many(
        records
    )

    print(
        f"Inserted {len(result.inserted_ids)} demo records."
    )


if __name__ == "__main__":
    asyncio.run(load_demo_data())