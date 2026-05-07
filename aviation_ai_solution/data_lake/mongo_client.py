"""
MongoDB Client for aviation data lake.
Handles connection, indexing, and CRUD operations for aviation records.
"""

from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from datetime import datetime
import os

class AviationDataLake:
    """
    NoSQL Data Lake using MongoDB for aviation records.
    
    Stores:
    - Audio records (metadata and paths)
    - Transcripts (text and timestamps)
    - Flight plans
    - ATC logs
    - Risk assessments
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.uri = self.config.get("mongo_uri", "mongodb://localhost:27017/")
        self.db_name = self.config.get("mongo_db_name", "aviation_ai")
        
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[self.db_name]
            self._setup_indexes()
        except Exception as e:
            print(f"MongoDB Connection Error: {e}. Falling back to mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False

    def _setup_indexes(self):
        """Initialize indexes for fast retrieval."""
        # Records collection: flight_code and timestamp
        self.db.records.create_index([("flight_code", 1), ("timestamp", -1)])
        self.db.records.create_index([("fir", 1)])
        self.db.records.create_index([("origin", 1), ("destination", 1)])
        
        # Transcripts collection: text search
        self.db.transcripts.create_index([("text", "text")])
        self.db.transcripts.create_index([("flight_code", 1)])

    def insert_record(self, collection: str, record: Dict[str, Any]):
        """Insert a record into the specified collection."""
        if self.mock_mode:
            return {"success": True, "id": "mock_id"}
        
        try:
            result = self.db[collection].insert_one(record)
            return {"success": True, "id": str(result.inserted_id)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_records(self, collection: str, query: Dict[str, Any], 
                     limit: int = 20, sort: List = [("timestamp", -1)]) -> List[Dict]:
        """Find records matching the query."""
        if self.mock_mode:
            return self._get_mock_records(collection, query)
            
        try:
            cursor = self.db[collection].find(query).sort(sort).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Query Error: {e}")
            return []

    def _get_mock_records(self, collection: str, query: Dict) -> List[Dict]:
        """Return mock records when MongoDB is unavailable."""
        # Simplified mock data generation based on query
        flight_code = query.get("flight_code", "DLH456")
        return [
            {
                "flight_code": flight_code,
                "timestamp": datetime.utcnow().isoformat(),
                "data": f"Mock {collection} data for {flight_code}",
                "fir": "EDGG"
            }
        ]

    def update_record(self, collection: str, query: Dict, update: Dict):
        """Update a record in the collection."""
        if self.mock_mode: return True
        try:
            self.db[collection].update_one(query, {"$set": update})
            return True
        except Exception:
            return False
