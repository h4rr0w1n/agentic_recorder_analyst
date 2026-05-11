"""
Orchestrator Agent for coordinating multi-agent workflows.

Handles agent coordination, task dispatching, response aggregation,
and human-in-the-loop escalation.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from .base_agent import BaseAgent, AgentMessage
from .retriever_agent import RetrieverAgent
from .analyzer_agent import AnalyzerAgent
from .predictor_agent import PredictorAgent
from .advisor_agent import AdvisorAgent
from .guardian_agent import GuardianAgent


class OrchestratorAgent(BaseAgent):
    """
    Central orchestrator for the aviation AI multi-agent system.
    
    Capabilities:
    - Agent coordination and task dispatching
    - Response aggregation from multiple agents
    - Human-in-the-loop escalation management
    - Workflow state tracking
    - Error handling and recovery
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.agents = {}
        self.workflow_history = []
        
    def initialize(self) -> bool:
        """Initialize all subordinate agents."""
        try:
            self.log("INFO", "Initializing Orchestrator Agent and subordinate agents")
            
            # Initialize configuration
            self.human_in_loop_threshold = self.config.get("human_in_loop_threshold", 0.7)
            self.escalation_enabled = self.config.get("escalation_enabled", True)
            
            # Initialize all agents
            agent_configs = self.config.get("agents", {})
            
            self.agents["retriever"] = RetrieverAgent(
                agent_id="Retriever_001",
                config=agent_configs.get("retriever", {})
            )
            self.agents["analyzer"] = AnalyzerAgent(
                agent_id="Analyzer_001", 
                config=agent_configs.get("analyzer", {})
            )
            self.agents["predictor"] = PredictorAgent(
                agent_id="Predictor_001",
                config=agent_configs.get("predictor", {})
            )
            self.agents["advisor"] = AdvisorAgent(
                agent_id="Advisor_001",
                config=agent_configs.get("advisor", {})
            )
            self.agents["guardian"] = GuardianAgent(
                agent_id="Guardian_001",
                config=agent_configs.get("guardian", {})
            )
            
            # Initialize each agent
            initialization_results = {}
            for name, agent in self.agents.items():
                success = agent.initialize()
                initialization_results[name] = success
                if not success:
                    self.log("ERROR", f"Failed to initialize {name} agent")
            
            # Check if all agents initialized successfully
            all_success = all(initialization_results.values())
            
            if all_success:
                self._initialized = True
                self.update_state("idle", confidence=1.0)
                self.log("INFO", "All agents initialized successfully")
            else:
                self.update_state("error", error="Some agents failed initialization")
            
            return all_success
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Orchestrator: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming orchestration requests."""
        if not self._initialized:
            return AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"error": "Orchestrator not initialized"},
                priority="high"
            )
        
        try:
            self.update_state("processing", message.content.get("task_type"))
            
            task_type = message.content.get("task_type", "analyze_flight")
            
            if task_type == "analyze_flight":
                results = self.execute_full_workflow(
                    query=message.content.get("query", {}),
                    flight_code=message.content.get("flight_code"),
                    time_window=message.content.get("time_window"),
                    fir=message.content.get("fir"),
                    origin=message.content.get("origin"),
                    destination=message.content.get("destination")
                )
            elif task_type == "risk_assessment":
                results = self.execute_risk_assessment_workflow(
                    flight_code=message.content.get("flight_code"),
                    context=message.content.get("context", {})
                )
            elif task_type == "real_time_monitoring":
                results = self.execute_realtime_monitoring(
                    stream_data=message.content.get("stream_data", [])
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results},
                priority=message.priority,
                metadata={"orchestration_time": datetime.utcnow().isoformat()}
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
        """Execute an orchestration task."""
        required_fields = ["task_type"]
        if not self.validate_input(task, required_fields):
            return {"success": False, "error": "Missing required fields"}
        
        message = AgentMessage(
            sender="user",
            recipient=self.agent_id,
            message_type="request",
            content=task
        )
        
        response = self.process_message(message)
        return response.content
    
    def execute_full_workflow(self, query: Dict, flight_code: Optional[str] = None,
                             time_window: Optional[Dict] = None, 
                             fir: Optional[str] = None,
                             origin: Optional[str] = None,
                             destination: Optional[str] = None,
                             context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute the complete multi-agent analysis workflow.
        
        Workflow:
        1. Retriever: Fetch relevant data
        2. Analyzer: Analyze transcripts and extract factors
        3. Predictor: Generate risk predictions
        4. Advisor: Create recommendations
        5. Guardian: Validate compliance
        6. Aggregate and return results
        
        Args:
            query: User query or analysis request.
            flight_code: Flight code to analyze.
            time_window: Time range for analysis.
            fir: Flight Information Region.
            
        Returns:
            Complete analysis results with recommendations.
        """
        self.log("INFO", f"Executing full workflow for flight {flight_code}")
        
        workflow_start = datetime.utcnow()
        session_data = {
            "start_time": workflow_start.isoformat(),
            "flight_code": flight_code,
            "fir": fir,
            "time_window": time_window,
            "agent_outputs": {},
            "workflow_steps": []
        }
        
        try:
            # Step 1: Retrieve data
            self.log("INFO", "Step 1: Retrieving data")
            retrieval_result = self.agents["retriever"].execute_task({
                "task_type": "retrieve_by_flight",
                "flight_code": flight_code,
                "time_window": time_window,
                "fir": fir,
                "origin": origin,
                "destination": destination
            })
            session_data["agent_outputs"]["retriever"] = retrieval_result
            session_data["workflow_steps"].append({"step": 1, "agent": "retriever", "status": "complete"})
            
            # Step 2: Analyze retrieved data
            self.log("INFO", "Step 2: Analyzing data")
            transcripts = self._extract_transcripts(retrieval_result)
            analysis_result = self.agents["analyzer"].execute_task({
                "task_type": "analyze_transcript",
                "transcript": transcripts,
                "metadata": {"flight_code": flight_code, "fir": fir}
            })
            session_data["agent_outputs"]["analyzer"] = analysis_result
            session_data["workflow_steps"].append({"step": 2, "agent": "analyzer", "status": "complete"})
            
            # Step 3: Predict risk
            self.log("INFO", "Step 3: Predicting risk")
            features = self._extract_features(analysis_result, retrieval_result)
            prediction_result = self.agents["predictor"].execute_task({
                "task_type": "predict_risk",
                "features": features,
                "context": {"flight_code": flight_code, "fir": fir}
            })
            session_data["agent_outputs"]["predictor"] = prediction_result
            session_data["workflow_steps"].append({"step": 3, "agent": "predictor", "status": "complete"})
            
            # Step 4: Generate advisory
            self.log("INFO", "Step 4: Generating advisory")
            advisory_result = self.agents["advisor"].execute_task({
                "task_type": "generate_advisory",
                "analysis": analysis_result.get("results", {}),
                "prediction": prediction_result.get("results", {}),
                "context": {"flight_code": flight_code, "fir": fir}
            })
            session_data["agent_outputs"]["advisor"] = advisory_result
            session_data["workflow_steps"].append({"step": 4, "agent": "advisor", "status": "complete"})
            
            # Step 5: Validate with Guardian
            self.log("INFO", "Step 5: Validating compliance")
            validation_result = self.agents["guardian"].execute_task({
                "task_type": "validate_advisory",
                "advisory": advisory_result.get("results", {}),
                "context": {"flight_code": flight_code, "fir": fir}
            })
            session_data["agent_outputs"]["guardian"] = validation_result
            session_data["workflow_steps"].append({"step": 5, "agent": "guardian", "status": "complete"})
            
            # Check if human review is needed
            requires_review = validation_result.get("results", {}).get("requires_review", False)
            if requires_review and self.escalation_enabled:
                self.log("WARNING", "Escalating for human review")
                escalation = self.agents["guardian"].execute_task({
                    "task_type": "escalate_for_review",
                    "item": advisory_result.get("results", {}),
                    "reason": "Low confidence or critical action requiring review"
                })
                session_data["escalation"] = escalation
            
            # Aggregate final output
            final_output = self._aggregate_results(
                retrieval=retrieval_result,
                analysis=analysis_result,
                prediction=prediction_result,
                advisory=advisory_result,
                validation=validation_result
            )
            
            session_data["final_output"] = final_output
            session_data["end_time"] = datetime.utcnow().isoformat()
            
            # Generate audit trail
            audit_trail = self.agents["guardian"].execute_task({
                "task_type": "generate_audit_trail",
                "session_data": session_data
            })
            
            self.workflow_history.append(session_data)
            
            return {
                "success": True,
                "output": final_output,
                "audit_trail": audit_trail,
                "requires_human_review": requires_review,
                "workflow_duration_seconds": (datetime.utcnow() - workflow_start).total_seconds()
            }
            
        except Exception as e:
            self.log("ERROR", f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": session_data
            }
    
    def execute_risk_assessment_workflow(self, flight_code: str,
                                        context: Dict) -> Dict[str, Any]:
        """Execute focused risk assessment workflow."""
        self.log("INFO", f"Executing risk assessment for {flight_code}")
        
        # Simplified workflow focusing on risk prediction
        retrieval = self.agents["retriever"].execute_task({
            "task_type": "retrieve_by_flight",
            "flight_code": flight_code
        })
        
        features = self._extract_features({}, retrieval)
        prediction = self.agents["predictor"].execute_task({
            "task_type": "predict_risk",
            "features": features,
            "context": context
        })
        
        return {
            "flight_code": flight_code,
            "risk_assessment": prediction.get("results", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def execute_realtime_monitoring(self, stream_data: List[Dict]) -> Dict[str, Any]:
        """Execute real-time monitoring workflow for streaming data."""
        self.log("INFO", f"Processing {len(stream_data)} stream data points")
        
        alerts = []
        
        for data_point in stream_data:
            # Quick anomaly detection
            anomaly_result = self.agents["predictor"].execute_task({
                "task_type": "detect_anomaly",
                "time_series": [data_point]
            })
            
            if anomaly_result.get("results", {}).get("anomaly_count", 0) > 0:
                alerts.append({
                    "data_point": data_point,
                    "anomaly_details": anomaly_result["results"],
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return {
            "processed_count": len(stream_data),
            "alerts_generated": len(alerts),
            "alerts": alerts
        }
    
    def _extract_transcripts(self, retrieval_result: Dict) -> str:
        """Extract transcript text from retrieval results."""
        transcripts = retrieval_result.get("transcripts", [])
        if not transcripts:
            return ""
        
        # Concatenate all transcript texts into a single narrative
        texts = [t.get("text", "") for t in transcripts if isinstance(t, dict)]
        return "\n".join(texts)
    
    def _extract_features(self, analysis_result: Dict, retrieval_result: Dict) -> Dict:
        """Extract features for prediction model from analysis and retrieval results."""
        # Extract actual features instead of using mocks
        
        # 1. Phraseology Compliance (from analysis)
        compliance = analysis_result.get("results", {}).get("phraseology_compliance", {})
        violations = len(compliance.get("violations", []))
        warnings = len(compliance.get("warnings", []))
        compliance_score = 1.0 - (violations * 0.1 + warnings * 0.05) if compliance else 0.85
        
        # 2. TOKAI factors (from analysis)
        tokai = analysis_result.get("results", {}).get("tokai_factors", {})
        negative_factors = sum(f["negative"] for f in tokai.values()) if tokai else 0
        
        # 3. Traffic/Contextual data (from retrieval)
        audio_records = retrieval_result.get("audio_records", [])
        traffic_density = len(audio_records) / 100.0 # Simple heuristic
        
        return {
            "traffic_density": min(traffic_density, 1.0),
            "weather_severity": 0.3, # Would come from METAR analysis
            "phraseology_compliance": max(compliance_score, 0.0),
            "negative_tokai_count": negative_factors,
            "record_count": len(audio_records)
        }
    
    def _aggregate_results(self, retrieval: Dict, analysis: Dict, 
                          prediction: Dict, advisory: Dict,
                          validation: Dict) -> Dict[str, Any]:
        """Aggregate results from all agents into final output."""
        return {
            "summary": {
                "flight_code": prediction.get("results", {}).get("context", {}).get("flight_code"),
                "risk_level": prediction.get("results", {}).get("risk_level", "UNKNOWN"),
                "risk_score": prediction.get("results", {}).get("risk_score", 0),
                "priority": advisory.get("results", {}).get("priority", "routine")
            },
            "detailed_results": {
                "retrieval": retrieval,
                "analysis": analysis,
                "prediction": prediction,
                "advisory": advisory,
                "validation": validation
            },
            "recommendations": advisory.get("results", {}).get("recommendations", []),
            "compliance_status": validation.get("results", {}).get("approved", True),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "agent_id": agent.agent_id,
                "state": agent.state.status,
                "confidence": agent.state.confidence_score,
                "current_task": agent.state.current_task
            }
        return status
    
    def shutdown(self) -> None:
        """Shutdown all agents gracefully."""
        self.log("INFO", "Shutting down Orchestrator and all agents")
        
        for name, agent in self.agents.items():
            agent.shutdown()
        
        super().shutdown()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Orchestrator-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "workflow_types": [
                "full_analysis", "risk_assessment", "realtime_monitoring"
            ],
            "managed_agents": list(self.agents.keys()),
            "human_in_loop_enabled": self.escalation_enabled,
            "human_in_loop_threshold": self.human_in_loop_threshold,
            "audit_trail_generation": True
        })
        return base_caps
    
    def analyze_flight(
        self,
        flight_code: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        fir: Optional[str] = None,
        date: Optional[datetime] = None,
        time_window: Optional[str] = None,
        include_weather: bool = True,
        include_notams: bool = True,
        include_atc_transcripts: bool = True,
        confidence_threshold: float = 0.75
    ) -> Dict[str, Any]:
        """
        Execute complete flight analysis workflow.
        
        Args:
            flight_code: Flight identifier (e.g., DLH456)
            origin: Origin airport ICAO code
            destination: Destination airport ICAO code
            fir: Flight Information Region
            date: Flight date
            time_window: Analysis time window
            include_weather: Include METAR/TAF data
            include_notams: Include NOTAM information
            include_atc_transcripts: Include ATC communications
            confidence_threshold: Minimum confidence for recommendations
            
        Returns:
            Complete analysis results dictionary
        """
        # Build query context
        query = {
            "flight_code": flight_code,
            "origin": origin,
            "destination": destination,
            "fir": fir,
            "date": date.isoformat() if date else datetime.now().isoformat(),
            "time_window": time_window or "Last 6 hours",
            "data_sources": []
        }
        
        if include_weather:
            query["data_sources"].append("METAR_TAF")
        if include_notams:
            query["data_sources"].append("NOTAM")
        if include_atc_transcripts:
            query["data_sources"].append("ATC_TRANSCRIPT")
        
        # Execute full workflow
        results = self.execute_full_workflow(
            query=query,
            flight_code=flight_code,
            time_window=time_window,
            fir=fir,
            origin=origin,
            destination=destination,
            context={"confidence_threshold": confidence_threshold}
        )
        
        # Transform to UI-friendly format
        risk_level = "LOW"
        if results.get("risk_score", 0) > 0.65:
            risk_level = "HIGH"
        elif results.get("risk_score", 0) > 0.45:
            risk_level = "MEDIUM"
        
        # Extract anomalies from predictor results
        anomalies = []
        if "predictor" in results and "anomalies" in results["predictor"]:
            for anomaly in results["predictor"]["anomalies"]:
                anomalies.append({
                    "type": anomaly.get("type", "Unknown"),
                    "severity": anomaly.get("severity", "LOW"),
                    "timestamp": anomaly.get("timestamp", "N/A")
                })
        
        # Extract recommendations from advisor results
        recommendations = []
        if "advisor" in results and "recommendations" in results["advisor"]:
            for rec in results["advisor"]["recommendations"]:
                recommendations.append({
                    "priority": rec.get("priority", "MEDIUM"),
                    "type": rec.get("type", "Information"),
                    "message": rec.get("description", "No description"),
                    "confidence": rec.get("confidence", 0.0)
                })
        
        # Check if human review is required
        human_review = (
            results.get("human_review_required", False) or
            risk_level == "HIGH" or
            any(a.get("severity") == "HIGH" for a in anomalies)
        )
        
        return {
            "flight_code": flight_code,
            "route": f"{origin or 'Origin TBD'} → {destination or 'Destination TBD'}",
            "fir": fir or "EDGG",
            "date": date,
            "risk_score": round(results.get("risk_score", 0.5), 2),
            "risk_level": risk_level,
            "confidence": round(results.get("confidence", 0.8), 2),
            "tokai_factors": results.get("tokai_factors", {}),
            "phraseology_compliance": results.get("phraseology_compliance", 0.95),
            "anomalies_detected": anomalies,
            "recommendations": recommendations,
            "warnings": results.get("warnings", []),
            "human_review_required": human_review
        }
