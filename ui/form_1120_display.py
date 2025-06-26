"""
Form 1120 display component for showing drafted tax form with editing capabilities.
"""

import streamlit as st
from typing import Dict, Any, Optional, Callable


def render_form_1120_section(form_data: Dict[str, Any], on_field_change: Optional[Callable] = None) -> None:
    """
    Render Form 1120 main section with editable fields.
    
    Args:
        form_data: Form 1120 data
        on_field_change: Callback function when field value changes
    """
    st.subheader("📄 Form 1120 - U.S. Corporation Income Tax Return")
    
    # Income section
    st.markdown("**Income**")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    
    with col1:
        st.write("1a. Gross receipts or sales")
    with col2:
        value = form_data.get("line_1a", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_1a", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_1a", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("2. Returns and allowances")
    with col2:
        value = form_data.get("line_2", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_2", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_2", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("3. Net receipts or sales")
    with col2:
        value = form_data.get("line_3", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_3", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_3", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("4. Cost of goods sold")
    with col2:
        value = form_data.get("line_4", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_4", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_4", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("5. Gross profit")
    with col2:
        value = form_data.get("line_5", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_5", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_5", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("6. Other income")
    with col2:
        value = form_data.get("line_6", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_6", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_6", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("7. Gross income")
    with col2:
        value = form_data.get("line_7", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_7", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_7", new_value)
    with col3:
        st.caption("$")
    
    st.divider()
    
    # Deductions section
    st.markdown("**Deductions**")
    
    deduction_fields = [
        ("line_8", "8. Compensation of officers"),
        ("line_9", "9. Salaries and wages"),
        ("line_10", "10. Repairs and maintenance"),
        ("line_11", "11. Bad debts"),
        ("line_12", "12. Rents"),
        ("line_13", "13. Taxes and licenses"),
        ("line_14", "14. Interest"),
        ("line_15", "15. Charitable contributions"),
        ("line_16", "16. Depreciation and depletion"),
        ("line_17", "17. Depletion"),
        ("line_18", "18. Advertising"),
        ("line_19", "19. Pension, profit-sharing, etc., plans"),
        ("line_20", "20. Employee benefit programs"),
        ("line_21", "21. Other deductions"),
    ]
    
    for field_key, field_label in deduction_fields:
        col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
        with col1:
            st.write(field_label)
        with col2:
            value = form_data.get(field_key, {}).get("value", 0)
            new_value = st.number_input("", value=float(value), key=field_key, format="%.2f")
            if new_value != value and on_field_change:
                on_field_change(field_key, new_value)
        with col3:
            st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("22. Total deductions")
    with col2:
        value = form_data.get("line_22", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_22", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_22", new_value)
    with col3:
        st.caption("$")
    
    st.divider()
    
    # Taxable income section
    st.markdown("**Taxable Income**")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("23. Taxable income before NOL and special deductions")
    with col2:
        value = form_data.get("line_23", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_23", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_23", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("24. Net operating loss deduction")
    with col2:
        value = form_data.get("line_24", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_24", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_24", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("25. Special deductions")
    with col2:
        value = form_data.get("line_25", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_25", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_25", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("26. Taxable income")
    with col2:
        value = form_data.get("line_26", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_26", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_26", new_value)
    with col3:
        st.caption("$")
    
    st.divider()
    
    # Tax and payments section
    st.markdown("**Tax and Payments**")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("27. Total tax")
    with col2:
        value = form_data.get("line_27", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_27", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_27", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("28. Credits")
    with col2:
        value = form_data.get("line_28", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_28", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_28", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("29. Total payments and credits")
    with col2:
        value = form_data.get("line_29", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_29", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_29", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("30. Amount you owe")
    with col2:
        value = form_data.get("line_30", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_30", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_30", new_value)
    with col3:
        st.caption("$")
    
    col1, col2, col3 = st.columns([0.3, 0.5, 0.2])
    with col1:
        st.write("31. Overpayment")
    with col2:
        value = form_data.get("line_31", {}).get("value", 0)
        new_value = st.number_input("", value=float(value), key="line_31", format="%.2f")
        if new_value != value and on_field_change:
            on_field_change("line_31", new_value)
    with col3:
        st.caption("$")


def render_schedule_c(schedule_c: Dict[str, Any], on_field_change: callable):
    """Render Schedule C section."""
    st.subheader("📋 Schedule C - Cost of Goods Sold")
    
    # Create a more compact layout
    cols = st.columns(2)
    
    for i, (field_key, field_data) in enumerate(schedule_c.items()):
        if isinstance(field_data, dict) and "value" in field_data:
            col = cols[i % 2]
            with col:
                value = field_data.get("value", 0)
                description = field_data.get("description", field_key.replace("_", " ").title())
                
                # Use a more compact layout
                st.write(f"**{description}:**")
                new_value = st.number_input(
                    f"Line {field_key.replace('line_', '')}", 
                    value=float(value), 
                    key=f"schedule_c_{field_key}", 
                    format="%.2f",
                    label_visibility="collapsed"
                )
                
                if new_value != value:
                    on_field_change(f"schedule_c_{field_key}", new_value)


def render_schedule_m1(schedule_m1: Dict[str, Any], on_field_change: callable):
    """Render Schedule M-1 section."""
    st.subheader("📋 Schedule M-1 - Reconciliation of Income (Loss) Per Books With Income (Loss) Per Return")
    
    # Create a more compact layout
    cols = st.columns(2)
    
    for i, (field_key, field_data) in enumerate(schedule_m1.items()):
        if isinstance(field_data, dict) and "value" in field_data:
            col = cols[i % 2]
            with col:
                value = field_data.get("value", 0)
                description = field_data.get("description", field_key.replace("_", " ").title())
                
                # Use a more compact layout
                st.write(f"**{description}:**")
                new_value = st.number_input(
                    f"Line {field_key.replace('line_', '')}", 
                    value=float(value), 
                    key=f"schedule_m1_{field_key}", 
                    format="%.2f",
                    label_visibility="collapsed"
                )
                
                if new_value != value:
                    on_field_change(f"schedule_m1_{field_key}", new_value)


def render_form_summary(drafted_forms: Dict[str, Any]) -> None:
    """
    Render a summary of the drafted forms.
    
    Args:
        drafted_forms: Complete drafted forms data
    """
    st.subheader("📊 Form Summary")
    
    form_1120 = drafted_forms.get("form_1120", {})
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gross_receipts = form_1120.get("line_1a", {}).get("value", 0)
        st.metric("Gross Receipts", f"${gross_receipts:,.0f}")
    
    with col2:
        cogs = form_1120.get("line_4", {}).get("value", 0)
        st.metric("Cost of Goods Sold", f"${cogs:,.0f}")
    
    with col3:
        gross_profit = form_1120.get("line_5", {}).get("value", 0)
        st.metric("Gross Profit", f"${gross_profit:,.0f}")
    
    with col4:
        taxable_income = form_1120.get("line_26", {}).get("value", 0)
        st.metric("Taxable Income", f"${taxable_income:,.0f}")
    
    # COGS ratio
    if gross_receipts and gross_receipts > 0:
        cogs_ratio = cogs / gross_receipts
        st.metric("COGS Ratio", f"{cogs_ratio:.1%}")
    
    # Reasoning
    if "reasoning" in drafted_forms:
        with st.expander("AI Reasoning", expanded=False):
            st.write(drafted_forms["reasoning"])


def render_form_approval_controls() -> Dict[str, Any]:
    """
    Render form approval and override controls.
    
    Returns:
        Dictionary with user actions
    """
    st.subheader("✅ Form Approval")
    
    actions = {}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Approve Form", type="primary"):
            actions["approve"] = True
    
    with col2:
        if st.button("⚠️ Request Changes"):
            actions["request_changes"] = True
    
    with col3:
        if st.button("📤 Export PDF"):
            actions["export"] = True
    
    return actions

