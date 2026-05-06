"""
Test suite for the Aviation AI Solution.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestBaseAgent:
    """Tests for BaseAgent class."""
    
    def test_agent_initialization(self):
        from aviation_ai_solution.agents.base_agent import BaseAgent
        
        # Can't instantiate abstract base class directly, but can test concrete subclass
        from aviation_ai_solution.agents.retriever_agent import RetrieverAgent
        
        agent = RetrieverAgent(agent_id="test_agent")
        assert agent.agent_id == "test_agent"
        assert agent.state.status == "idle"
    
    def test_agent_message_creation(self):
        from aviation_ai_solution.agents.base_agent import AgentMessage
        
        msg = AgentMessage(
            sender="test",
            recipient="agent",
            message_type="request",
            content={"key": "value"}
        )
        
        assert msg.sender == "test"
        assert msg.recipient == "agent"
        assert msg.content["key"] == "value"


class TestRetrieverAgent:
    """Tests for RetrieverAgent."""
    
    def test_retriever_initialization(self):
        from aviation_ai_solution.agents.retriever_agent import RetrieverAgent
        
        config = {"hybrid_search_alpha": 0.6, "top_k_results": 15}
        agent = RetrieverAgent(config=config)
        
        success = agent.initialize()
        assert success is True
        assert agent.hybrid_alpha == 0.6
        assert agent.top_k == 15
    
    def test_retriever_search(self):
        from aviation_ai_solution.agents.retriever_agent import RetrieverAgent
        
        agent = RetrieverAgent()
        agent.initialize()
        
        results = agent.search(query="test query", top_k=5)
        assert isinstance(results, list)


class TestAnalyzerAgent:
    """Tests for AnalyzerAgent."""
    
    def test_analyzer_initialization(self):
        from aviation_ai_solution.agents.analyzer_agent import AnalyzerAgent
        
        agent = AnalyzerAgent()
        success = agent.initialize()
        assert success is True
        assert agent.tokai_enabled is True
    
    def test_tokai_extraction(self):
        from aviation_ai_solution.agents.analyzer_agent import AnalyzerAgent
        
        agent = AnalyzerAgent()
        agent.initialize()
        
        text = "The pilot did not see the traffic and failed to comply with procedure"
        factors = agent.extract_tokai_factors(text)
        
        assert "A-1_Perception" in factors
        assert "A-5_Conformance" in factors
        assert factors["A-1_Perception"]["negative"] > 0
        assert factors["A-5_Conformance"]["negative"] > 0
    
    def test_phraseology_check(self):
        from aviation_ai_solution.agents.analyzer_agent import AnalyzerAgent
        
        agent = AnalyzerAgent()
        agent.initialize()
        
        transcript = """
        ATC: DLH456 cleared to descend FL100
        Pilot: uh... roger DLH456
        """
        
        result = agent.check_phraseology_compliance(transcript)
        
        assert "compliant" in result
        assert len(result.get("non_standard_phrases", [])) > 0


class TestPredictorAgent:
    """Tests for PredictorAgent."""
    
    def test_predictor_initialization(self):
        from aviation_ai_solution.agents.predictor_agent import PredictorAgent
        
        agent = PredictorAgent()
        success = agent.initialize()
        assert success is True
    
    def test_risk_prediction(self):
        from aviation_ai_solution.agents.predictor_agent import PredictorAgent
        
        agent = PredictorAgent()
        agent.initialize()
        
        features = {
            "traffic_density": 0.8,
            "weather_severity": 0.5,
            "phraseology_compliance": 0.9
        }
        
        result = agent.predict_risk(features, context={"fir": "EDGG"})
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert 0 <= result["risk_score"] <= 1


class TestAdvisorAgent:
    """Tests for AdvisorAgent."""
    
    def test_advisor_initialization(self):
        from aviation_ai_solution.agents.advisor_agent import AdvisorAgent
        
        agent = AdvisorAgent()
        success = agent.initialize()
        assert success is True
    
    def test_advisory_generation(self):
        from aviation_ai_solution.agents.advisor_agent import AdvisorAgent
        
        agent = AdvisorAgent()
        agent.initialize()
        
        analysis = {"risk_indicators": [{"severity": "high"}]}
        prediction = {"risk_level": "HIGH", "risk_score": 0.85}
        
        result = agent.generate_advisory(analysis, prediction, {"flight_code": "DLH456"})
        
        assert "recommendations" in result
        assert "priority" in result
        assert result["priority"] in ["MAYDAY", "PAN-PAN", "routine"]


class TestGuardianAgent:
    """Tests for GuardianAgent."""
    
    def test_guardian_initialization(self):
        from aviation_ai_solution.agents.guardian_agent import GuardianAgent
        
        agent = GuardianAgent()
        success = agent.initialize()
        assert success is True
    
    def test_compliance_validation(self):
        from aviation_ai_solution.agents.guardian_agent import GuardianAgent
        
        agent = GuardianAgent()
        agent.initialize()
        
        data = {"transcript": "wilco"}
        result = agent.validate_compliance(data, ruleset="phraseology")
        
        assert "compliant" in result
        assert "compliance_score" in result


class TestOrchestratorAgent:
    """Tests for OrchestratorAgent."""
    
    def test_orchestrator_initialization(self):
        from aviation_ai_solution.agents.orchestrator_agent import OrchestratorAgent
        
        config = {
            "agents": {
                "retriever": {},
                "analyzer": {},
                "predictor": {},
                "advisor": {},
                "guardian": {}
            }
        }
        
        agent = OrchestratorAgent(config=config)
        success = agent.initialize()
        assert success is True
        assert len(agent.agents) == 5


class TestStreamProcessor:
    """Tests for StreamProcessor."""
    
    def test_session_grouping(self):
        from aviation_ai_solution.pipelines.stream_processor import StreamProcessor
        
        processor = StreamProcessor()
        
        data_points = [
            {"timestamp": "2026-05-06T14:30:00Z", "type": "adsb"},
            {"timestamp": "2026-05-06T14:35:00Z", "type": "metar"},
            {"timestamp": "2026-05-07T10:00:00Z", "type": "adsb"}
        ]
        
        sessions = processor.group_by_session(data_points)
        
        assert len(sessions) == 2
        assert "2026-05-06" in sessions
        assert "2026-05-07" in sessions
        assert len(sessions["2026-05-06"].data_points) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
