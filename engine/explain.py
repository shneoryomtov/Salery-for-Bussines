"""Explanation generation for calculations."""

from decimal import Decimal
from .models import ExplainStep


def format_number(value):
    """Format a number for display."""
    if isinstance(value, Decimal):
        value = float(value)
    return f"{value:,.2f}"


def create_explain_steps(calculation_dict: dict) -> list:
    """
    Generate explanation steps from calculation results.
    """
    steps = []
    
    if "daily_hours" in calculation_dict:
        steps.append(ExplainStep(
            label="שעות עבודה יומיות",
            formula="שעות שבועיות / ימי עבודה בשבוע",
            value=format_number(calculation_dict["daily_hours"]),
        ))
    
    if "effective_workdays_per_year" in calculation_dict:
        steps.append(ExplainStep(
            label="ימי עבודה יעילים בשנה",
            formula="ימי עבודה בשנה - חגים - חופשה - מחלה",
            value=str(calculation_dict["effective_workdays_per_year"]),
        ))
    
    if "effective_work_hours_per_year" in calculation_dict:
        steps.append(ExplainStep(
            label="שעות עבודה יעילות בשנה",
            formula="ימים יעילים × שעות יומיות",
            value=format_number(calculation_dict["effective_work_hours_per_year"]),
        ))
    
    if "annual_gross" in calculation_dict:
        steps.append(ExplainStep(
            label="הכנסה ברוטו שנתית",
            formula="שיעור שעתי × שעות יעילות (או חודשי × חודשים)",
            value=format_number(calculation_dict["annual_gross"]),
        ))
    
    if "expenses_recognized" in calculation_dict:
        steps.append(ExplainStep(
            label="הוצאות מוכרות",
            formula="סכום הוצאות × אחוזי הכרה",
            value=format_number(calculation_dict["expenses_recognized"]),
        ))
    
    if "taxable_income" in calculation_dict:
        steps.append(ExplainStep(
            label="הכנסה חייבת",
            formula="ברוטו - הוצאות מוכרות - ניכויים (פנסיה וקרן)",
            value=format_number(calculation_dict["taxable_income"]),
        ))
    
    if "income_tax_total" in calculation_dict:
        steps.append(ExplainStep(
            label="מס הכנסה",
            formula="בהתאם לסוגריים מס פרוגרסיבי",
            value=format_number(calculation_dict["income_tax_total"]),
        ))
    
    if "ni_and_health_total" in calculation_dict:
        steps.append(ExplainStep(
            label="ביטוח לאומי ובריאות",
            formula="בהתאם לסוגריים",
            value=format_number(calculation_dict["ni_and_health_total"]),
        ))
    
    if "net_annual" in calculation_dict:
        steps.append(ExplainStep(
            label="הכנסה נטו שנתית",
            formula="ברוטו - הוצאות בפועל - מסים - ביטוח לאומי",
            value=format_number(calculation_dict["net_annual"]),
        ))
    
    return steps


def create_breakdown_table_rows(calculation_dict: dict) -> list:
    """
    Create detailed breakdown table rows.
    """
    rows = []
    
    if "annual_gross" in calculation_dict:
        rows.append({
            "stage": 0,
            "description": "הכנסה ברוטו שנתית",
            "amount": calculation_dict["annual_gross"],
        })
    
    if "total_lost_hours" in calculation_dict and calculation_dict["total_lost_hours"] > 0:
        lost_amount = calculation_dict.get("lost_income_amount", Decimal("0"))
        if lost_amount > 0:
            rows.append({
                "stage": 1,
                "description": "בניכוי: הכנסה אבודה (חופשה/מחלה/חגים)",
                "amount": f"({lost_amount})",
            })
            rows.append({
                "stage": 1.5,
                "description": "הכנסה ברוטו לאחר השפעת ימים",
                "amount": calculation_dict.get("gross_after_time_adjustment", calculation_dict["annual_gross"]),
            })
    
    if "expenses_recognized" in calculation_dict and calculation_dict["expenses_recognized"] > 0:
        rows.append({
            "stage": 2,
            "description": "בניכוי: הוצאות מוכרות",
            "amount": f"({calculation_dict['expenses_recognized']})",
        })
    
    total_deductions = Decimal("0")
    if "pension_recognized" in calculation_dict:
        total_deductions += calculation_dict["pension_recognized"]
    if "study_fund_recognized" in calculation_dict:
        total_deductions += calculation_dict["study_fund_recognized"]
    
    if total_deductions > 0:
        rows.append({
            "stage": 3,
            "description": "בניכוי: פנסיה וקרן השתלמות מוכרות",
            "amount": f"({total_deductions})",
        })
    
    if "taxable_income" in calculation_dict:
        rows.append({
            "stage": 4,
            "description": "הכנסה חייבת (בעבור חישוב מס)",
            "amount": calculation_dict["taxable_income"],
        })
    
    if "income_tax_total" in calculation_dict and calculation_dict["income_tax_total"] > 0:
        rows.append({
            "stage": 5,
            "description": "בניכוי: מס הכנסה",
            "amount": f"({calculation_dict['income_tax_total']})",
        })
    
    if "ni_and_health_total" in calculation_dict and calculation_dict["ni_and_health_total"] > 0:
        rows.append({
            "stage": 6,
            "description": "בניכוי: ביטוח לאומי וביטוח בריאות",
            "amount": f"({calculation_dict['ni_and_health_total']})",
        })
    
    if "net_annual" in calculation_dict:
        rows.append({
            "stage": 7,
            "description": "=== הכנסה נטו שנתית ===",
            "amount": calculation_dict["net_annual"],
        })
    
    return rows
