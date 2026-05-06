"""
Predictor Agent for risk prediction and anomaly detection.

Handles time-series anomaly detection, risk classification, and counterfactual simulation
using ensemble models (Random Forest, LSTM, Graph Neural Networks).
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import random

from .base_agent import BaseAgent, AgentMessage


class PredictorAgent(BaseAgent):
    """
    Agent responsible for predictive risk modeling and anomaly detection.
    
    Capabilities:
    - Time-series anomaly detection
    - Classification (risk levels: Low/Medium/High/Critical)
    - Counterfactual simulation
    - Loss-of-Separation (LoS) precursor modeling
    - Weather-traffic interaction forecasting
    - Crew fatigue/ATC workload correlation analysis
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.models = {}
        
    def initialize(self) -> bool:
        """Initialize prediction models."""
        try:
            self.log("INFO", "Initializing Predictor Agent")
            
            # Initialize configuration
            self.risk_threshold_low = self.config.get("risk_threshold_low", 0.3)
            self.risk_threshold_high = self.config.get("risk_threshold_high", 0.7)
            self.ensemble_weights = self.config.get("model_ensemble_weights", {
                "random_forest": 0.4,
                "lstm": 0.35,
                "gnn": 0.25
            })
            
            # In production, load actual trained models
            # self.models["random_forest"] = load_rf_model()
            # self.models["lstm"] = load_lstm_model()
            # self.models["gnn"] = load_gnn_model()
            
            self._initialized = True
            self.update_state("idle", confidence=1.0)
            self.log("INFO", "Predictor Agent initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Predictor Agent: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming prediction requests."""
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
            
            task_type = message.content.get("task_type", "predict_risk")
            
            if task_type == "predict_risk":
                results = self.predict_risk(
                    features=message.content.get("features", {}),
                    context=message.content.get("context", {})
                )
            elif task_type == "detect_anomaly":
                results = self.detect_anomaly(
                    time_series=message.content.get("time_series", []),
                    window_size=message.content.get("window_size", 10)
                )
            elif task_type == "simulate_counterfactual":
                results = self.simulate_counterfactual(
                    scenario=message.content.get("scenario", {}),
                    modifications=message.content.get("modifications", {})
                )
            elif task_type == "forecast_weather_traffic":
                results = self.forecast_weather_traffic_interaction(
                    weather_data=message.content.get("weather_data", {}),
                    traffic_data=message.content.get("traffic_data", {}),
                    forecast_horizon=message.content.get("horizon_hours", 6)
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results},
                priority=message.priority,
                metadata={"prediction_time": datetime.utcnow().isoformat()}
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
        """Execute a prediction task."""
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
    
    def predict_risk(self, features: Dict[str, Any], 
                     context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Predict risk level for a given flight/sector scenario.
        
        Args:
            features: Feature dictionary including:
                - Structured: Flight level, airspace class, traffic density, weather METAR codes
                - Temporal: Time-of-day, sector handoff frequency, crew duty time
                - Text-derived: TOKAI factor scores, phraseology compliance rate
                - Voice-derived: Readback error rate, radio transmission quality
            context: Additional context (flight code, FIR, timestamp).
            
        Returns:
            Risk prediction with score, level, confidence intervals, and contributing factors.
        """
        self.log("INFO", "Predicting risk level")
        
        context = context or {}
        
        # Simulate ensemble model predictions
        # In production, run actual model inference
        
        # Random Forest prediction (feature importance + interpretable rules)
        rf_score = self._random_forest_predict(features)
        
        # LSTM prediction (temporal anomaly detection)
        lstm_score = self._lstm_predict(features)
        
        # GNN prediction (risk propagation across FIR/sector graph)
        gnn_score = self._gnn_predict(features, context)
        
        # Ensemble combination
        final_score = (
            self.ensemble_weights["random_forest"] * rf_score +
            self.ensemble_weights["lstm"] * lstm_score +
            self.ensemble_weights["gnn"] * gnn_score
        )
        
        # Determine risk level
        if final_score >= self.risk_threshold_high:
            risk_level = "HIGH"
        elif final_score >= self.risk_threshold_low:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Identify top contributing factors
        contributing_factors = self._identify_contributing_factors(features, final_score)
        
        # Calculate confidence intervals (simplified)
        confidence_interval = {
            "lower": max(0, final_score - 0.1),
            "upper": min(1, final_score + 0.1),
            "confidence": 0.85
        }
        
        return {
            "risk_score": round(final_score, 4),
            "risk_level": risk_level,
            "confidence_interval": confidence_interval,
            "contributing_factors": contributing_factors,
            "model_outputs": {
                "random_forest": round(rf_score, 4),
                "lstm": round(lstm_score, 4),
                "gnn": round(gnn_score, 4)
            },
            "thresholds": {
                "low": self.risk_threshold_low,
                "high": self.risk_threshold_high
            },
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_anomaly(self, time_series: List[Dict], 
                       window_size: int = 10) -> Dict[str, Any]:
        """
        Detect anomalies in time-series data.
        
        Args:
            time_series: List of data points with timestamps and values.
            window_size: Window size for anomaly detection.
            
        Returns:
            Anomaly detection results with scores and timestamps.
        """
        self.log("INFO", f"Detecting anomalies with window size {window_size}")
        
        if len(time_series) < window_size:
            return {
                "anomalies": [],
                "anomaly_count": 0,
                "message": "Insufficient data points for anomaly detection"
            }
        
        anomalies = []
        
        # Simplified anomaly detection using statistical methods
        # In production, use LSTM-based or isolation forest approaches
        
        values = [point.get("value", 0) for point in time_series]
        
        for i in range(window_size, len(values)):
            window = values[i-window_size:i]
            current_value = values[i]
            
            mean = sum(window) / len(window)
            std = (sum((x - mean) ** 2 for x in window) / len(window)) ** 0.5
            
            if std > 0:
                z_score = abs(current_value - mean) / std
                
                if z_score > 3.0:  # Threshold for anomaly
                    anomalies.append({
                        "index": i,
                        "timestamp": time_series[i].get("timestamp"),
                        "value": current_value,
                        "z_score": round(z_score, 2),
                        "severity": "high" if z_score > 4.0 else "medium"
                    })
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "total_points": len(time_series),
            "detection_method": "statistical_zscore",
            "window_size": window_size
        }
    
    def simulate_counterfactual(self, scenario: Dict, 
                                modifications: Dict) -> Dict[str, Any]:
        """
        Run counterfactual simulation ("what-if" scenario testing).
        
        Args:
            scenario: Base scenario definition.
            modifications: Changes to apply for counterfactual.
            
        Returns:
            Simulation results comparing base and modified scenarios.
        """
        self.log("INFO", "Running counterfactual simulation")
        
        # Predict risk for base scenario
        base_prediction = self.predict_risk(
            features=scenario.get("features", {}),
            context=scenario.get("context", {})
        )
        
        # Apply modifications to create counterfactual scenario
        counterfactual_features = scenario.get("features", {}).copy()
        counterfactual_features.update(modifications.get("features", {}))
        
        counterfactual_context = scenario.get("context", {}).copy()
        counterfactual_context.update(modifications.get("context", {}))
        
        # Predict risk for counterfactual scenario
        counterfactual_prediction = self.predict_risk(
            features=counterfactual_features,
            context=counterfactual_context
        )
        
        # Calculate impact
        risk_change = counterfactual_prediction["risk_score"] - base_prediction["risk_score"]
        
        return {
            "base_scenario": base_prediction,
            "counterfactual_scenario": counterfactual_prediction,
            "modifications_applied": modifications,
            "risk_change": round(risk_change, 4),
            "risk_improvement": risk_change < 0,
            "recommendation": "Recommended" if risk_change < -0.1 else "Not recommended" if risk_change > 0.1 else "Neutral impact"
        }
    
    def forecast_weather_traffic_interaction(self, weather_data: Dict,
                                            traffic_data: Dict,
                                            forecast_horizon: int = 6) -> Dict[str, Any]:
        """
        Forecast weather-traffic interaction effects.
        
        Args:
            weather_data: Current and forecasted weather data.
            traffic_data: Current traffic density and flow data.
            forecast_horizon: Hours to forecast ahead.
            
        Returns:
            Forecast results with predicted capacity and delay impacts.
        """
        self.log("INFO", f"Forecasting weather-traffic interaction for {forecast_horizon}h")
        
        # Simplified forecasting logic
        # In production, use spatio-temporal models
        
        hourly_forecast = []
        
        for hour in range(1, forecast_horizon + 1):
            # Simulate weather degradation impact
            weather_impact = random.uniform(0.1, 0.5)
            traffic_load = traffic_data.get("current_density", 0.5)
            
            # Interaction effect
            combined_impact = weather_impact * traffic_load * (1 + hour * 0.1)
            
            hourly_forecast.append({
                "hour_ahead": hour,
                "weather_impact": round(weather_impact, 3),
                "predicted_traffic_load": round(min(1.0, traffic_load * (1 + hour * 0.05)), 3),
                "combined_impact": round(combined_impact, 3),
                "predicted_capacity_reduction": round(combined_impact * 0.3, 3),
                "predicted_delay_minutes": round(combined_impact * 15, 1)
            })
        
        return {
            "forecast_horizon_hours": forecast_horizon,
            "hourly_forecast": hourly_forecast,
            "peak_impact_hour": max(hourly_forecast, key=lambda x: x["combined_impact"])["hour_ahead"],
            "average_delay_minutes": round(sum(h["predicted_delay_minutes"] for h in hourly_forecast) / len(hourly_forecast), 1),
            "recommendation": self._generate_weather_traffic_recommendation(hourly_forecast)
        }
    
    def _random_forest_predict(self, features: Dict) -> float:
        """Simulate Random Forest prediction."""
        # Placeholder - in production, use actual RF model
        base_risk = 0.3
        
        # Adjust based on features
        if features.get("traffic_density", 0) > 0.8:
            base_risk += 0.2
        if features.get("weather_severity", 0) > 0.7:
            base_risk += 0.15
        if features.get("phraseology_compliance", 1.0) < 0.8:
            base_risk += 0.1
        
        return min(1.0, base_risk + random.uniform(-0.1, 0.1))
    
    def _lstm_predict(self, features: Dict) -> float:
        """Simulate LSTM temporal anomaly prediction."""
        # Placeholder - in production, use actual LSTM model
        return random.uniform(0.2, 0.5)
    
    def _gnn_predict(self, features: Dict, context: Dict) -> float:
        """Simulate Graph Neural Network prediction for sector risk propagation."""
        # Placeholder - in production, use actual GNN model
        fir = context.get("fir", "")
        
        # Higher risk for busy FIRs (simulated)
        busy_firs = ["EDGG", "EGTT", "LFFF", "KZNY"]
        base = 0.4 if fir in busy_firs else 0.3
        
        return base + random.uniform(-0.1, 0.1)
    
    def _identify_contributing_factors(self, features: Dict, 
                                       risk_score: float) -> List[Dict]:
        """Identify top factors contributing to risk score."""
        factors = []
        
        feature_importance = {
            "traffic_density": features.get("traffic_density", 0),
            "weather_severity": features.get("weather_severity", 0),
            "phraseology_compliance": 1.0 - features.get("phraseology_compliance", 1.0),
            "crew_duty_time": features.get("crew_duty_hours", 0) / 14.0,
            "sector_handoff_frequency": features.get("handoffs_per_hour", 0) / 10.0
        }
        
        # Sort by importance
        sorted_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        for factor_name, value in sorted_factors[:5]:
            if value > 0.1:  # Only include significant factors
                factors.append({
                    "factor": factor_name,
                    "contribution": round(value, 3),
                    "impact": "high" if value > 0.5 else "medium" if value > 0.2 else "low"
                })
        
        return factors
    
    def _generate_weather_traffic_recommendation(self, forecast: List[Dict]) -> str:
        """Generate recommendation based on weather-traffic forecast."""
        peak_impact = max(f["combined_impact"] for f in forecast)
        
        if peak_impact > 0.7:
            return "Consider proactive flow management measures and increased staffing"
        elif peak_impact > 0.4:
            return "Monitor situation closely; prepare contingency plans"
        else:
            return "Normal operations expected; continue standard monitoring"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Predictor-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "prediction_types": [
                "risk_assessment", "anomaly_detection", "counterfactual_simulation",
                "weather_traffic_forecast", "los_prediction"
            ],
            "model_ensemble": list(self.ensemble_weights.keys()),
            "risk_levels": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            "thresholds": {
                "low": self.risk_threshold_low,
                "high": self.risk_threshold_high
            }
        })
        return base_caps
