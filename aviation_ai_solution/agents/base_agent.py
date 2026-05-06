"""
Base Agent class for the Aviation AI multi-agent framework.

All specialized agents inherit from this base class to ensure consistent
interfaces and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: str = "request"  # request, response, event, escalation
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: str = "normal"  # low, normal, high, critical
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """State container for agent operations."""
    agent_id: str = ""
    status: str = "idle"  # idle, processing, waiting, error
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all aviation AI agents.
    
    Provides common functionality for agent initialization, message handling,
    state management, and logging.
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent. Auto-generated if not provided.
            config: Configuration dictionary for agent-specific settings.
        """
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.config = config or {}
        self.state = AgentState(agent_id=self.agent_id)
        self.message_queue: List[AgentMessage] = []
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize agent resources (models, connections, etc.).
        
        Returns:
            True if initialization successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process an incoming message and generate a response.
        
        Args:
            message: The incoming agent message to process.
            
        Returns:
            Response message with processed results.
        """
        pass
    
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task assigned to this agent.
        
        Args:
            task: Task definition with parameters and context.
            
        Returns:
            Task execution results.
        """
        pass
    
    def send_message(self, message: AgentMessage) -> None:
        """
        Queue a message for sending to another agent.
        
        Args:
            message: The message to queue.
        """
        message.sender = self.agent_id
        self.message_queue.append(message)
        
    def receive_message(self, message: AgentMessage) -> None:
        """
        Receive and queue an incoming message for processing.
        
        Args:
            message: The incoming message to queue.
        """
        message.recipient = self.agent_id
        self.message_queue.append(message)
        
    def get_next_message(self) -> Optional[AgentMessage]:
        """
        Retrieve the next message from the queue.
        
        Returns:
            The next message in the queue, or None if queue is empty.
        """
        if self.message_queue:
            return self.message_queue.pop(0)
        return None
    
    def update_state(self, status: str, task: Optional[str] = None, 
                     confidence: float = 1.0, error: Optional[str] = None) -> None:
        """
        Update the agent's internal state.
        
        Args:
            status: New status value.
            task: Current task name (optional).
            confidence: Confidence score for current operations.
            error: Error message if status is 'error'.
        """
        self.state.status = status
        self.state.current_task = task
        self.state.confidence_score = confidence
        self.state.error_message = error
        
        if status == "error" and error:
            self.state.metadata["last_error_time"] = datetime.utcnow().isoformat()
            
    def log(self, level: str, message: str, **kwargs) -> None:
        """
        Log a message with the specified level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            message: Log message content.
            **kwargs: Additional context to include in the log.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "level": level,
            "message": message,
            **kwargs
        }
        # In production, this would integrate with proper logging infrastructure
        print(f"[{log_entry['timestamp']}] [{level}] [{self.agent_id}] {message}")
        
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that input data contains all required fields.
        
        Args:
            data: Input data dictionary to validate.
            required_fields: List of required field names.
            
        Returns:
            True if validation passes, False otherwise.
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            self.log("WARNING", f"Missing required fields: {missing_fields}")
            return False
        return True
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return the capabilities of this agent.
        
        Returns:
            Dictionary describing agent capabilities.
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.__class__.__name__,
            "config": self.config,
            "status": self.state.status
        }
    
    def shutdown(self) -> None:
        """
        Clean up agent resources before shutdown.
        """
        self.log("INFO", "Shutting down agent")
        self.state.status = "shutdown"
        self.message_queue.clear()
