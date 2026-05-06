"""
Aviation AI Solution - Multi-Agent Framework for Aviation Records Analysis

This package implements an agentic AI system that retrieves, analyzes aviation records
(scattered and streamed), and delivers predictive/advisory/warning outputs for ATC operations.
"""

__version__ = "0.1.0"
__author__ = "Aviation AI Team"

from .agents.base_agent import BaseAgent
from .agents.retriever_agent import RetrieverAgent
from .agents.analyzer_agent import AnalyzerAgent
from .agents.predictor_agent import PredictorAgent
from .agents.advisor_agent import AdvisorAgent
from .agents.guardian_agent import GuardianAgent
from .agents.orchestrator_agent import OrchestratorAgent

__all__ = [
    "BaseAgent",
    "RetrieverAgent",
    "AnalyzerAgent",
    "PredictorAgent",
    "AdvisorAgent",
    "GuardianAgent",
    "OrchestratorAgent",
]
