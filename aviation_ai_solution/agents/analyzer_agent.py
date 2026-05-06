"""
Analyzer Agent for NLP/NLU analysis of aviation transcripts.

Handles domain-tuned NLP, TOKAI taxonomy factor extraction, phraseology compliance,
and multi-snippet conversation chaining for full flight narratives.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import re

from .base_agent import BaseAgent, AgentMessage


class AnalyzerAgent(BaseAgent):
    """
    Agent responsible for semantic analysis of aviation data.
    
    Capabilities:
    - Domain-tuned NLP (aviation phraseology)
    - Syntactic dependency parsing
    - Topic modeling for incident clustering
    - TOKAI taxonomy factor extraction (A-1 Perception to A-5 Conformance)
    - Non-verbal signal detection (radio silence, readback errors)
    - Multi-snippet conversation chaining for full flight narrative
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        self.nlp_model = None
        self.tokai_patterns = {}
        
    def initialize(self) -> bool:
        """Initialize NLP models and analysis pipelines."""
        try:
            self.log("INFO", "Initializing Analyzer Agent")
            
            # Initialize configuration
            self.tokai_enabled = self.config.get("tokai_taxonomy_enabled", True)
            self.phraseology_check_enabled = self.config.get("phraseology_check_enabled", True)
            
            # Initialize TOKAI factor patterns
            if self.tokai_enabled:
                self._init_tokai_patterns()
            
            # In production, load actual NLP model
            # self.nlp_model = spacy.load("en_aviation_core")
            
            self._initialized = True
            self.update_state("idle", confidence=1.0)
            self.log("INFO", "Analyzer Agent initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Analyzer Agent: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def _init_tokai_patterns(self) -> None:
        """Initialize TOKAI taxonomy factor extraction patterns."""
        self.tokai_patterns = {
            "A-1_Perception": [
                "see", "detect", "identify", "hear", "visual contact", 
                "observe", "spot", "notice", "look", "view"
            ],
            "A-2_Memory": [
                "remember", "recall", "forget", "previous instruction",
                "previously", "earlier", "before", "past"
            ],
            "A-3_Decision": [
                "decide", "plan", "judge", "select route", "choose",
                "determine", "resolve", "conclude"
            ],
            "A-4_Action": [
                "execute", "convey", "record", "transmit", "perform",
                "implement", "carry out", "act"
            ],
            "A-5_Conformance": [
                "comply", "deviate", "procedure", "SOP", "regulation",
                "standard", "protocol", "requirement", "clearance"
            ]
        }
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming analysis requests."""
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
            
            task_type = message.content.get("task_type", "analyze_transcript")
            
            if task_type == "analyze_transcript":
                results = self.analyze_transcript(
                    transcript=message.content.get("transcript", ""),
                    metadata=message.content.get("metadata", {})
                )
            elif task_type == "extract_tokai_factors":
                results = self.extract_tokai_factors(
                    text=message.content.get("text", "")
                )
            elif task_type == "check_phraseology":
                results = self.check_phraseology_compliance(
                    transcript=message.content.get("transcript", "")
                )
            elif task_type == "chain_conversations":
                results = self.chain_conversation_snippets(
                    snippets=message.content.get("snippets", []),
                    time_threshold=message.content.get("time_threshold", 300)
                )
            elif task_type == "detect_nonverbal_signals":
                results = self.detect_nonverbal_signals(
                    transcript=message.content.get("transcript", ""),
                    audio_metadata=message.content.get("audio_metadata", {})
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results},
                priority=message.priority,
                metadata={"analysis_time": datetime.utcnow().isoformat()}
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
        """Execute an analysis task."""
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
    
    def analyze_transcript(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of an ATC transcript.
        
        Args:
            transcript: ATC/crew radio transcript text.
            metadata: Optional metadata (flight code, timestamp, FIR, etc.).
            
        Returns:
            Analysis results including TOKAI factors, phraseology compliance, and insights.
        """
        self.log("INFO", "Analyzing transcript")
        
        metadata = metadata or {}
        
        results = {
            "metadata": metadata,
            "transcript_length": len(transcript),
            "tokai_factors": {},
            "phraseology_compliance": {},
            "nonverbal_signals": {},
            "topics": [],
            "sentiment": None,
            "risk_indicators": []
        }
        
        # Extract TOKAI factors
        if self.tokai_enabled:
            results["tokai_factors"] = self.extract_tokai_factors(transcript)
        
        # Check phraseology compliance
        if self.phraseology_check_enabled:
            results["phraseology_compliance"] = self.check_phraseology_compliance(transcript)
        
        # Detect non-verbal signals
        results["nonverbal_signals"] = self.detect_nonverbal_signals(transcript)
        
        # Extract topics
        results["topics"] = self._extract_topics(transcript)
        
        # Identify risk indicators
        results["risk_indicators"] = self._identify_risk_indicators(transcript, results)
        
        return results
    
    def extract_tokai_factors(self, text: str) -> Dict[str, Dict[str, int]]:
        """
        Extract TOKAI taxonomy factors from text.
        
        TOKAI Factors:
        - A-1: Perception issues
        - A-2: Memory issues
        - A-3: Decision-making issues
        - A-4: Action issues
        - A-5: Conformance issues
        
        Args:
            text: Input text to analyze.
            
        Returns:
            Dictionary with factor counts (positive/negative).
        """
        factors = {k: {"positive": 0, "negative": 0} for k in self.tokai_patterns.keys()}
        
        text_lower = text.lower()
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for negation in sentence
            has_negation = any(neg in sentence_lower for neg in ["not", "no", "never", "failed", "unable", "incorrectly"])
            
            for factor, keywords in self.tokai_patterns.items():
                for keyword in keywords:
                    if keyword in sentence_lower:
                        if has_negation:
                            factors[factor]["negative"] += 1
                        else:
                            factors[factor]["positive"] += 1
        
        return factors
    
    def check_phraseology_compliance(self, transcript: str) -> Dict[str, Any]:
        """
        Check transcript for ICAO standard phraseology compliance.
        
        Args:
            transcript: ATC transcript to check.
            
        Returns:
            Compliance report with violations and recommendations.
        """
        compliance_report = {
            "compliant": True,
            "violations": [],
            "warnings": [],
            "readback_errors": [],
            "missing_readbacks": [],
            "non_standard_phrases": []
        }
        
        # Standard ICAO phraseology patterns
        standard_patterns = [
            r"(?i)\bcleared (to|for|via)\b",
            r"(?i)\bexpect (further clearance|approach)\b",
            r"(?i)\broger\b",
            r"(?i)\bwilco\b",
            r"(?i)\bstandby\b",
            r"(?i)\baffirm(negative)?\b",
            r"(?i)\bmayday\b",
            r"(?i)\bpan pan\b",
        ]
        
        # Non-standard phrases that might indicate issues
        non_standard_indicators = [
            "uh", "um", "like", "you know", "basically",
            "I think", "maybe", "probably", "sort of"
        ]
        
        lines = transcript.split('\n')
        for i, line in enumerate(lines):
            # Check for non-standard phrases
            for indicator in non_standard_indicators:
                if indicator in line.lower():
                    compliance_report["non_standard_phrases"].append({
                        "line": i + 1,
                        "phrase": indicator,
                        "context": line.strip()[:100]
                    })
                    compliance_report["warnings"].append(f"Non-standard phrase at line {i+1}: '{indicator}'")
            
            # Check for incomplete readbacks (simplified check)
            if "cleared" in line.lower() and ("readback" not in line.lower() and "wilco" not in line.lower()):
                if not any("roger" in l.lower() or "wilco" in l.lower() for l in lines[i:min(i+3, len(lines))]):
                    compliance_report["missing_readbacks"].append({
                        "line": i + 1,
                        "clearance": line.strip()[:100]
                    })
        
        # Determine overall compliance
        if compliance_report["violations"] or compliance_report["missing_readbacks"]:
            compliance_report["compliant"] = False
        
        compliance_report["compliance_score"] = max(0, 1.0 - (
            len(compliance_report["violations"]) * 0.2 +
            len(compliance_report["warnings"]) * 0.05 +
            len(compliance_report["missing_readbacks"]) * 0.15
        ))
        
        return compliance_report
    
    def chain_conversation_snippets(self, snippets: List[Dict], 
                                    time_threshold: int = 300) -> Dict[str, Any]:
        """
        Chain multiple conversation snippets into a full flight narrative.
        
        Args:
            snippets: List of conversation snippets with timestamps.
            time_threshold: Maximum time gap (seconds) to consider snippets related.
            
        Returns:
            Chained conversation with temporal ordering and context linking.
        """
        if not snippets:
            return {"chained_conversation": [], "gaps": [], "total_duration": 0}
        
        # Sort snippets by timestamp
        sorted_snippets = sorted(snippets, key=lambda x: x.get("timestamp", ""))
        
        chained = []
        gaps = []
        current_chain = []
        
        for i, snippet in enumerate(sorted_snippets):
            if not current_chain:
                current_chain.append(snippet)
            else:
                # Calculate time gap
                prev_time = self._parse_timestamp(current_chain[-1].get("timestamp", ""))
                curr_time = self._parse_timestamp(snippet.get("timestamp", ""))
                
                if prev_time and curr_time:
                    gap_seconds = (curr_time - prev_time).total_seconds()
                    
                    if gap_seconds > time_threshold:
                        # Significant gap - save current chain and start new one
                        if current_chain:
                            chained.append({
                                "segment_id": len(chained) + 1,
                                "snippets": current_chain,
                                "start_time": current_chain[0].get("timestamp"),
                                "end_time": current_chain[-1].get("timestamp"),
                                "duration_seconds": gap_seconds
                            })
                        gaps.append({
                            "after_segment": len(chained),
                            "gap_seconds": gap_seconds,
                            "before": current_chain[-1].get("timestamp"),
                            "after": snippet.get("timestamp")
                        })
                        current_chain = [snippet]
                    else:
                        current_chain.append(snippet)
                else:
                    current_chain.append(snippet)
        
        # Add final chain
        if current_chain:
            chained.append({
                "segment_id": len(chained) + 1,
                "snippets": current_chain,
                "start_time": current_chain[0].get("timestamp"),
                "end_time": current_chain[-1].get("timestamp")
            })
        
        # Calculate total duration
        total_duration = 0
        if chained:
            first_start = self._parse_timestamp(chained[0]["start_time"])
            last_end = self._parse_timestamp(chained[-1]["end_time"])
            if first_start and last_end:
                total_duration = (last_end - first_start).total_seconds()
        
        return {
            "chained_conversation": chained,
            "gaps": gaps,
            "total_segments": len(chained),
            "total_duration_seconds": total_duration,
            "snippet_count": len(snippets)
        }
    
    def detect_nonverbal_signals(self, transcript: str, 
                                 audio_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Detect non-verbal signals in communication.
        
        Args:
            transcript: ATC transcript.
            audio_metadata: Optional audio metadata (silence periods, transmission quality).
            
        Returns:
            Detection results for radio silence, transmission issues, etc.
        """
        signals = {
            "radio_silence_periods": [],
            "transmission_quality_issues": [],
            "interruptions": [],
            "overlapping_communications": [],
            "stress_indicators": []
        }
        
        # Analyze transcript for stress indicators
        stress_words = ["urgent", "emergency", "immediately", "now", "quickly", "hurry"]
        lines = transcript.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for stress indicators
            for word in stress_words:
                if word in line_lower:
                    signals["stress_indicators"].append({
                        "line": i + 1,
                        "indicator": word,
                        "context": line.strip()[:100]
                    })
            
            # Check for interruptions (incomplete sentences)
            if line.strip().endswith('-') or line.strip().endswith('...'):
                signals["interruptions"].append({
                    "line": i + 1,
                    "text": line.strip()
                })
        
        # Process audio metadata if provided
        if audio_metadata:
            if "silence_periods" in audio_metadata:
                signals["radio_silence_periods"] = audio_metadata["silence_periods"]
            
            if "transmission_quality" in audio_metadata:
                signals["transmission_quality_issues"] = audio_metadata["transmission_quality"]
        
        return signals
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - in production, use proper NLP
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_topics(self, transcript: str) -> List[str]:
        """Extract topics from transcript."""
        # Simplified topic extraction - in production, use LDA or similar
        aviation_topics = {
            "weather": ["weather", "metar", "turbulence", "wind", "visibility", "cloud"],
            "navigation": ["route", "waypoint", "fix", "heading", "course", "track"],
            "clearance": ["cleared", "clearance", "approved", "authorized"],
            "emergency": ["mayday", "pan", "emergency", "urgent"],
            "traffic": ["traffic", "conflict", "separation", "distance"]
        }
        
        transcript_lower = transcript.lower()
        detected_topics = []
        
        for topic, keywords in aviation_topics.items():
            if any(keyword in transcript_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _identify_risk_indicators(self, transcript: str, analysis_results: Dict) -> List[Dict]:
        """Identify potential risk indicators from analysis."""
        risk_indicators = []
        
        # Check TOKAI factors for negative patterns
        tokai = analysis_results.get("tokai_factors", {})
        for factor, counts in tokai.items():
            if counts.get("negative", 0) > counts.get("positive", 0):
                risk_indicators.append({
                    "type": "tokai_factor_imbalance",
                    "factor": factor,
                    "severity": "medium",
                    "details": f"Negative {factor} indicators exceed positive"
                })
        
        # Check phraseology compliance
        phraseology = analysis_results.get("phraseology_compliance", {})
        if not phraseology.get("compliant", True):
            risk_indicators.append({
                "type": "phraseology_violation",
                "severity": "high" if phraseology.get("missing_readbacks") else "medium",
                "details": "Phraseology compliance issues detected"
            })
        
        # Check for emergency keywords
        emergency_keywords = ["mayday", "pan pan", "emergency", "fuel emergency"]
        if any(kw in transcript.lower() for kw in emergency_keywords):
            risk_indicators.append({
                "type": "emergency_declaration",
                "severity": "critical",
                "details": "Emergency keywords detected in transcript"
            })
        
        return risk_indicators
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Analyzer-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "analysis_types": [
                "transcript_analysis", "tokai_extraction", "phraseology_check",
                "conversation_chaining", "nonverbal_detection"
            ],
            "tokai_taxonomy_enabled": self.tokai_enabled,
            "phraseology_check_enabled": self.phraseology_check_enabled,
            "supported_languages": ["en"],  # Extendable to more languages
            "aviation_domain_tuned": True
        })
        return base_caps
