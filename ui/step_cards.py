"""
Reusable Streamlit components for workflow step display.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
import time


def render_step_card(step_name: str, step_data: Dict[str, Any], step_number: int, total_steps: int) -> None:
    """
    Render a single step card in the workflow timeline.
    
    Args:
        step_name: Name of the step
        step_data: Step status and metadata
        step_number: Current step number
        total_steps: Total number of steps
    """
    status = step_data.get("status", "pending")
    
    # Create container for the step card
    with st.container():
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            # Status icon
            if status == "completed":
                st.success("✅")
            elif status == "running":
                st.info("🔄")
            elif status == "failed":
                st.error("❌")
            else:
                st.write("⏳")
        
        with col2:
            # Step header
            st.markdown(f"**Step {step_number}: {step_name}**")
            
            # Status badge
            if status == "completed":
                st.success(f"Completed")
            elif status == "running":
                st.info("Running...")
            elif status == "failed":
                st.error("Failed")
            else:
                st.write("Pending")
            
            # Progress bar
            if status == "running":
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
            
            # Error message if failed
            if status == "failed" and "error" in step_data:
                with st.expander("Error Details", expanded=False):
                    st.error(step_data["error"])
            
            # Execution time if completed
            if status == "completed" and "execution_time" in step_data:
                st.caption(f"⏱️ {step_data['execution_time']:.2f}s")
            
            st.divider()


def render_workflow_timeline(progress_data: Dict[str, Any]):
    """Render workflow steps as a compact table."""
    if not progress_data:
        return
    
    st.markdown("### 🗂️ Workflow Steps")
    
    # Table header
    cols = st.columns([2, 1, 1])
    with cols[0]:
        st.markdown("**Step**")
    with cols[1]:
        st.markdown("**Status**")
    with cols[2]:
        st.markdown("**Duration**")
    
    # Table rows
    for step_name, step_info in progress_data.items():
        cols = st.columns([2, 1, 1])
        status = step_info.get("status", "pending")
        duration = step_info.get("duration", 0.0)
        error = step_info.get("error", None)
        
        # Status icon
        if status == "completed":
            icon = "✅"
            status_text = "Completed"
        elif status == "failed":
            icon = "❌"
            status_text = "Failed"
        elif status == "running":
            icon = "⏳"
            status_text = "Running"
        else:
            icon = "⬜"
            status_text = status.title()
        
        with cols[0]:
            st.write(step_name)
        with cols[1]:
            st.write(f"{icon} {status_text}")
        with cols[2]:
            st.write(f"{duration:.2f}s")
        
        # Expandable error details if failed
        if status == "failed" and error:
            st.expander(f"Error Details for {step_name}").write(error)


def render_progress_summary(progress_data: Dict[str, Any]) -> None:
    """
    Render a summary of overall workflow progress.
    
    Args:
        progress_data: Progress data from session state
    """
    if not progress_data:
        return
    
    completed = sum(1 for data in progress_data.values() if data.get("status") == "completed")
    failed = sum(1 for data in progress_data.values() if data.get("status") == "failed")
    total = len(progress_data)
    
    # Progress metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Steps", total)
    
    with col2:
        st.metric("Completed", completed, delta=completed)
    
    with col3:
        st.metric("Failed", failed, delta=failed)
    
    with col4:
        progress_pct = (completed / total * 100) if total > 0 else 0
        st.metric("Progress", f"{progress_pct:.1f}%")


def render_step_details(step_name: str, step_data: Dict[str, Any]) -> None:
    """
    Render detailed information for a specific step.
    
    Args:
        step_name: Name of the step
        step_data: Step data and metadata
    """
    with st.expander(f"📊 {step_name} Details", expanded=False):
        st.json(step_data)


def render_workflow_controls() -> Dict[str, Any]:
    """
    Render workflow control buttons.
    
    Returns:
        Dictionary with control actions
    """
    col1, col2, col3 = st.columns(3)
    
    actions = {}
    
    with col1:
        if st.button("🚀 Start Workflow", type="primary"):
            actions["start"] = True
    
    with col2:
        if st.button("🔄 Reset"):
            actions["reset"] = True
    
    with col3:
        if st.button("⏸️ Pause"):
            actions["pause"] = True
    
    return actions


def render_status_badge(status: str) -> None:
    """
    Render a status badge with appropriate styling.
    
    Args:
        status: Status string (pending, running, completed, failed)
    """
    if status == "completed":
        st.success("✅ Completed")
    elif status == "running":
        st.info("🔄 Running")
    elif status == "failed":
        st.error("❌ Failed")
    else:
        st.write("⏳ Pending")


def render_execution_time(execution_time: Optional[float]) -> None:
    """
    Render execution time with appropriate formatting.
    
    Args:
        execution_time: Execution time in seconds
    """
    if execution_time is not None:
        if execution_time < 60:
            st.caption(f"⏱️ {execution_time:.2f}s")
        else:
            minutes = int(execution_time // 60)
            seconds = execution_time % 60
            st.caption(f"⏱️ {minutes}m {seconds:.1f}s")

