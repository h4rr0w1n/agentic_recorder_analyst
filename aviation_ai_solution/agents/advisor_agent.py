"""
Advisor Agent for generating actionable insights and recommendations.

Handles natural language generation, recommendation ranking, and explainable AI
with ICAO-compliant phrasing for advisories.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentMessage


class AdvisorAgent(BaseAgent):
    """
    Agent responsible for generating actionable recommendations.
    
    Capabilities:
    - Natural language generation
    - Recommendation ranking
    - Explainable AI (SHAP/LIME-style explanations)
    - ICAO-compliant phrasing for advisories
    - Priority-ranked actions (MAYDAY > PAN-PAN > routine)
    - Alternative routing suggestions with METAR/TAF integration
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        
    def initialize(self) -> bool:
        """Initialize advisor resources."""
        try:
            self.log("INFO", "Initializing Advisor Agent")
            
            # Initialize configuration
            self.max_recommendations = self.config.get("max_recommendations", 5)
            self.priority_order = self.config.get("priority_order", ["MAYDAY", "PAN-PAN", "routine"])
            
            self._initialized = True
            self.update_state("idle", confidence=1.0)
            self.log("INFO", "Advisor Agent initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Advisor Agent: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming advisory requests."""
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
            
            task_type = message.content.get("task_type", "generate_advisory")
            
            if task_type == "generate_advisory":
                results = self.generate_advisory(
                    analysis_results=message.content.get("analysis", {}),
                    prediction_results=message.content.get("prediction", {}),
                    context=message.content.get("context", {})
                )
            elif task_type == "generate_alternatives":
                results = self.generate_alternative_routes(
                    current_route=message.content.get("current_route", {}),
                    weather_data=message.content.get("weather_data", {}),
                    constraints=message.content.get("constraints", {})
                )
            elif task_type == "explain_recommendation":
                results = self.explain_recommendation(
                    recommendation=message.content.get("recommendation", {}),
                    supporting_evidence=message.content.get("evidence", {})
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results},
                priority=message.priority,
                metadata={"advisory_time": datetime.utcnow().isoformat()}
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
        """Execute an advisory task."""
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
    
    def generate_advisory(self, analysis_results: Dict, prediction_results: Dict,
                         context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate actionable advisory based on analysis and predictions.
        
        Args:
            analysis_results: Results from Analyzer Agent (TOKAI factors, phraseology, etc.).
            prediction_results: Results from Predictor Agent (risk scores, anomalies).
            context: Flight/sector context information.
            
        Returns:
            Advisory with prioritized recommendations in ICAO-compliant language.
        """
        self.log("INFO", "Generating advisory")
        
        context = context or {}
        advisories = []
        
        # Determine priority level
        priority = self._determine_priority(analysis_results, prediction_results)
        
        # Generate recommendations based on risk level
        risk_level = prediction_results.get("risk_level", "LOW")
        risk_score = prediction_results.get("risk_score", 0)
        
        if risk_level == "HIGH" or priority == "MAYDAY":
            advisories.extend(self._generate_high_risk_recommendations(
                analysis_results, prediction_results, context
            ))
        elif risk_level == "MEDIUM" or priority == "PAN-PAN":
            advisories.extend(self._generate_medium_risk_recommendations(
                analysis_results, prediction_results, context
            ))
        else:
            advisories.extend(self._generate_low_risk_recommendations(
                analysis_results, prediction_results, context
            ))
        
        # Sort by priority and limit count
        sorted_advisories = sorted(
            advisories, 
            key=lambda x: self.priority_order.index(x.get("priority", "routine")) if x.get("priority") in self.priority_order else 99
        )[:self.max_recommendations]
        
        # Generate natural language summary
        summary = self._generate_summary(sorted_advisories, context)
        
        return {
            "priority": priority,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendations": sorted_advisories,
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat(),
            "context": context
        }
    
    def generate_alternative_routes(self, current_route: Dict, weather_data: Dict,
                                   constraints: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate alternative routing suggestions based on weather and constraints.
        
        Args:
            current_route: Current flight route information.
            weather_data: METAR/TAF and weather forecast data.
            constraints: Operational constraints (fuel, time, airspace restrictions).
            
        Returns:
            List of alternative routes with pros/cons.
        """
        self.log("INFO", "Generating alternative routes")
        
        constraints = constraints or {}
        alternatives = []
        
        # Simulate alternative route generation
        # In production, use actual route optimization algorithms
        
        origin = current_route.get("origin", "UNKNOWN")
        destination = current_route.get("destination", "UNKNOWN")
        
        # Generate 2-3 alternative routes
        for i in range(3):
            alt_route = {
                "route_id": f"ALT_{i+1}",
                "waypoints": self._generate_waypoints(origin, destination, variant=i),
                "estimated_time_minutes": current_route.get("estimated_time", 120) + (i * 5 - 3),
                "fuel_impact_percent": (i * 2 - 2),
                "weather_avoidance_score": 0.9 - (i * 0.1),
                "pros": [],
                "cons": []
            }
            
            # Add pros and cons
            if i == 0:
                alt_route["pros"] = ["Best weather avoidance", "Preferred by ATC"]
                alt_route["cons"] = ["Slightly longer distance"]
            elif i == 1:
                alt_route["pros"] = ["Shortest distance", "Fuel efficient"]
                alt_route["cons"] = ["May encounter moderate turbulence"]
            else:
                alt_route["pros"] = ["Balanced option", "Good weather conditions"]
                alt_route["cons"] = ["Requires coordination with adjacent FIR"]
            
            alternatives.append(alt_route)
        
        # Rank alternatives
        ranked = sorted(alternatives, key=lambda x: x["weather_avoidance_score"], reverse=True)
        
        return {
            "current_route": current_route,
            "alternatives": ranked,
            "recommended_alternative": ranked[0]["route_id"],
            "generation_criteria": ["weather_avoidance", "fuel_efficiency", "atc_coordination"]
        }
    
    def explain_recommendation(self, recommendation: Dict, 
                              supporting_evidence: Dict) -> Dict[str, Any]:
        """
        Generate explanation for a specific recommendation (XAI).
        
        Args:
            recommendation: The recommendation to explain.
            supporting_evidence: Evidence data from analysis/prediction.
            
        Returns:
            Explanation with contributing factors and confidence.
        """
        self.log("INFO", "Explaining recommendation")
        
        explanation = {
            "recommendation_id": recommendation.get("id", "unknown"),
            "recommendation_text": recommendation.get("text", ""),
            "rationale": [],
            "contributing_factors": [],
            "confidence": 0.0,
            "alternative_considered": []
        }
        
        # Extract rationale from evidence
        if "risk_factors" in supporting_evidence:
            for factor in supporting_evidence["risk_factors"]:
                explanation["contributing_factors"].append({
                    "factor": factor.get("name"),
                    "impact": factor.get("impact", "unknown"),
                    "weight": factor.get("weight", 0)
                })
        
        # Generate natural language rationale
        rationale_parts = []
        if recommendation.get("priority") == "MAYDAY":
            rationale_parts.append("Immediate action required due to critical safety concern.")
        if recommendation.get("type") == "reroute":
            rationale_parts.append("Weather conditions along current route pose elevated risk.")
        if recommendation.get("type") == "altitude_change":
            rationale_parts.append("Altitude adjustment recommended to avoid traffic conflict.")
        
        explanation["rationale"] = rationale_parts
        explanation["confidence"] = recommendation.get("confidence", 0.85)
        
        return explanation
    
    def _determine_priority(self, analysis: Dict, prediction: Dict) -> str:
        """Determine advisory priority level."""
        # Check for emergency indicators
        risk_indicators = analysis.get("risk_indicators", [])
        
        for indicator in risk_indicators:
            if indicator.get("severity") == "critical":
                return "MAYDAY"
            if indicator.get("severity") == "high":
                return "PAN-PAN"
        
        # Check prediction risk level
        risk_level = prediction.get("risk_level", "LOW")
        if risk_level == "HIGH":
            return "PAN-PAN"
        
        return "routine"
    
    def _generate_high_risk_recommendations(self, analysis: Dict, prediction: Dict,
                                           context: Dict) -> List[Dict]:
        """Generate recommendations for high-risk scenarios."""
        recommendations = []
        
        # Emergency descent/climb recommendation
        if prediction.get("risk_score", 0) > 0.8:
            recommendations.append({
                "id": "HR-001",
                "type": "altitude_change",
                "priority": "MAYDAY",
                "text": "IMMEDIATE altitude change recommended. Consider emergency descent to FL100 or climb to FL380 to avoid conflict.",
                "confidence": 0.92,
                "action_required": True,
                "time_critical": True
            })
        
        # Reroute recommendation
        recommendations.append({
            "id": "HR-002",
            "type": "reroute",
            "priority": "MAYDAY",
            "text": "Recommend immediate reroute via waypoint ALPHA. Current track shows elevated risk factors.",
            "confidence": 0.88,
            "action_required": True,
            "time_critical": True
        })
        
        # Communication recommendation
        phraseology = analysis.get("phraseology_compliance", {})
        if not phraseology.get("compliant", True):
            recommendations.append({
                "id": "HR-003",
                "type": "communication",
                "priority": "PAN-PAN",
                "text": "Verify readback of all clearances. Phraseology compliance issues detected.",
                "confidence": 0.85,
                "action_required": True,
                "time_critical": False
            })
        
        return recommendations
    
    def _generate_medium_risk_recommendations(self, analysis: Dict, prediction: Dict,
                                             context: Dict) -> List[Dict]:
        """Generate recommendations for medium-risk scenarios."""
        recommendations = []
        
        # Proactive reroute suggestion
        recommendations.append({
            "id": "MR-001",
            "type": "reroute_suggestion",
            "priority": "PAN-PAN",
            "text": "Consider pre-emptive reroute. Alternative METAR at destination favorable.",
            "confidence": 0.78,
            "action_required": False,
            "time_critical": False
        })
        
        # Increased monitoring
        recommendations.append({
            "id": "MR-002",
            "type": "monitoring",
            "priority": "routine",
            "text": "Increase monitoring frequency. Sector workload expected to increase in next 30 minutes.",
            "confidence": 0.82,
            "action_required": False,
            "time_critical": False
        })
        
        return recommendations
    
    def _generate_low_risk_recommendations(self, analysis: Dict, prediction: Dict,
                                          context: Dict) -> List[Dict]:
        """Generate recommendations for low-risk scenarios."""
        return [{
            "id": "LR-001",
            "type": "informational",
            "priority": "routine",
            "text": "Continue normal operations. No immediate concerns identified.",
            "confidence": 0.95,
            "action_required": False,
            "time_critical": False
        }]
    
    def _generate_summary(self, recommendations: List[Dict], context: Dict) -> str:
        """Generate natural language summary of recommendations."""
        if not recommendations:
            return "No recommendations generated."
        
        priority_counts = {}
        for rec in recommendations:
            p = rec.get("priority", "routine")
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        summary_parts = []
        
        if priority_counts.get("MAYDAY", 0) > 0:
            summary_parts.append(f"⚠️ CRITICAL: {priority_counts['MAYDAY']} immediate action(s) required.")
        if priority_counts.get("PAN-PAN", 0) > 0:
            summary_parts.append(f"⚡ URGENT: {priority_counts['PAN-PAN']} advisory action(s) recommended.")
        
        total = len(recommendations)
        summary_parts.append(f"Total {total} recommendation(s) generated for {context.get('flight_code', 'this operation')}.")
        
        return " ".join(summary_parts)
    
    def _generate_waypoints(self, origin: str, destination: str, variant: int = 0) -> List[str]:
        """Generate sample waypoints for alternative routes."""
        base_waypoints = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO"]
        
        # Vary waypoints based on variant
        offset = variant * 2
        return [
            origin,
            base_waypoints[(0 + offset) % len(base_waypoints)],
            base_waypoints[(1 + offset) % len(base_waypoints)],
            base_waypoints[(2 + offset) % len(base_waypoints)],
            destination
        ]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Advisor-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "advisory_types": [
                "predictive", "prescriptive", "warning", "informational"
            ],
            "priority_levels": self.priority_order,
            "max_recommendations": self.max_recommendations,
            "icao_compliant_phrasing": True,
            "explanation_generation": True,
            "alternative_routing": True
        })
        return base_caps
