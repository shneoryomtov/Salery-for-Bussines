"""Tax calculation engine."""

from decimal import Decimal
from typing import List, Tuple
from .models import TaxCalculationResult


def calculate_progressive_tax(
    taxable_income: Decimal,
    brackets: List[dict],
) -> TaxCalculationResult:
    """
    Calculate tax using progressive brackets.
    
    Brackets format: [{"threshold": 0, "rate": 0.1}, {"threshold": 50000, "rate": 0.2}, ...]
    """
    if not brackets or taxable_income <= 0:
        return TaxCalculationResult(total=Decimal("0"), details=[])
    
    # Sort brackets by threshold
    sorted_brackets = sorted(brackets, key=lambda x: x.get("threshold", 0))
    
    total_tax = Decimal("0")
    details = []
    
    for i, bracket in enumerate(sorted_brackets):
        threshold = Decimal(str(bracket.get("threshold", 0)))
        rate = Decimal(str(bracket.get("rate", 0)))
        
        # Determine ceiling of this bracket
        if i + 1 < len(sorted_brackets):
            next_threshold = Decimal(str(sorted_brackets[i + 1].get("threshold", 0)))
            ceiling = next_threshold
        else:
            ceiling = None
        
        if taxable_income < threshold:
            break
        
        lower_bound = max(threshold, Decimal("0"))
        
        if ceiling is not None:
            upper_bound = min(taxable_income, ceiling)
        else:
            upper_bound = taxable_income
        
        if upper_bound > lower_bound:
            bracket_income = upper_bound - lower_bound
            bracket_tax = bracket_income * rate
            total_tax += bracket_tax
            
            details.append({
                "threshold": float(threshold),
                "rate": float(rate),
                "income_in_bracket": float(bracket_income),
                "tax_in_bracket": float(bracket_tax),
            })
    
    return TaxCalculationResult(total=total_tax, details=details)


def apply_tax_credits(
    tax_before_credits: Decimal,
    credit_point_value: Decimal,
    number_of_credits: Decimal,
) -> Decimal:
    """
    Reduce tax by credit points.
    
    Formula: tax_after_credits = max(0, tax_before_credits - credit_points * point_value)
    """
    total_credits = credit_point_value * number_of_credits
    tax_after = tax_before_credits - total_credits
    return max(Decimal("0"), tax_after)


def calculate_national_insurance_and_health(
    taxable_income: Decimal,
    ni_brackets: List[dict],
    health_brackets: List[dict],
) -> Tuple[TaxCalculationResult, TaxCalculationResult]:
    """
    Calculate national insurance and health payments using progressive brackets.
    """
    ni_result = calculate_progressive_tax(taxable_income, ni_brackets)
    health_result = calculate_progressive_tax(taxable_income, health_brackets)
    
    return ni_result, health_result
