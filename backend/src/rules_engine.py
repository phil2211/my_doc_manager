import re

def extract_metadata_via_rules(text: str, known_senders: list[str]) -> dict:
    metadata = {"date": None, "sender": None, "category": None}
    
    # Simple date regex YYYY-MM-DD
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if date_match:
        metadata["date"] = date_match.group(0)
        
    for sender in known_senders:
        if sender.lower() in text.lower():
            metadata["sender"] = sender
            break
            
    return metadata