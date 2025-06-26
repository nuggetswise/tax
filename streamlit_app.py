"""
Agentic Tax Return Drafter - Main Streamlit Application
"""

import streamlit as st
import os
import tempfile
import time
from typing import Dict, Any, List
import pandas as pd

# Import our modules
from agent.workflow import WorkflowEngine
from agent.steps.extract_data import ExtractData
from agent.steps.draft_forms import DraftForms
from agent.steps.diagnostics import Diagnostics
from agent.steps.adjustments import Adjustments
from services.provenance import get_provenance_tracker
from services.llm import get_llm_service
from ui.step_cards import (
    render_workflow_timeline, 
    render_progress_summary, 
    render_workflow_controls
)
from ui.form_1120_display import (
    render_form_1120_section,
    render_schedule_c,
    render_schedule_m1,
    render_form_summary,
    render_form_approval_controls
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "workflow_engine" not in st.session_state:
        st.session_state.workflow_engine = WorkflowEngine()
        # Add workflow steps
        st.session_state.workflow_engine.add_step(ExtractData())
        st.session_state.workflow_engine.add_step(DraftForms())
        st.session_state.workflow_engine.add_step(Diagnostics())
        st.session_state.workflow_engine.add_step(Adjustments())
    
    if "context" not in st.session_state:
        st.session_state.context = {}
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    if "current_time" not in st.session_state:
        st.session_state.current_time = time.time()


def get_available_sample_files():
    """Get list of available sample files with descriptions."""
    sample_files = [
        {
            "name": "client_gl_2024.csv",
            "path": "sample_data/client_gl_2024.csv",
            "description": "General Business - Standard C-Corp with $1.25M revenue, 70% COGS ratio",
            "business_type": "General Business",
            "revenue": "$1,250,000",
            "cogs_ratio": "70%"
        },
        {
            "name": "restaurant_1120_2024.csv", 
            "path": "sample_data/restaurant_1120_2024.csv",
            "description": "Restaurant - High COGS (76%), food costs, employee-heavy operations",
            "business_type": "Restaurant",
            "revenue": "$1,250,000", 
            "cogs_ratio": "76%"
        },
        {
            "name": "consulting_1120_2024.csv",
            "path": "sample_data/consulting_1120_2024.csv", 
            "description": "Consulting - Low COGS (10%), high salaries, professional services",
            "business_type": "Consulting",
            "revenue": "$850,000",
            "cogs_ratio": "10%"
        },
        {
            "name": "manufacturing_1120_2024.csv",
            "path": "sample_data/manufacturing_1120_2024.csv",
            "description": "Manufacturing - Very high COGS (80%), equipment depreciation, inventory",
            "business_type": "Manufacturing", 
            "revenue": "$2,100,000",
            "cogs_ratio": "80%"
        }
    ]
    
    # Filter to only include files that actually exist
    available_files = []
    for file_info in sample_files:
        if os.path.exists(file_info["path"]):
            file_info["size"] = os.path.getsize(file_info["path"])
            file_info["type"] = "text/csv"
            available_files.append(file_info)
    
    return available_files


def save_uploaded_file(uploaded_file) -> Dict[str, str]:
    """Save uploaded file to temporary location."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return {
            "name": uploaded_file.name,
            "path": tmp_file.name,
            "size": uploaded_file.size,
            "type": uploaded_file.type
        }


def render_file_selection_section():
    """Render file selection section with sample files and upload options."""
    st.header("📁 Select Tax Documents")
    
    # Create tabs for different selection methods
    tab1, tab2 = st.tabs(["📋 Sample Documents", "📤 Upload Your Own"])
    
    with tab1:
        st.markdown("**Choose a sample document to see how the agent handles different business types:**")
        
        available_samples = get_available_sample_files()
        
        if not available_samples:
            st.warning("No sample files found. Please upload your own documents.")
            return
        
        # Display sample files in a more compact grid
        cols = st.columns(2)
        selected_sample = None
        
        for i, sample in enumerate(available_samples):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"**{sample['business_type']}**")
                    st.write(f"💰 {sample['revenue']} | 📊 {sample['cogs_ratio']} COGS")
                    st.caption(sample['description'])
                    
                    if st.button(f"Select {sample['business_type']}", key=f"select_{i}"):
                        selected_sample = sample
        
        if selected_sample:
            st.session_state.uploaded_files = [selected_sample]
            st.session_state.context["uploaded_files"] = [selected_sample]
            st.success(f"✅ Selected: {selected_sample['business_type']}")
            st.rerun()
    
    with tab2:
        st.markdown("**Upload your own tax documents:**")
        
        uploaded_files = st.file_uploader(
            "Choose tax documents to process",
            type=["pdf", "csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="Upload PDF tax documents, CSV files, or Excel spreadsheets"
        )
        
        if uploaded_files:
            st.success(f"📎 {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display uploaded files more compactly
            for file in uploaded_files:
                col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                with col1:
                    st.write(f"📄 {file.name}")
                with col2:
                    st.write(f"{file.size / 1024:.1f} KB")
                with col3:
                    st.write(file.type or "Unknown")
            
            # Save files and update session state
            if st.button("🚀 Process Documents", type="primary"):
                with st.spinner("Saving uploaded files..."):
                    saved_files = []
                    for file in uploaded_files:
                        saved_file = save_uploaded_file(file)
                        saved_files.append(saved_file)
                    
                    st.session_state.uploaded_files = saved_files
                    st.session_state.context["uploaded_files"] = saved_files
                    st.success("Files saved and ready for processing!")
                    st.rerun()


def render_file_preview():
    """Render preview of selected file contents."""
    if not st.session_state.uploaded_files:
        return
    
    st.header("📊 File Preview")
    
    for file_info in st.session_state.uploaded_files:
        with st.expander(f"📄 {file_info['name']} - {file_info.get('business_type', 'Uploaded File')}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("File Size", f"{file_info['size'] / 1024:.1f} KB")
            with col2:
                st.metric("File Type", file_info['type'])
            with col3:
                if 'business_type' in file_info:
                    st.metric("Business Type", file_info['business_type'])
                else:
                    st.metric("Source", "User Upload")
            
            # Show file contents preview (more compact)
            if file_info['type'] == 'text/csv':
                try:
                    df = pd.read_csv(file_info['path'])
                    st.write("**File Contents Preview:**")
                    st.dataframe(df.head(5), use_container_width=True)  # Show only 5 rows instead of 10
                    
                    # Show summary statistics in a more compact way
                    if 'Debit' in df.columns and 'Credit' in df.columns:
                        total_debits = df['Debit'].sum() if 'Debit' in df.columns else 0
                        total_credits = df['Credit'].sum() if 'Credit' in df.columns else 0
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Debits", f"${total_debits:,.0f}")
                        with col2:
                            st.metric("Total Credits", f"${total_credits:,.0f}")
                        
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            else:
                st.info("File preview not available for this file type.")


def render_workflow_section():
    """Render workflow execution section."""
    st.header("⚙️ Workflow Execution")
    
    # Show which file is being processed (more compact)
    if st.session_state.uploaded_files:
        file_info = st.session_state.uploaded_files[0]
        st.info(f"🔄 **Processing:** {file_info['name']} ({file_info.get('business_type', 'Uploaded File')})")
        
        # Show file details in a more compact way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{file_info['size'] / 1024:.1f} KB")
        with col2:
            st.metric("File Type", file_info['type'])
        with col3:
            if 'business_type' in file_info:
                st.metric("Business Type", file_info['business_type'])
            else:
                st.metric("Source", "User Upload")
    
    # Workflow controls
    actions = render_workflow_controls()
    
    if actions.get("start"):
        if not st.session_state.uploaded_files:
            st.error("Please select or upload files before starting the workflow.")
            return
        
        with st.spinner(f"Running workflow on {st.session_state.uploaded_files[0]['name']}..."):
            st.session_state.current_time = time.time()
            
            # Execute workflow
            try:
                final_context = st.session_state.workflow_engine.execute(st.session_state.context)
                st.session_state.context = final_context
                st.success(f"✅ Workflow completed successfully for {st.session_state.uploaded_files[0]['name']}!")
                st.rerun()
            except Exception as e:
                st.error(f"Workflow failed: {str(e)}")
    
    elif actions.get("reset"):
        st.session_state.workflow_engine.reset()
        st.session_state.context = {}
        st.session_state.uploaded_files = []
        st.success("Workflow reset successfully!")
        st.rerun()
    
    # Display progress (more compact)
    progress_data = st.session_state.get("progress", {})
    if progress_data:
        render_progress_summary(progress_data)
        render_workflow_timeline(progress_data)


def render_results_section():
    """Render results and form display section."""
    if not st.session_state.context.get("drafted_forms"):
        return
    
    st.header("📊 Results & Form Review")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Form 1120", 
        "📋 Schedules", 
        "⚠️ Issues", 
        "🔧 Adjustments", 
        "📈 Summary"
    ])
    
    drafted_forms = st.session_state.context.get("drafted_forms", {})
    diagnostics = st.session_state.context.get("diagnostics", {})
    adjustments = st.session_state.context.get("adjustments", {})
    
    with tab1:
        # Form 1120 main section
        form_1120 = drafted_forms.get("form_1120", {})
        
        def on_field_change(field, value):
            """Handle field value changes."""
            if field in form_1120:
                form_1120[field]["value"] = value
                st.rerun()
        
        render_form_1120_section(form_1120, on_field_change)
        
        # Form approval controls
        approval_actions = render_form_approval_controls()
        if approval_actions.get("approve"):
            st.success("Form approved! ✅")
        elif approval_actions.get("request_changes"):
            st.warning("Changes requested. Please review and update the form.")
    
    with tab2:
        # Schedules
        schedule_c = drafted_forms.get("schedule_c", {})
        schedule_m1 = drafted_forms.get("schedule_m1", {})
        
        def on_schedule_field_change(field, value):
            """Handle schedule field changes."""
            if field.startswith("schedule_c_"):
                actual_field = field.replace("schedule_c_", "")
                if actual_field in schedule_c:
                    schedule_c[actual_field]["value"] = value
            elif field.startswith("schedule_m1_"):
                actual_field = field.replace("schedule_m1_", "")
                if actual_field in schedule_m1:
                    schedule_m1[actual_field]["value"] = value
            st.rerun()
        
        render_schedule_c(schedule_c, on_schedule_field_change)
        st.divider()
        render_schedule_m1(schedule_m1, on_schedule_field_change)
    
    with tab3:
        # Diagnostics (more compact)
        st.subheader("🔍 Diagnostic Results")
        
        if diagnostics.get("issues"):
            issues = diagnostics["issues"]
            
            # Summary metrics (more compact)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Issues", diagnostics.get("total_issues", 0))
            with col2:
                st.metric("Critical", diagnostics.get("critical_issues", 0))
            with col3:
                st.metric("Warnings", diagnostics.get("warnings", 0))
            with col4:
                st.metric("Info", diagnostics.get("info", 0))
            
            # Display issues by severity (more compact)
            for severity in ["critical", "warning", "info"]:
                severity_issues = [i for i in issues if i["severity"] == severity]
                if severity_issues:
                    st.markdown(f"**{severity.title()} Issues:**")
                    for issue in severity_issues:
                        with st.expander(f"⚠️ {issue['title']}", expanded=severity=="critical"):
                            st.write(f"**Description:** {issue['description']}")
                            if "field" in issue:
                                st.write(f"**Field:** {issue['field']}")
                            if "value" in issue and issue["value"] is not None:
                                st.write(f"**Current Value:** ${issue['value']:,.2f}")
                            if "expected" in issue:
                                st.write(f"**Expected Value:** ${issue['expected']:,.2f}")
        else:
            st.success("✅ No issues found! All checks passed.")
    
    with tab4:
        # Adjustments
        st.subheader("🔧 Suggested Adjustments")
        
        if adjustments.get("suggestions"):
            suggestions = adjustments["suggestions"]
            
            st.metric("Total Suggestions", adjustments.get("total_suggestions", 0))
            
            for i, suggestion in enumerate(suggestions):
                with st.expander(f"💡 {suggestion['description']}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Field:** {suggestion['field']}")
                        if suggestion['current_value'] is not None:
                            st.write(f"**Current:** ${suggestion['current_value']:,.2f}")
                        st.write(f"**Suggested:** ${suggestion['suggested_value']:,.2f}")
                    
                    with col2:
                        st.write(f"**Type:** {suggestion['adjustment_type']}")
                        st.write(f"**Priority:** {suggestion['priority']}")
                        st.write(f"**Confidence:** {suggestion['confidence']:.1%}")
                    
                    st.write(f"**Reasoning:** {suggestion['reasoning']}")
                    
                    # Apply button
                    if st.button(f"Apply Suggestion {i+1}", key=f"apply_{i}"):
                        # Apply the suggestion
                        field = suggestion['field']
                        new_value = suggestion['suggested_value']
                        
                        # Update the appropriate form field
                        if field.startswith("schedule_c_"):
                            actual_field = field.replace("schedule_c_", "")
                            if actual_field in drafted_forms.get("schedule_c", {}):
                                drafted_forms["schedule_c"][actual_field]["value"] = new_value
                        elif field.startswith("schedule_m1_"):
                            actual_field = field.replace("schedule_m1_", "")
                            if actual_field in drafted_forms.get("schedule_m1", {}):
                                drafted_forms["schedule_m1"][actual_field]["value"] = new_value
                        else:
                            if field in drafted_forms.get("form_1120", {}):
                                drafted_forms["form_1120"][field]["value"] = new_value
                        
                        st.success(f"Applied suggestion to {field}")
                        st.rerun()
        else:
            st.info("No adjustment suggestions available.")
    
    with tab5:
        # Summary
        render_form_summary(drafted_forms)


def render_provenance_section():
    """Render provenance tracking section."""
    st.sidebar.header("🔍 Provenance Trail")
    
    provenance_tracker = get_provenance_tracker()
    records = provenance_tracker.export_to_dict()
    
    if records:
        # Summary
        st.sidebar.metric("Total Records", len(records))
        
        # Confidence summary
        confidence_summary = provenance_tracker.get_confidence_summary()
        if confidence_summary:
            avg_confidence = sum(confidence_summary.values()) / len(confidence_summary)
            st.sidebar.metric("Avg Confidence", f"{avg_confidence:.1%}")
        
        # Recent records
        with st.sidebar.expander("Recent Activity", expanded=False):
            for record in records[-5:]:  # Show last 5 records
                st.write(f"**{record['step']}** - {record['field']}")
                st.write(f"Value: {record['value']}")
                st.write(f"Confidence: {record['confidence']:.1%}")
                st.caption(f"Source: {record['source_ref']}")
                st.divider()
        
        # Export provenance
        if st.sidebar.button("📤 Export Provenance"):
            df = pd.DataFrame(records)
            st.sidebar.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name="provenance_trail.csv",
                mime="text/csv"
            )
    else:
        st.sidebar.info("No provenance records yet.")


def render_llm_status_section():
    """Render LLM provider status in sidebar."""
    st.sidebar.header("🤖 LLM Status")
    
    try:
        llm_service = get_llm_service()
        available_providers = llm_service.get_available_providers()
        active_provider = llm_service.get_active_provider()
        
        st.sidebar.success(f"✅ Active: {active_provider}")
        st.sidebar.write(f"📡 Available: {', '.join(available_providers)}")
        
        # Provider status indicators
        for provider in available_providers:
            if provider == active_provider:
                st.sidebar.write(f"🟢 {provider} (Active)")
            else:
                st.sidebar.write(f"🟡 {provider} (Fallback)")
        
    except Exception as e:
        st.sidebar.error(f"❌ LLM Error: {str(e)}")


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Agentic Tax Return Drafter",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title and description (more compact)
    st.title("🤖 Agentic Tax Return Drafter")
    st.markdown("**AI-powered U.S. corporate tax return preparation with full audit trail**")
    
    # Create main layout
    col1, col2 = st.columns([3, 1])  # Changed from [2, 1] to [3, 1] for more main content space
    
    with col1:
        # Main content area
        if not st.session_state.uploaded_files:
            render_file_selection_section()
        else:
            render_file_preview()
            st.divider()
            render_workflow_section()
            render_results_section()
    
    with col2:
        # Sidebar content (more compact)
        render_llm_status_section()
        render_provenance_section()
        
        # File status (more compact)
        if st.session_state.uploaded_files:
            st.sidebar.header("📁 Files")
            for file in st.session_state.uploaded_files:
                st.sidebar.write(f"📄 {file['name']}")
                st.sidebar.caption(f"{file['size'] / 1024:.1f} KB")
        
        # Workflow status (more compact)
        if st.session_state.context:
            st.sidebar.header("⚙️ Status")
            progress_data = st.session_state.get("progress", {})
            if progress_data:
                completed = sum(1 for data in progress_data.values() if data.get("status") == "completed")
                total = len(progress_data)
                st.sidebar.progress(completed / total if total > 0 else 0)
                st.sidebar.write(f"{completed}/{total} steps completed")


if __name__ == "__main__":
    main()

