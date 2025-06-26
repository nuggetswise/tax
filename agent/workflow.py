"""
Workflow engine for agentic tax return drafting.
Manages step execution, error handling, and progress tracking.
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import streamlit as st
from services.provenance import get_provenance_tracker


class BaseStep(ABC):
    """Base class for all workflow steps."""
    
    def __init__(self, name: str, description: str):
        """Initialize step with name and description."""
        self.name = name
        self.description = description
        self.status = "pending"  # pending, running, completed, failed
        self.error_message: Optional[str] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the step logic.
        
        Args:
            context: Current workflow context
            
        Returns:
            Updated context
        """
        pass
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle step execution errors.
        
        Args:
            context: Current workflow context
            error: Exception that occurred
            
        Returns:
            Updated context (may include error handling)
        """
        self.status = "failed"
        self.error_message = str(error)
        return context
    
    def get_execution_time(self) -> Optional[float]:
        """Get step execution time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class WorkflowEngine:
    """Orchestrates the execution of workflow steps."""
    
    def __init__(self):
        """Initialize workflow engine."""
        self.steps: List[BaseStep] = []
        self.provenance_tracker = get_provenance_tracker()
    
    def add_step(self, step: BaseStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all workflow steps in order.
        
        Args:
            context: Initial workflow context
            
        Returns:
            Final context after all steps complete
        """
        # Initialize progress tracking
        if "progress" not in st.session_state:
            st.session_state["progress"] = {}
        
        for i, step in enumerate(self.steps):
            try:
                # Update step status
                step.status = "running"
                step.start_time = st.session_state.get("current_time", 0)
                
                # Update progress in session state
                st.session_state["progress"][step.name] = {
                    "status": "running",
                    "step_number": i + 1,
                    "total_steps": len(self.steps)
                }
                
                # Execute step
                context = step.run(context)
                
                # Mark step as completed
                step.status = "completed"
                step.end_time = st.session_state.get("current_time", 0)
                
                # Update progress
                st.session_state["progress"][step.name] = {
                    "status": "completed",
                    "step_number": i + 1,
                    "total_steps": len(self.steps),
                    "execution_time": step.get_execution_time()
                }
                
            except Exception as e:
                # Handle step failure
                context = step.on_error(context, e)
                
                # Update progress with error
                st.session_state["progress"][step.name] = {
                    "status": "failed",
                    "step_number": i + 1,
                    "total_steps": len(self.steps),
                    "error": str(e)
                }
                
                # Optionally continue or break
                if not self._should_continue_on_error(step, e):
                    break
        
        return context
    
    def _should_continue_on_error(self, step: BaseStep, error: Exception) -> bool:
        """
        Determine if workflow should continue after step failure.
        
        Args:
            step: The step that failed
            error: The exception that occurred
            
        Returns:
            True if workflow should continue, False to stop
        """
        # For now, continue on all errors - can be customized per step
        return True
    
    def reset(self) -> None:
        """Reset all steps to pending status."""
        for step in self.steps:
            step.status = "pending"
            step.error_message = None
            step.start_time = None
            step.end_time = None
        
        # Clear progress
        if "progress" in st.session_state:
            st.session_state["progress"] = {}
    
    def get_step_status(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific step."""
        for step in self.steps:
            if step.name == step_name:
                return {
                    "name": step.name,
                    "description": step.description,
                    "status": step.status,
                    "error_message": step.error_message,
                    "execution_time": step.get_execution_time()
                }
        return None
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall workflow progress."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for step in self.steps if step.status == "completed")
        failed_steps = sum(1 for step in self.steps if step.status == "failed")
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "pending_steps": total_steps - completed_steps - failed_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
        }

