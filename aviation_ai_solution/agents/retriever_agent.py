"""
Retriever Agent for aviation data retrieval and semantic search.

Handles hybrid search (BM25 + vector embeddings), temporal/spatial indexing,
and graph-based entity traversal across aviation data sources.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import os
import json

from .base_agent import BaseAgent, AgentMessage


class RetrieverAgent(BaseAgent):
    """
    Agent responsible for retrieving aviation records from various sources.
    
    Capabilities:
    - Hybrid search (BM25 + vector embeddings)
    - Temporal/spatial indexing
    - Graph-based entity traversal
    - FIR/sector-aware indexing
    - ICAO document type recognition (NOTAM format parser)
    - Crew/flight cross-referencing via IATA SSIM
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.indexes = {}
        self.vector_store = None
        self.graph_db = None
        self.bm25_index = None
        
    def initialize(self) -> bool:
        """Initialize retrieval indexes and connections."""
        try:
            self.log("INFO", "Initializing Retriever Agent")
            
            # Initialize configuration
            self.hybrid_alpha = self.config.get("hybrid_search_alpha", 0.5)
            self.top_k = self.config.get("top_k_results", 20)
            
            # In production, initialize actual vector store and graph DB
            # self.vector_store = initialize_vector_store(self.config)
            # self.graph_db = initialize_graph_db(self.config)
            # self.bm25_index = initialize_bm25_index()
            
            self._initialized = True
            self.update_state("idle", confidence=1.0)
            self.log("INFO", "Retriever Agent initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Retriever Agent: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming retrieval requests."""
        if not self._initialized:
            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"error": "Agent not initialized"},
                priority="high"
            )
        
        try:
            self.update_state("processing", message.content.get("task_type"))
            
            task_type = message.content.get("task_type", "search")
            
            if task_type == "search":
                results = self.search(
                    query=message.content.get("query", ""),
                    filters=message.content.get("filters", {}),
                    top_k=message.content.get("top_k", self.top_k)
                )
            elif task_type == "retrieve_by_flight":
                results = self.retrieve_by_flight(
                    flight_code=message.content.get("flight_code"),
                    time_window=message.content.get("time_window"),
                    fir=message.content.get("fir")
                )
            elif task_type == "retrieve_by_entity":
                results = self.retrieve_by_entity(
                    entity_id=message.content.get("entity_id"),
                    entity_type=message.content.get("entity_type"),
                    relationship_depth=message.content.get("depth", 2)
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results, "count": len(results) if isinstance(results, list) else 0},
                priority=message.priority,
                metadata={"query_time": datetime.utcnow().isoformat()}
            )
            
            self.update_state("idle", confidence=0.95)
            return response
            
        except Exception as e:
            self.log("ERROR", f"Error processing message: {str(e)}")
            self.update_state("error", error=str(e))
            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"error": str(e)},
                priority="critical"
            )
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a retrieval task."""
        required_fields = ["task_type"]
        if not self.validate_input(task, required_fields):
            return {"success": False, "error": "Missing required fields"}
        
        message = AgentMessage(
            sender="orchestrator",
            recipient=self.agent_id,
            message_type="request",
            content=task
        )
        
        response = self.process_message(message)
        return response.content
    
    def search(self, query: str, filters: Optional[Dict] = None, 
               top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Perform hybrid search across aviation data sources.
        
        Args:
            query: Search query string.
            filters: Optional filters (time range, FIR, flight code, etc.).
            top_k: Number of results to return.
            
        Returns:
            List of matching records with relevance scores.
        """
        self.log("INFO", f"Executing hybrid search for query: {query[:50]}...")
        
        filters = filters or {}
        results = []
        
        # Simulated search results - in production, this would query actual indexes
        # BM25 keyword search
        bm25_results = self._bm25_search(query, filters, top_k)
        
        # Vector semantic search
        vector_results = self._vector_search(query, filters, top_k)
        
        # Combine results with hybrid scoring
        combined = self._combine_hybrid_results(bm25_results, vector_results, self.hybrid_alpha)
        
        # Apply post-filtering
        filtered_results = self._apply_filters(combined, filters)
        
        return filtered_results[:top_k]
    
    def retrieve_by_flight(self, flight_code: str, time_window: Optional[Dict] = None,
                          fir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all records associated with a specific flight.
        
        Args:
            flight_code: IATA/ICAO flight code (e.g., "DLH456").
            time_window: Time range dictionary with 'start' and 'end'.
            fir: Flight Information Region code.
            
        Returns:
            List of flight-related records (ATC logs, flight plans, METARs, etc.).
        """
        self.log("INFO", f"Retrieving records for flight {flight_code}")
        
        # Query graph database for flight entity and related records
        # In production: traverse graph from flight node
        results = []
        
        # Simulate retrieving different record types
        record_types = ["flight_plan", "atc_transcript", "metar", "notam", "adsb_track"]
        
        for record_type in record_types:
            results.append({
                "type": record_type,
                "flight_code": flight_code,
                "fir": fir,
                "time_window": time_window,
                "data": f"Sample {record_type} data for {flight_code}"
            })
        
        return results
    
    def retrieve_by_entity(self, entity_id: str, entity_type: str,
                          relationship_depth: int = 2) -> Dict[str, Any]:
        """
        Retrieve records by entity ID using graph traversal.
        
        Args:
            entity_id: Entity identifier (crew ID, flight code, ATC sector, etc.).
            entity_type: Type of entity (crew, flight, atc_sector, fir).
            relationship_depth: How many hops to traverse in the graph.
            
        Returns:
            Dictionary with entity data and related records.
        """
        self.log("INFO", f"Retrieving by entity: {entity_type}:{entity_id}")
        
        # Graph traversal to find related entities
        # In production: use Neo4j or similar graph database
        result = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "traversal_depth": relationship_depth,
            "related_entities": [],
            "records": []
        }
        
        return result
    
    def _bm25_search(self, query: str, filters: Dict, top_k: int) -> List[Dict]:
        """Perform BM25 keyword search."""
        # Placeholder for actual BM25 implementation
        return []
    
    def _vector_search(self, query: str, filters: Dict, top_k: int) -> List[Dict]:
        """Perform vector semantic search."""
        # Placeholder for actual vector search implementation
        return []
    
    def _combine_hybrid_results(self, bm25_results: List, vector_results: List,
                                alpha: float) -> List[Dict]:
        """Combine BM25 and vector search results with weighted scoring."""
        # Reciprocal Rank Fusion or simple weighted combination
        combined = {}
        
        for i, result in enumerate(bm25_results):
            result_id = result.get("id", str(i))
            score = (1 - alpha) * (1.0 / (i + 1))
            combined[result_id] = {"score": score, "data": result}
        
        for i, result in enumerate(vector_results):
            result_id = result.get("id", str(i))
            score = alpha * (1.0 / (i + 1))
            if result_id in combined:
                combined[result_id]["score"] += score
            else:
                combined[result_id] = {"score": score, "data": result}
        
        # Sort by combined score
        sorted_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        return [item["data"] for item in sorted_results]
    
    def _apply_filters(self, results: List[Dict], filters: Dict) -> List[Dict]:
        """Apply post-search filters to results."""
        if not filters:
            return results
        
        filtered = []
        for result in results:
            match = True
            
            # Time range filter
            if "time_range" in filters:
                result_time = result.get("timestamp")
                if result_time:
                    start = filters["time_range"].get("start")
                    end = filters["time_range"].get("end")
                    if start and result_time < start:
                        match = False
                    if end and result_time > end:
                        match = False
            
            # FIR filter
            if "fir" in filters and result.get("fir") != filters["fir"]:
                match = False
            
            # Flight code filter
            if "flight_code" in filters and result.get("flight_code") != filters["flight_code"]:
                match = False
            
            if match:
                filtered.append(result)
        
        return filtered
    
    def parse_notam(self, notam_text: str) -> Dict[str, Any]:
        """Parse NOTAM text into structured format."""
        # ICAO NOTAM format parser
        # Example: A1234/24 NOTAMN ...
        parsed = {
            "raw": notam_text,
            "notam_id": None,
            "year": None,
            "type": None,
            "fir": None,
            "keywords": [],
            "valid_from": None,
            "valid_to": None
        }
        
        # Simple parsing logic - in production, use proper NOTAM grammar
        parts = notam_text.split()
        if len(parts) > 0:
            parsed["notam_id"] = parts[0] if "/" in parts[0] else None
        
        return parsed
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Retriever-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "search_types": ["keyword", "semantic", "hybrid", "graph_traversal"],
            "supported_filters": ["time_range", "fir", "flight_code", "entity_type"],
            "data_sources": ["flight_plans", "atc_transcripts", "metars", "notams", "adsb_tracks"],
            "hybrid_search_enabled": True,
            "graph_traversal_enabled": True
        })
        return base_caps
