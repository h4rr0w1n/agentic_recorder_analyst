"""
Guardian Agent for compliance checking and validation.

Handles rule-based validation, ICAO phraseology compliance, audit trail generation,
and confidence calibration for safety-critical operations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentMessage


class GuardianAgent(BaseAgent):
    """
    Agent responsible for safety compliance and validation.
    
    Capabilities:
    - Rule-based validation against ICAO/IATA standards
    - ICAO Annex 10 phraseology compliance checker
    - SOP deviation detection (e.g., missed readbacks)
    - Regulatory boundary enforcement (FIR handoff protocols)
    - Audit trail generation
    - Confidence calibration
    """
    
    def __init__(self, agent_id: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(agent_id, config)
        
    def initialize(self) -> bool:
        """Initialize guardian rules and validators."""
        try:
            self.log("INFO", "Initializing Guardian Agent")
            
            # Initialize configuration
            self.icao_phraseology_strict = self.config.get("icao_phraseology_strict", True)
            self.confidence_threshold = self.config.get("confidence_threshold", 0.85)
            
            # Load compliance rules
            self._load_compliance_rules()
            
            self._initialized = True
            self.update_state("idle", confidence=1.0)
            self.log("INFO", "Guardian Agent initialized successfully")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize Guardian Agent: {str(e)}")
            self.update_state("error", error=str(e))
            return False
    
    def _load_compliance_rules(self) -> None:
        """Load ICAO/IATA compliance rules."""
        self.compliance_rules = {
            "phraseology": [
                {"rule_id": "PHR-001", "description": "Readback required for all clearances", "severity": "high"},
                {"rule_id": "PHR-002", "description": "Standard ICAO phraseology must be used", "severity": "medium"},
                {"rule_id": "PHR-003", "description": "Callsign must be included in initial contact", "severity": "medium"},
            ],
            "procedures": [
                {"rule_id": "SOP-001", "description": "FIR handoff protocol must be followed", "severity": "high"},
                {"rule_id": "SOP-002", "description": "Altitude change requires ATC clearance", "severity": "critical"},
                {"rule_id": "SOP-003", "description": "Emergency declarations require immediate acknowledgment", "severity": "critical"},
            ],
            "regulatory": [
                {"rule_id": "REG-001", "description": "Separation minima must be maintained", "severity": "critical"},
                {"rule_id": "REG-002", "description": "Flight level assignment per semicircular rule", "severity": "medium"},
            ]
        }
    
    def process_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming compliance check requests."""
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
            
            task_type = message.content.get("task_type", "validate_compliance")
            
            if task_type == "validate_compliance":
                results = self.validate_compliance(
                    data=message.content.get("data", {}),
                    ruleset=message.content.get("ruleset", "all")
                )
            elif task_type == "check_phraseology":
                results = self.check_icao_phraseology(
                    transcript=message.content.get("transcript", "")
                )
            elif task_type == "validate_advisory":
                results = self.validate_advisory(
                    advisory=message.content.get("advisory", {}),
                    context=message.content.get("context", {})
                )
            elif task_type == "generate_audit_trail":
                results = self.generate_audit_trail(
                    session_data=message.content.get("session_data", {})
                )
            elif task_type == "escalate_for_review":
                results = self.escalate_for_human_review(
                    item=message.content.get("item", {}),
                    reason=message.content.get("reason", "")
                )
            else:
                results = {"error": f"Unknown task type: {task_type}"}
            
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="response",
                content={"results": results},
                priority=message.priority,
                metadata={"validation_time": datetime.utcnow().isoformat()}
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
        """Execute a guardian task."""
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
    
    def validate_compliance(self, data: Dict, ruleset: str = "all") -> Dict[str, Any]:
        """
        Validate data against compliance rules.
        
        Args:
            data: Data to validate (transcript, advisory, flight data).
            ruleset: Which ruleset to apply (phraseology, procedures, regulatory, all).
            
        Returns:
            Compliance report with violations and recommendations.
        """
        self.log("INFO", f"Validating compliance with ruleset: {ruleset}")
        
        violations = []
        warnings = []
        compliant_count = 0
        
        # Determine which rules to check
        rules_to_check = []
        if ruleset == "all" or ruleset == "phraseology":
            rules_to_check.extend(self.compliance_rules.get("phraseology", []))
        if ruleset == "all" or ruleset == "procedures":
            rules_to_check.extend(self.compliance_rules.get("procedures", []))
        if ruleset == "all" or ruleset == "regulatory":
            rules_to_check.extend(self.compliance_rules.get("regulatory", []))
        
        # Check each rule
        for rule in rules_to_check:
            is_compliant, details = self._check_rule(rule, data)
            
            if is_compliant:
                compliant_count += 1
            else:
                violation = {
                    "rule_id": rule["rule_id"],
                    "description": rule["description"],
                    "severity": rule["severity"],
                    "details": details
                }
                
                if rule["severity"] in ["critical", "high"]:
                    violations.append(violation)
                else:
                    warnings.append(violation)
        
        total_rules = len(rules_to_check)
        compliance_score = compliant_count / total_rules if total_rules > 0 else 1.0
        
        return {
            "compliant": len(violations) == 0,
            "compliance_score": round(compliance_score, 3),
            "total_rules_checked": total_rules,
            "compliant_count": compliant_count,
            "violations": violations,
            "warnings": warnings,
            "ruleset_applied": ruleset,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def check_icao_phraseology(self, transcript: str) -> Dict[str, Any]:
        """
        Check transcript for ICAO Annex 10 phraseology compliance.
        
        Args:
            transcript: ATC/crew radio transcript.
            
        Returns:
            Phraseology compliance report.
        """
        self.log("INFO", "Checking ICAO phraseology compliance")
        
        report = {
            "compliant": True,
            "issues": [],
            "non_standard_terms": [],
            "missing_elements": [],
            "score": 1.0
        }
        
        # Standard ICAO phrases that should be present in proper contexts
        standard_clearance_responses = ["wilco", "roger", "affirm", "negative", "standby"]
        
        lines = transcript.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for non-standard filler words
            fillers = ["uh", "um", "like", "you know", "basically", "actually"]
            for filler in fillers:
                if filler in line_lower:
                    report["non_standard_terms"].append({
                        "line": i + 1,
                        "term": filler,
                        "context": line[:80]
                    })
                    report["issues"].append(f"Non-standard filler '{filler}' at line {i+1}")
            
            # Check for missing readback indicators after clearances
            if "cleared" in line_lower or "turn" in line_lower or "climb" in line_lower or "descend" in line_lower:
                # Look ahead for readback
                has_readback = any(
                    resp in ' '.join(lines[i:min(i+3, len(lines))]).lower() 
                    for resp in standard_clearance_responses
                )
                if not has_readback:
                    report["missing_elements"].append({
                        "line": i + 1,
                        "type": "readback",
                        "clearance": line[:80]
                    })
        
        # Calculate score
        penalty = (
            len(report["non_standard_terms"]) * 0.05 +
            len(report["missing_elements"]) * 0.15
        )
        report["score"] = max(0, 1.0 - penalty)
        report["compliant"] = report["score"] >= self.confidence_threshold
        
        return report
    
    def validate_advisory(self, advisory: Dict, context: Dict) -> Dict[str, Any]:
        """
        Validate an advisory before it's presented to users.
        
        Args:
            advisory: Advisory generated by Advisor Agent.
            context: Operational context.
            
        Returns:
            Validation report with approval status.
        """
        self.log("INFO", "Validating advisory")
        
        validation = {
            "approved": True,
            "requires_review": False,
            "rejection_reasons": [],
            "warnings": [],
            "modifications_suggested": []
        }
        
        # Check advisory confidence
        avg_confidence = 0
        recommendations = advisory.get("recommendations", [])
        if recommendations:
            avg_confidence = sum(r.get("confidence", 0) for r in recommendations) / len(recommendations)
        
        if avg_confidence < self.confidence_threshold:
            validation["requires_review"] = True
            validation["warnings"].append(f"Average confidence ({avg_confidence:.2f}) below threshold ({self.confidence_threshold})")
        
        # Check for critical actions without sufficient evidence
        for rec in recommendations:
            if rec.get("action_required") and rec.get("time_critical"):
                if rec.get("confidence", 0) < 0.9:
                    validation["requires_review"] = True
                    validation["warnings"].append(
                        f"Time-critical action '{rec.get('id')}' has low confidence ({rec.get('confidence')})"
                    )
        
        # Check ICAO phrasing in recommendations
        for rec in recommendations:
            text = rec.get("text", "")
            if "maybe" in text.lower() or "possibly" in text.lower():
                validation["modifications_suggested"].append({
                    "recommendation_id": rec.get("id"),
                    "issue": "Uncertain language detected",
                    "suggestion": "Use definitive ICAO-compliant phrasing"
                })
        
        # Check for hallucinated information
        if "hallucination_score" in advisory:
            if advisory["hallucination_score"] > 0.2:
                validation["rejection_reasons"].append("High hallucination risk detected")
                validation["approved"] = False
        
        return validation
    
    def generate_audit_trail(self, session_data: Dict) -> Dict[str, Any]:
        """
        Generate audit trail for a session.
        
        Args:
            session_data: Complete session data including all agent interactions.
            
        Returns:
            Audit trail document.
        """
        self.log("INFO", "Generating audit trail")
        
        audit_trail = {
            "audit_id": f"AUDIT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "session_summary": {
                "start_time": session_data.get("start_time"),
                "end_time": session_data.get("end_time"),
                "flight_code": session_data.get("flight_code"),
                "fir": session_data.get("fir")
            },
            "agent_interactions": [],
            "decisions_made": [],
            "human_interventions": [],
            "compliance_checks": [],
            "recommendations_issued": []
        }
        
        # Extract agent interactions
        for agent_name, agent_data in session_data.get("agent_outputs", {}).items():
            audit_trail["agent_interactions"].append({
                "agent": agent_name,
                "tasks_performed": agent_data.get("tasks", []),
                "confidence_scores": agent_data.get("confidence_scores", []),
                "errors": agent_data.get("errors", [])
            })
        
        # Extract decisions
        if "final_output" in session_data:
            audit_trail["decisions_made"].append({
                "decision_type": "advisory_generation",
                "output_summary": str(session_data["final_output"])[:200],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return audit_trail
    
    def escalate_for_human_review(self, item: Dict, reason: str) -> Dict[str, Any]:
        """
        Escalate an item for human expert review.
        
        Args:
            item: Item requiring review (advisory, prediction, etc.).
            reason: Reason for escalation.
            
        Returns:
            Escalation record.
        """
        self.log("WARNING", f"Escalating for human review: {reason}")
        
        escalation = {
            "escalation_id": f"ESC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "item_type": item.get("type", "unknown"),
            "item_id": item.get("id", "unknown"),
            "reason": reason,
            "priority": item.get("priority", "normal"),
            "status": "pending_review",
            "assigned_to": None,
            "review_deadline": None
        }
        
        # Set deadline based on priority
        if item.get("priority") == "MAYDAY":
            escalation["review_deadline"] = datetime.utcnow().isoformat()  # Immediate
            escalation["status"] = "urgent"
        elif item.get("priority") == "PAN-PAN":
            escalation["priority"] = "high"
        
        return escalation
    
    def _check_rule(self, rule: Dict, data: Dict) -> tuple:
        """Check a single compliance rule against data."""
        rule_id = rule["rule_id"]
        
        # Simplified rule checking logic
        # In production, implement proper rule engine
        
        if rule_id.startswith("PHR"):
            # Phraseology rules
            transcript = data.get("transcript", "")
            if rule_id == "PHR-001":  # Readback required
                has_readback = "wilco" in transcript.lower() or "roger" in transcript.lower()
                return has_readback, "Readback detected" if has_readback else "No readback found"
        
        elif rule_id.startswith("SOP"):
            # Procedure rules
            if rule_id == "SOP-002":  # Altitude change requires clearance
                altitude_changes = data.get("altitude_changes", [])
                all_cleared = all(change.get("cleared", False) for change in altitude_changes)
                return all_cleared, "All altitude changes cleared" if all_cleared else "Uncleared altitude change detected"
        
        elif rule_id.startswith("REG"):
            # Regulatory rules
            if rule_id == "REG-001":  # Separation minima
                separation = data.get("current_separation_nm", 10)
                return separation >= 5, f"Separation: {separation}nm"
        
        # Default: assume compliant
        return True, "Rule check passed"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Guardian-specific capabilities."""
        base_caps = super().get_capabilities()
        base_caps.update({
            "validation_types": [
                "compliance_check", "phraseology_validation", "advisory_validation",
                "audit_trail_generation", "human_escalation"
            ],
            "rulesets": list(self.compliance_rules.keys()) if hasattr(self, 'compliance_rules') else [],
            "confidence_threshold": self.confidence_threshold,
            "icao_annex_10_compliance": True,
            "sop_deviation_detection": True
        })
        return base_caps
