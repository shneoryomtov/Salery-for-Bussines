"""Typed models for the salary calculator engine."""

from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal


@dataclass
class ExpenseItem:
    """Represents a single expense/cost item."""
    name: str
    category: str
    amount: Decimal
    frequency: str  # "monthly", "yearly", "one-time"
    tax_recognition_pct: Decimal = Decimal("100")
    vat_recognition_pct: Decimal = Decimal("0")
    expense_type: str = "recurring"  # "recurring", "depreciation_asset", "leasing"
    
    # For depreciation assets:
    purchase_price: Optional[Decimal] = None
    purchase_date: Optional[str] = None  # "YYYY-MM-DD"
    depreciation_years: Optional[int] = None
    depreciation_rate_pct: Optional[Decimal] = None
    
    # For leasing/payments:
    monthly_payment: Optional[Decimal] = None
    start_month: Optional[int] = None  # 1-12
    end_month: Optional[int] = None    # 1-12
    
    notes: str = ""


@dataclass
class ContributionSettings:
    """Pension and study fund contribution settings."""
    pension_mode: str  # "percentage", "fixed_annual", "fixed_monthly"
    pension_value: Decimal = Decimal("0")
    
    study_fund_mode: str = "percentage"  # "percentage", "fixed_annual", "fixed_monthly"
    study_fund_value: Decimal = Decimal("0")
    
    maximize_study_to_ceiling: bool = False
    include_in_tax_deductions: bool = True


@dataclass
class WorkProfile:
    """User's work profile settings."""
    year: int
    workdays_per_week: Decimal
    weekly_hours: Decimal
    income_mode: str  # "hourly" or "monthly"
    hourly_rate: Optional[Decimal] = None
    monthly_gross: Optional[Decimal] = None
    months_per_year: Decimal = Decimal("12")


@dataclass
class CalendarSettings:
    """Holiday and calendar settings."""
    holiday_mode: str  # "builtin" or "manual"
    holiday_days: int = 0  # days that fall on workdays
    erev_holiday_days: int = 0
    erev_holiday_hours_reduction: Decimal = Decimal("0")


@dataclass
class TimeOffSettings:
    """Vacation and sick day settings."""
    vacation_days_per_year: int = 0
    sick_days_per_year: int = 0
    treat_vacation_as_lost_income: bool = True
    treat_sick_as_lost_income: bool = True
    show_reserve_needed: bool = True


@dataclass
class TaxSettings:
    """Tax calculation settings."""
    income_tax_brackets: List[dict] = field(default_factory=list)  # [{"threshold": 0, "rate": 0.1}, ...]
    national_insurance_brackets: List[dict] = field(default_factory=list)
    health_brackets: List[dict] = field(default_factory=list)
    tax_credit_point_value: Decimal = Decimal("0")
    number_of_tax_credit_points: Decimal = Decimal("0")
    study_fund_ceiling: Decimal = Decimal("0")
    pension_contribution_deductible: bool = True
    yearly_workday_assumption: int = 260  # typical Israeli assumption


@dataclass
class ScenarioInput:
    """Complete input scenario for calculations."""
    name: str = "Untitled Scenario"
    work_profile: WorkProfile = field(default_factory=WorkProfile)
    calendar_settings: CalendarSettings = field(default_factory=CalendarSettings)
    time_off_settings: TimeOffSettings = field(default_factory=TimeOffSettings)
    contribution_settings: ContributionSettings = field(default_factory=ContributionSettings)
    expenses: List[ExpenseItem] = field(default_factory=list)
    tax_settings: TaxSettings = field(default_factory=TaxSettings)


@dataclass
class ExplainStep:
    """Single step in calculation explanation."""
    label: str
    formula: str
    value: str


@dataclass
class ExpenseBreakdown:
    """Expense calculation results."""
    total_annual: Decimal
    recognized_annual: Decimal
    by_category: dict = field(default_factory=dict)
    depreciation_details: List[dict] = field(default_factory=list)


@dataclass
class TaxCalculationResult:
    """Result of tax bracket calculation."""
    total: Decimal
    details: List[dict] = field(default_factory=list)  # Per-bracket details


@dataclass
class CalculationResults:
    """Complete calculation results."""
    # Work hours
    daily_hours: Decimal
    effective_workdays_per_year: int
    effective_work_hours_per_year: Decimal
    
    # Gross income
    annual_gross: Decimal
    monthly_gross_equivalent: Decimal
    
    # Time off impacts
    holiday_lost_hours: Decimal
    erev_holiday_lost_hours: Decimal
    vacation_lost_hours: Decimal
    sick_lost_hours: Decimal
    total_lost_hours: Decimal
    
    # Expenses
    expenses_breakdown: ExpenseBreakdown
    
    # Contributions
    pension_annual: Decimal
    study_fund_annual: Decimal
    pension_recognized: Decimal
    study_fund_recognized: Decimal
    
    # Taxable income
    gross_after_time_adjustment: Decimal
    taxable_income: Decimal
    
    # Taxes
    income_tax: TaxCalculationResult
    national_insurance: TaxCalculationResult
    health_payment: TaxCalculationResult
    
    # Reserves
    monthly_reserve_vacation_sick: Decimal
    
    # Net income
    net_annual: Decimal
    net_monthly: Decimal
    
    # Derived metrics
    effective_deduction_rate: Decimal
    
    # Explanations
    explain_steps: List[ExplainStep] = field(default_factory=list)
    
    # Breakdown table rows
    breakdown_rows: List[dict] = field(default_factory=list)


@dataclass
class SolverResult:
    """Result from target net solver."""
    required_gross_annual: Decimal
    required_gross_monthly: Decimal
    resulting_net_annual: Decimal
    resulting_net_monthly: Decimal
    iterations: int
