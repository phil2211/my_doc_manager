from src.learning_service import save_correction
from mongomock import MongoClient

def test_save_correction():
    client = MongoClient()
    db = client.doc_manager
    save_correction(db, "Raw text here", {"sender": "New Sender", "category": "Bill"})
    
    assert db.corrections.count_documents({}) == 1
    assert db.senders.count_documents({"name": "New Sender"}) == 1