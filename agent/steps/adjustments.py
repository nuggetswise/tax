"""
Adjustments step for suggesting corrections to flagged diagnostic issues.
"""

from typing import Dict, Any, List
from agent.workflow import BaseStep
from services.llm import get_llm_service
from services.provenance import get_provenance_tracker


class Adjustments(BaseStep):
    """Step for suggesting adjustments to flagged issues."""
    
    def __init__(self):
        """Initialize Adjustments step."""
        super().__init__(
            name="Adjustments",
            description="Generate AI-suggested adjustments for flagged diagnostic issues"
        )
        self.llm_service = get_llm_service()
        self.provenance_tracker = get_provenance_tracker()
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute adjustments for flagged issues.
        
        Args:
            context: Workflow context containing diagnostics and drafted forms
            
        Returns:
            Updated context with suggested adjustments
        """
        diagnostics = context.get("diagnostics", {})
        drafted_forms = context.get("drafted_forms", {})
        tax_data = context.get("tax_data", {})
        
        if not diagnostics or not diagnostics.get("issues"):
            # No issues to adjust
            context["adjustments"] = {
                "suggestions": [],
                "total_suggestions": 0,
                "applied_adjustments": []
            }
            return context
        
        issues = diagnostics["issues"]
        suggestions = []
        
        # Generate suggestions for each issue
        for issue in issues:
            if issue["severity"] in ["critical", "warning"]:
                suggestion = self._generate_suggestion(issue, drafted_forms, tax_data)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Update context
        context["adjustments"] = {
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "applied_adjustments": []
        }
        
        # Track adjustment provenance
        self.provenance_tracker.add_record(
            step=self.name,
            field="adjustment_summary",
            value=f"Generated {len(suggestions)} suggestions",
            source_ref="adjustment_step",
            confidence=0.8,
            metadata={
                "total_suggestions": len(suggestions),
                "issues_processed": len(issues),
                "critical_issues": len([i for i in issues if i["severity"] == "critical"])
            }
        )
        
        return context
    
    def _generate_suggestion(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any], tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a suggestion for a specific issue.
        
        Args:
            issue: Diagnostic issue to address
            drafted_forms: Current drafted forms
            tax_data: Original extracted tax data
            
        Returns:
            Suggestion dictionary
        """
        issue_type = issue["type"]
        
        if issue_type == "math_error":
            return self._suggest_math_correction(issue, drafted_forms)
        elif issue_type == "high_cogs_ratio":
            return self._suggest_cogs_adjustment(issue, drafted_forms, tax_data)
        elif issue_type == "missing_field":
            return self._suggest_missing_field(issue, drafted_forms, tax_data)
        elif issue_type == "negative_value":
            return self._suggest_negative_value_correction(issue, drafted_forms)
        elif issue_type == "schedule_inconsistency":
            return self._suggest_schedule_correction(issue, drafted_forms)
        else:
            return self._suggest_generic_adjustment(issue, drafted_forms, tax_data)
    
    def _suggest_math_correction(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest correction for mathematical errors."""
        field = issue["field"]
        current_value = issue["value"]
        expected_value = issue["expected"]
        
        return {
            "issue_id": issue.get("type", "unknown"),
            "field": field,
            "current_value": current_value,
            "suggested_value": expected_value,
            "adjustment_type": "mathematical_correction",
            "description": f"Correct {field} from {current_value} to {expected_value}",
            "reasoning": f"Mathematical calculation error. {issue['description']}",
            "confidence": 0.95,
            "priority": "high"
        }
    
    def _suggest_cogs_adjustment(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any], tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest adjustment for high COGS ratio."""
        current_ratio = issue["actual_ratio"]
        threshold = issue["threshold"]
        
        # Calculate suggested COGS based on typical ratio
        form_1120 = drafted_forms.get("form_1120", {})
        gross_receipts = self._get_line_value(form_1120, "line_1a")
        
        if gross_receipts:
            # Suggest 70% ratio instead of current high ratio
            suggested_cogs = gross_receipts * 0.7
            current_cogs = issue["value"]
            
            return {
                "issue_id": "high_cogs_ratio",
                "field": "line_4",
                "current_value": current_cogs,
                "suggested_value": suggested_cogs,
                "adjustment_type": "ratio_adjustment",
                "description": f"Reduce COGS from ${current_cogs:,.0f} to ${suggested_cogs:,.0f}",
                "reasoning": f"Current COGS ratio of {current_ratio:.1%} is unusually high. Suggesting 70% ratio based on industry standards.",
                "confidence": 0.75,
                "priority": "medium"
            }
        
        return None
    
    def _suggest_missing_field(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any], tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest value for missing critical field."""
        field = issue["field"]
        
        # Map form fields to tax data fields
        field_mapping = {
            "line_1a": "gross_receipts",
            "line_4": "cost_of_goods_sold",
            "line_26": "net_income"
        }
        
        tax_field = field_mapping.get(field)
        if tax_field and tax_data.get(tax_field):
            suggested_value = tax_data[tax_field]
            
            return {
                "issue_id": "missing_field",
                "field": field,
                "current_value": None,
                "suggested_value": suggested_value,
                "adjustment_type": "missing_field_population",
                "description": f"Populate {field} with ${suggested_value:,.0f} from extracted data",
                "reasoning": f"Critical field {field} is missing. Using extracted {tax_field} value.",
                "confidence": 0.8,
                "priority": "high"
            }
        
        return None
    
    def _suggest_negative_value_correction(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest correction for negative values."""
        field = issue["field"]
        current_value = issue["value"]
        
        return {
            "issue_id": "negative_value",
            "field": field,
            "current_value": current_value,
            "suggested_value": abs(current_value),
            "adjustment_type": "negative_value_correction",
            "description": f"Change {field} from {current_value} to {abs(current_value)}",
            "reasoning": f"Field {field} should not be negative. Converting to positive value.",
            "confidence": 0.9,
            "priority": "medium"
        }
    
    def _suggest_schedule_correction(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest correction for schedule inconsistencies."""
        field = issue["field"]
        current_value = issue["value"]
        expected_value = issue["expected"]
        
        return {
            "issue_id": "schedule_inconsistency",
            "field": field,
            "current_value": current_value,
            "suggested_value": expected_value,
            "adjustment_type": "schedule_correction",
            "description": f"Correct {field} to match main form value",
            "reasoning": f"Schedule value should match corresponding main form value for consistency.",
            "confidence": 0.85,
            "priority": "medium"
        }
    
    def _suggest_generic_adjustment(self, issue: Dict[str, Any], drafted_forms: Dict[str, Any], tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic adjustment suggestion using LLM."""
        prompt = f"""
        Analyze this tax form issue and suggest an adjustment:
        
        Issue: {issue['title']}
        Description: {issue['description']}
        Field: {issue.get('field', 'Unknown')}
        Current Value: {issue.get('value', 'Unknown')}
        Severity: {issue['severity']}
        
        Available tax data: {tax_data}
        
        Please suggest a specific adjustment with:
        1. A new value for the field
        2. Reasoning for the adjustment
        3. Confidence level (0-1)
        
        Return as JSON:
        {{
            "suggested_value": number,
            "reasoning": "string",
            "confidence": number
        }}
        """
        
        try:
            response = self.llm_service.chat_json(prompt)
            
            return {
                "issue_id": issue.get("type", "unknown"),
                "field": issue.get("field", "unknown"),
                "current_value": issue.get("value"),
                "suggested_value": response.get("suggested_value"),
                "adjustment_type": "llm_suggestion",
                "description": f"LLM-suggested adjustment for {issue.get('field', 'unknown')}",
                "reasoning": response.get("reasoning", "AI-generated suggestion"),
                "confidence": response.get("confidence", 0.7),
                "priority": "medium"
            }
        except Exception as e:
            return None
    
    def _get_line_value(self, form_data: Dict[str, Any], line_key: str) -> float:
        """Extract numeric value from form line data."""
        line_data = form_data.get(line_key, {})
        if isinstance(line_data, dict) and "value" in line_data:
            try:
                return float(line_data["value"])
            except (ValueError, TypeError):
                return None
        return None

