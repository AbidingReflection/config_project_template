import json
import logging
from datetime import date, datetime

class SensitiveDict:
    """Custom dictionary-like class for handling sensitive data."""
    
    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return "<SensitiveDict>"

    def __str__(self):
        return self.__repr__()

    def get_data(self):
        return self._data
    

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for SensitiveDict, Logger, and date/datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, SensitiveDict):
            return str(obj)
        if isinstance(obj, logging.Logger):
            return "<Logger>"
        if isinstance(obj, (date, datetime)):
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)


def normalize_key(key: str) -> str:
    """Normalize each key by lowercasing the first character of each word (separated by spaces or underscores)."""
    parts = key.strip().replace("_", " ").split()  # Replace underscores with spaces, then split by spaces
    normalized_parts = [part[0].lower() + part[1:] if part else part for part in parts]  # Lowercase first char
    return "_".join(normalized_parts)  # Join with underscores