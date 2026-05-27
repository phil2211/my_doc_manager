def save_correction(db, raw_text: str, corrected_metadata: dict):
    # Save the correction for few-shot learning
    db.corrections.insert_one({
        "raw_text": raw_text,
        "metadata": corrected_metadata
    })
    
    # Update known senders
    sender = corrected_metadata.get("sender")
    if sender:
        db.senders.update_one(
            {"name": sender},
            {"$set": {"name": sender}},
            upsert=True
        )