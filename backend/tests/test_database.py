import pytest
from unittest.mock import patch, MagicMock
from src.database import get_db_client

@patch('src.database.MongoClient')
def test_get_db_client(mock_mongo_client):
    mock_client_instance = MagicMock()
    mock_client_instance.admin.command.return_value = {'ok': 1.0}
    mock_mongo_client.return_value = mock_client_instance
    
    client = get_db_client()
    assert client is not None
    assert client.admin.command('ping')['ok'] == 1.0