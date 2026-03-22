"""Pension and study fund contribution calculations."""

from decimal import Decimal
from .models import ContributionSettings


def calculate_pension_contribution(
    settings: ContributionSettings,
    gross_annual: Decimal,
) -> tuple[Decimal, Decimal]:
    """
    Calculate annual pension contribution.
    
    Returns:
        (annual_amount, recognized_deduction_amount)
    """
    if settings.pension_mode == "percentage":
        annual = gross_annual * (settings.pension_value / Decimal("100"))
    elif settings.pension_mode == "fixed_annual":
        annual = settings.pension_value
    elif settings.pension_mode == "fixed_monthly":
        annual = settings.pension_value * Decimal("12")
    else:
        annual = Decimal("0")
    
    recognized = annual if settings.include_in_tax_deductions else Decimal("0")
    
    return annual, recognized


def calculate_study_fund_contribution(
    settings: ContributionSettings,
    gross_annual: Decimal,
    study_fund_ceiling: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    """
    Calculate annual study fund contribution.
    
    Returns:
        (annual_amount, recognized_deduction, non_recognized_amount)
    """
    if settings.study_fund_mode == "percentage":
        calculated = gross_annual * (settings.study_fund_value / Decimal("100"))
    elif settings.study_fund_mode == "fixed_annual":
        calculated = settings.study_fund_value
    elif settings.study_fund_mode == "fixed_monthly":
        calculated = settings.study_fund_value * Decimal("12")
    else:
        calculated = Decimal("0")
    
    # Apply ceiling if enabled
    if settings.maximize_study_to_ceiling and study_fund_ceiling > 0:
        annual = min(calculated, study_fund_ceiling)
    else:
        annual = calculated
    
    recognized = annual if settings.include_in_tax_deductions else Decimal("0")
    non_recognized = calculated - annual
    
    return annual, recognized, non_recognized


def calculate_total_contribution_deductions(
    pension_recognized: Decimal,
    study_fund_recognized: Decimal,
) -> Decimal:
    """
    Calculate total recognized contributions for tax purposes.
    
    Formula: total_deduction = pension_recognized + study_fund_recognized
    """
    return pension_recognized + study_fund_recognized
