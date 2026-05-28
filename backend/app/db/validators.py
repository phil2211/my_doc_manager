from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase


async def apply_collection_validators(db: AsyncIOMotorDatabase) -> None:
    validators = {
        "source_files": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["filename", "storage_path", "sha256", "uploaded_at", "status"],
                "properties": {
                    "filename": {"bsonType": "string"},
                    "storage_path": {"bsonType": "string"},
                    "sha256": {"bsonType": "string"},
                    "uploaded_at": {"bsonType": "date"},
                    "status": {"bsonType": "string"},
                },
            }
        },
        "pages": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["source_file_id", "page_number"],
                "properties": {
                    "source_file_id": {"bsonType": "objectId"},
                    "page_number": {"bsonType": "int"},
                    "is_scanned": {"bsonType": "bool"},
                    "text_content": {"bsonType": "string"},
                },
            }
        },
        "logical_documents": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["source_file_id", "page_ids"],
                "properties": {
                    "source_file_id": {"bsonType": "objectId"},
                    "page_ids": {"bsonType": "array", "items": {"bsonType": "objectId"}},
                    "doc_type": {"bsonType": "string"},
                    "search_text": {"bsonType": "string"},
                },
            }
        },
        "processing_jobs": {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["source_file_id", "status", "progress_pct", "started_at"],
                "properties": {
                    "source_file_id": {"bsonType": "objectId"},
                    "status": {"bsonType": "string"},
                    "progress_pct": {"bsonType": "int"},
                    "started_at": {"bsonType": "date"},
                },
            }
        },
    }

    for collection_name, validator in validators.items():
        try:
            await db.command(
                "collMod",
                collection_name,
                validator=validator,
                validationLevel="moderate",
            )
        except Exception:
            await db.create_collection(collection_name, validator=validator, validationLevel="moderate")
