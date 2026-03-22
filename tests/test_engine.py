"""Unit tests for calculation engine."""

import pytest
from decimal import Decimal
from engine.worktime import (
    calculate_daily_hours,
    calculate_potential_workdays,
    calculate_lost_hours,
    calculate_effective_work_hours,
)
from engine.expenses import annualize_expense, calculate_recognized_expense
from engine.contributions import calculate_pension_contribution
from engine.taxes import calculate_progressive_tax
from engine.models import (
    ExpenseItem,
    ContributionSettings,
    TaxCalculationResult,
)


class TestWorktime:
    """Tests for worktime calculations."""
    
    def test_calculate_daily_hours(self):
        """Test daily hours calculation."""
        result = calculate_daily_hours(Decimal("40"), Decimal("5"))
        assert result == Decimal("8")
    
    def test_calculate_daily_hours_zero_workdays(self):
        """Test daily hours with zero workdays."""
        result = calculate_daily_hours(Decimal("40"), Decimal("0"))
        assert result == Decimal("0")
    
    def test_calculate_potential_workdays(self):
        """Test potential workdays calculation."""
        result = calculate_potential_workdays(
            yearly_workday_assumption=260,
            holiday_days=15,
            erev_holiday_days=5,
        )
        assert result == 240
    
    def test_calculate_lost_hours_holidays(self):
        """Test lost hours from holidays."""
        result = calculate_lost_hours(
            daily_hours=Decimal("8"),
            holiday_days=10,
            erev_holiday_days=0,
            erev_holiday_hours_reduction=Decimal("0"),
            vacation_days=0,
            vacation_treat_as_lost=False,
            sick_days=0,
            sick_treat_as_lost=False,
        )
        assert result["holiday_lost_hours"] == Decimal("80")
        assert result["total_lost_hours"] == Decimal("80")
    
    def test_calculate_effective_work_hours(self):
        """Test effective work hours calculation."""
        potential = Decimal("2080")
        lost = Decimal("80")
        result = calculate_effective_work_hours(potential, lost)
        assert result == Decimal("2000")


class TestExpenses:
    """Tests for expense calculations."""
    
    def test_annualize_monthly_expense(self):
        """Test converting monthly expense to annual."""
        exp = ExpenseItem(
            name="Office Rent",
            category="office",
            amount=Decimal("2000"),
            frequency="monthly",
            tax_recognition_pct=Decimal("100"),
        )
        result = annualize_expense(exp, 2026)
        assert result == Decimal("24000")
    
    def test_annualize_yearly_expense(self):
        """Test annual expense stays the same."""
        exp = ExpenseItem(
            name="Insurance",
            category="other",
            amount=Decimal("12000"),
            frequency="yearly",
            tax_recognition_pct=Decimal("100"),
        )
        result = annualize_expense(exp, 2026)
        assert result == Decimal("12000")
    
    def test_calculate_recognized_expense(self):
        """Test expense recognition percentage."""
        result = calculate_recognized_expense(Decimal("10000"), Decimal("50"))
        assert result == Decimal("5000")
    
    def test_calculate_recognized_expense_full(self):
        """Test full expense recognition."""
        result = calculate_recognized_expense(Decimal("10000"), Decimal("100"))
        assert result == Decimal("10000")


class TestContributions:
    """Tests for contribution calculations."""
    
    def test_pension_percentage_mode(self):
        """Test pension as percentage."""
        settings = ContributionSettings(
            pension_mode="percentage",
            pension_value=Decimal("5"),
            include_in_tax_deductions=True,
        )
        gross = Decimal("100000")
        annual, recognized = calculate_pension_contribution(settings, gross)
        assert annual == Decimal("5000")
        assert recognized == Decimal("5000")
    
    def test_pension_fixed_annual_mode(self):
        """Test pension as fixed annual amount."""
        settings = ContributionSettings(
            pension_mode="fixed_annual",
            pension_value=Decimal("6000"),
            include_in_tax_deductions=True,
        )
        gross = Decimal("100000")
        annual, recognized = calculate_pension_contribution(settings, gross)
        assert annual == Decimal("6000")


class TestTaxes:
    """Tests for tax calculations."""
    
    def test_progressive_tax_single_bracket(self):
        """Test tax with single bracket."""
        brackets = [{"threshold": 0, "rate": 0.1}]
        result = calculate_progressive_tax(Decimal("100000"), brackets)
        assert result.total == Decimal("10000")
    
    def test_progressive_tax_multiple_brackets(self):
        """Test tax with multiple brackets."""
        brackets = [
            {"threshold": 0, "rate": 0.1},
            {"threshold": 50000, "rate": 0.2},
        ]
        result = calculate_progressive_tax(Decimal("100000"), brackets)
        # 50000 * 0.1 + 50000 * 0.2 = 5000 + 10000 = 15000
        assert result.total == Decimal("15000")
    
    def test_progressive_tax_zero_income(self):
        """Test tax with zero income."""
        brackets = [{"threshold": 0, "rate": 0.1}]
        result = calculate_progressive_tax(Decimal("0"), brackets)
        assert result.total == Decimal("0")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
