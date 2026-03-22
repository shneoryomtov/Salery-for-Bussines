"""Expense calculation engine."""

from decimal import Decimal
from typing import List, Tuple
from datetime import datetime
from .models import ExpenseItem, ExpenseBreakdown


def annualize_expense(expense: ExpenseItem, year: int) -> Decimal:
    """
    Convert expense to annual amount based on frequency.
    
    Handles special cases like depreciation assets and leasing with time restrictions.
    """
    if expense.expense_type == "depreciation_asset":
        return calculate_depn_annual(expense, year)
    elif expense.expense_type == "leasing":
        return calculate_leasing_annual(expense, year)
    else:  # recurring
        if expense.frequency == "monthly":
            return expense.amount * Decimal("12")
        elif expense.frequency == "yearly":
            return expense.amount
        elif expense.frequency == "one-time":
            return expense.amount
        else:
            return Decimal("0")


def calculate_depn_annual(expense: ExpenseItem, year: int) -> Decimal:
    """
    Calculate annual depreciation for an asset.
    
    Uses straight-line depreciation.
    Only counts months within the year if purchase_date is provided.
    """
    if expense.purchase_price is None:
        return Decimal("0")
    
    if expense.depreciation_rate_pct is not None:
        # Use rate percentage
        annual_depn = expense.purchase_price * (expense.depreciation_rate_pct / Decimal("100"))
    elif expense.depreciation_years is not None and expense.depreciation_years > 0:
        # Use years of depreciation
        annual_depn = expense.purchase_price / Decimal(expense.depreciation_years)
    else:
        return Decimal("0")
    
    # If purchase_date provided, calculate months active in year
    if expense.purchase_date:
        try:
            purchase_date = datetime.strptime(expense.purchase_date, "%Y-%m-%d")
            purchase_year = purchase_date.year
            purchase_month = purchase_date.month
            
            if purchase_year > year:
                return Decimal("0")  # Not yet purchased
            elif purchase_year == year:
                # Only count from purchase month onwards
                months_active = 13 - purchase_month
                annual_depn = annual_depn * Decimal(months_active) / Decimal("12")
        except (ValueError, AttributeError):
            pass  # Invalid date, use full year
    
    return annual_depn


def calculate_leasing_annual(expense: ExpenseItem, year: int) -> Decimal:
    """
    Calculate annual leasing payment, considering active months in year.
    """
    if expense.monthly_payment is None:
        return Decimal("0")
    
    months_active = 12
    
    # If start/end month provided, calculate active months
    if expense.start_month is not None and expense.end_month is not None:
        if expense.end_month < expense.start_month:
            # Spans calendar year boundary - simplified, use 12
            months_active = 12
        else:
            months_active = expense.end_month - expense.start_month + 1
    
    return expense.monthly_payment * Decimal(months_active)


def calculate_recognized_expense(
    annual_amount: Decimal,
    tax_recognition_pct: Decimal,
) -> Decimal:
    """
    Apply tax recognition percentage to expense amount.
    
    Formula: recognized = annual_amount * (recognition_pct / 100)
    """
    if tax_recognition_pct < 0:
        tax_recognition_pct = Decimal("0")
    if tax_recognition_pct > 100:
        tax_recognition_pct = Decimal("100")
    
    return annual_amount * (tax_recognition_pct / Decimal("100"))


def breakdown_expenses(
    expenses: List[ExpenseItem],
    year: int,
) -> Tuple[ExpenseBreakdown, List[dict]]:
    """
    Calculate complete expense breakdown.
    
    Returns:
        - ExpenseBreakdown object with totals
        - List of detail rows for display
    """
    total_annual = Decimal("0")
    total_recognized = Decimal("0")
    by_category = {}
    depreciation_details = []
    detail_rows = []
    
    for expense in expenses:
        annual = annualize_expense(expense, year)
        recognized = calculate_recognized_expense(annual, expense.tax_recognition_pct)
        
        total_annual += annual
        total_recognized += recognized
        
        # Aggregate by category
        if expense.category not in by_category:
            by_category[expense.category] = {
                "annual": Decimal("0"),
                "recognized": Decimal("0"),
            }
        by_category[expense.category]["annual"] += annual
        by_category[expense.category]["recognized"] += recognized
        
        # Track depreciation details
        if expense.expense_type == "depreciation_asset":
            depreciation_details.append({
                "name": expense.name,
                "purchase_price": expense.purchase_price,
                "annual_depreciation": annual,
                "depreciation_years": expense.depreciation_years,
            })
        
        # Add to detail rows
        detail_rows.append({
            "name": expense.name,
            "category": expense.category,
            "frequency": expense.frequency,
            "annual_amount": annual,
            "recognition_pct": expense.tax_recognition_pct,
            "recognized_amount": recognized,
        })
    
    breakdown = ExpenseBreakdown(
        total_annual=total_annual,
        recognized_annual=total_recognized,
        by_category=by_category,
        depreciation_details=depreciation_details,
    )
    
    return breakdown, detail_rows
