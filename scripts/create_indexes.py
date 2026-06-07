import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.database import db


async def create_indexes():
    await db["financial_assets"].create_index([
        ("asset_id", 1),
        ("is_current", 1),
        ("is_deleted", 1)
    ])

    await db["financial_assets"].create_index([
        ("symbol", 1),
        ("is_current", 1)
    ])

    await db["data_sources"].create_index([
        ("data_source_id", 1)
    ])

    await db["time_series_points"].create_index([
        ("asset_id", 1),
        ("data_source_id", 1),
        ("business_date", -1),
        ("system_time", -1)
    ])

    await db["analytics_aggregations"].create_index([
        ("computed_at", -1)
    ])

    await db["analytics_predictions"].create_index([
        ("computed_at", -1)
    ])

    print("Indexes created successfully.")


if __name__ == "__main__":
    asyncio.run(create_indexes())