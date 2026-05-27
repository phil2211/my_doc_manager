def generate_filename(metadata: dict) -> str:
    date = metadata.get("date", "UnknownDate")
    cat = metadata.get("category", "UnknownCategory")
    sender = metadata.get("sender", "UnknownSender")
    return f"{date}_{cat}_{sender}.pdf"

# (OAuth and Upload functions would be implemented here, mocked in tests)