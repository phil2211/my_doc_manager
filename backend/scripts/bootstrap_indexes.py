from __future__ import annotations

"""Bootstrap indexes outside the FastAPI app."""

import asyncio

from app.db.client import close_client, get_database
from app.db.indexes import ensure_indexes


async def main() -> None:
    db = get_database()
    await ensure_indexes(db)
    await close_client()
    print("Indexes ensured.")


if __name__ == "__main__":
    asyncio.run(main())
