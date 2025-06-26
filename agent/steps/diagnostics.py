"""
Diagnostics step for identifying potential issues in drafted tax forms.
"""

from typing import Dict, Any, List
from agent.workflow import BaseStep
from services.provenance import get_provenance_tracker


class Diagnostics(BaseStep):
    """Step for running diagnostics on drafted forms."""
    
    def __init__(self):
        """Initialize Diagnostics step."""
        super().__init__(
            name="Diagnostics",
            description="Run rule-based diagnostics to identify potential issues and anomalies"
        )
        self.provenance_tracker = get_provenance_tracker()
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute diagnostics on drafted forms.
        
        Args:
            context: Workflow context containing drafted forms
            
        Returns:
            Updated context with diagnostic results
        """
        drafted_forms = context.get("drafted_forms", {})
        if not drafted_forms:
            # If no drafted forms, create a minimal diagnostic result
            context["diagnostics"] = {
                "issues": [{
                    "type": "no_forms",
                    "severity": "info",
                    "title": "No Forms Available",
                    "description": "No forms were drafted for diagnostics",
                    "field": "general",
                    "value": None
                }],
                "total_issues": 1,
                "critical_issues": 0,
                "warnings": 0,
                "info": 1
            }
            return context
        
        form_1120 = drafted_forms.get("form_1120", {})
        schedule_c = drafted_forms.get("schedule_c", {})
        schedule_m1 = drafted_forms.get("schedule_m1", {})
        
        # Run diagnostic checks
        issues = []
        
        # Check 1: COGS ratio
        cogs_issue = self._check_cogs_ratio(form_1120)
        if cogs_issue:
            issues.append(cogs_issue)
        
        # Check 2: Mathematical consistency
        math_issues = self._check_mathematical_consistency(form_1120)
        issues.extend(math_issues)
        
        # Check 3: Missing critical fields
        missing_issues = self._check_missing_fields(form_1120)
        issues.extend(missing_issues)
        
        # Check 4: Unusual values
        unusual_issues = self._check_unusual_values(form_1120)
        issues.extend(unusual_issues)
        
        # Check 5: Schedule consistency
        schedule_issues = self._check_schedule_consistency(form_1120, schedule_c, schedule_m1)
        issues.extend(schedule_issues)
        
        # Update context
        context["diagnostics"] = {
            "issues": issues,
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
            "warnings": len([i for i in issues if i["severity"] == "warning"]),
            "info": len([i for i in issues if i["severity"] == "info"])
        }
        
        # Track diagnostic provenance
        self.provenance_tracker.add_record(
            step=self.name,
            field="diagnostic_summary",
            value=f"Found {len(issues)} issues",
            source_ref="diagnostic_step",
            confidence=0.95,
            metadata={
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i["severity"] == "critical"]),
                "warnings": len([i for i in issues if i["severity"] == "warning"]),
                "info": len([i for i in issues if i["severity"] == "info"])
            }
        )
        
        return context
    
    def _check_cogs_ratio(self, form_1120: Dict[str, Any]) -> Dict[str, Any]:
        """Check if COGS ratio is unusually high."""
        gross_receipts = self._get_line_value(form_1120, "line_1a")
        cogs = self._get_line_value(form_1120, "line_4")
        
        if gross_receipts and cogs and gross_receipts > 0:
            cogs_ratio = cogs / gross_receipts
            if cogs_ratio > 0.8:
                return {
                    "type": "high_cogs_ratio",
                    "severity": "warning",
                    "title": "High Cost of Goods Sold Ratio",
                    "description": f"COGS ratio is {cogs_ratio:.1%}, which is unusually high. Typical ratios are 60-70%.",
                    "field": "line_4",
                    "value": cogs,
                    "threshold": 0.8,
                    "actual_ratio": cogs_ratio
                }
        return None
    
    def _check_mathematical_consistency(self, form_1120: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check mathematical consistency of form calculations."""
        issues = []
        
        # Check: Line 3 = Line 1a - Line 2
        line_1a = self._get_line_value(form_1120, "line_1a")
        line_2 = self._get_line_value(form_1120, "line_2")
        line_3 = self._get_line_value(form_1120, "line_3")
        
        if all(v is not None for v in [line_1a, line_2, line_3]):
            expected_line_3 = line_1a - line_2
            if abs(line_3 - expected_line_3) > 1:  # Allow for rounding
                issues.append({
                    "type": "math_error",
                    "severity": "critical",
                    "title": "Mathematical Error in Net Receipts",
                    "description": f"Line 3 should equal Line 1a - Line 2. Expected: {expected_line_3}, Found: {line_3}",
                    "field": "line_3",
                    "value": line_3,
                    "expected": expected_line_3
                })
        
        # Check: Line 5 = Line 3 - Line 4
        line_4 = self._get_line_value(form_1120, "line_4")
        line_5 = self._get_line_value(form_1120, "line_5")
        
        if all(v is not None for v in [line_3, line_4, line_5]):
            expected_line_5 = line_3 - line_4
            if abs(line_5 - expected_line_5) > 1:
                issues.append({
                    "type": "math_error",
                    "severity": "critical",
                    "title": "Mathematical Error in Gross Profit",
                    "description": f"Line 5 should equal Line 3 - Line 4. Expected: {expected_line_5}, Found: {line_5}",
                    "field": "line_5",
                    "value": line_5,
                    "expected": expected_line_5
                })
        
        return issues
    
    def _check_missing_fields(self, form_1120: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for missing critical fields."""
        issues = []
        critical_fields = ["line_1a", "line_4", "line_26"]  # Gross receipts, COGS, Taxable income
        
        for field in critical_fields:
            if not self._get_line_value(form_1120, field):
                issues.append({
                    "type": "missing_field",
                    "severity": "critical",
                    "title": f"Missing Critical Field: {field}",
                    "description": f"Critical field {field} is missing or zero",
                    "field": field,
                    "value": None
                })
        
        return issues
    
    def _check_unusual_values(self, form_1120: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for unusual or suspicious values."""
        issues = []
        
        # Check for negative values where they shouldn't be
        positive_fields = ["line_1a", "line_4", "line_26"]
        for field in positive_fields:
            value = self._get_line_value(form_1120, field)
            if value is not None and value < 0:
                issues.append({
                    "type": "negative_value",
                    "severity": "warning",
                    "title": f"Negative Value in {field}",
                    "description": f"Field {field} has a negative value: {value}",
                    "field": field,
                    "value": value
                })
        
        # Check for unusually large values
        gross_receipts = self._get_line_value(form_1120, "line_1a")
        if gross_receipts and gross_receipts > 1000000000:  # $1 billion
            issues.append({
                "type": "large_value",
                "severity": "info",
                "title": "Unusually Large Gross Receipts",
                "description": f"Gross receipts of ${gross_receipts:,.0f} may need verification",
                "field": "line_1a",
                "value": gross_receipts
            })
        
        return issues
    
    def _check_schedule_consistency(self, form_1120: Dict[str, Any], schedule_c: Dict[str, Any], schedule_m1: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check consistency between main form and schedules."""
        issues = []
        
        # Check Schedule C consistency with main form
        if schedule_c:
            form_line_1a = self._get_line_value(form_1120, "line_1a")
            schedule_line_1 = self._get_line_value(schedule_c, "line_1")
            
            if form_line_1a is not None and schedule_line_1 is not None:
                if abs(form_line_1a - schedule_line_1) > 1:
                    issues.append({
                        "type": "schedule_inconsistency",
                        "severity": "warning",
                        "title": "Schedule C Inconsistency",
                        "description": f"Form 1120 Line 1a ({form_line_1a}) doesn't match Schedule C Line 1 ({schedule_line_1})",
                        "field": "schedule_c_line_1",
                        "value": schedule_line_1,
                        "expected": form_line_1a
                    })
        
        return issues
    
    def _get_line_value(self, form_data: Dict[str, Any], line_key: str) -> float:
        """Extract numeric value from form line data."""
        line_data = form_data.get(line_key, {})
        if isinstance(line_data, dict) and "value" in line_data:
            try:
                return float(line_data["value"])
            except (ValueError, TypeError):
                return None
        return None

