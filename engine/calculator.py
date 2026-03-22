"""Main calculation engine."""

from decimal import Decimal
from .models import (
    ScenarioInput,
    CalculationResults,
    ExpenseBreakdown,
)
from . import worktime, expenses, contributions, taxes
from .explain import create_explain_steps, create_breakdown_table_rows


def calculate_all(scenario: ScenarioInput) -> CalculationResults:
    """
    Execute complete calculation pipeline for a scenario.
    """
    work = scenario.work_profile
    calendar = scenario.calendar_settings
    timeoff = scenario.time_off_settings
    contrib = scenario.contribution_settings
    tax_settings = scenario.tax_settings
    
    # === WORKDAY CALCULATIONS ===
    daily_hours = worktime.calculate_daily_hours(work.weekly_hours, work.workdays_per_week)
    
    potential_workdays = worktime.calculate_potential_workdays(
        yearly_workday_assumption=tax_settings.yearly_workday_assumption,
        holiday_days=calendar.holiday_days,
        erev_holiday_days=calendar.erev_holiday_days,
    )
    
    effective_workdays = worktime.calculate_workdays_after_timeoff(
        potential_workdays=potential_workdays,
        vacation_days=timeoff.vacation_days_per_year,
        sick_days=timeoff.sick_days_per_year,
        treat_vacation_as_lost=timeoff.treat_vacation_as_lost_income,
        treat_sick_as_lost=timeoff.treat_sick_as_lost_income,
    )
    
    potential_hours = Decimal(effective_workdays) * daily_hours
    
    lost_hours_dict = worktime.calculate_lost_hours(
        daily_hours=daily_hours,
        holiday_days=calendar.holiday_days,
        erev_holiday_days=calendar.erev_holiday_days,
        erev_holiday_hours_reduction=calendar.erev_holiday_hours_reduction,
        vacation_days=timeoff.vacation_days_per_year,
        vacation_treat_as_lost=timeoff.treat_vacation_as_lost_income,
        sick_days=timeoff.sick_days_per_year,
        sick_treat_as_lost=timeoff.treat_sick_as_lost_income,
    )
    
    total_lost_hours = lost_hours_dict["total_lost_hours"]
    effective_work_hours = worktime.calculate_effective_work_hours(potential_hours, total_lost_hours)
    
    # === GROSS INCOME ===
    if work.income_mode == "hourly" and work.hourly_rate:
        annual_gross = effective_work_hours * work.hourly_rate
        hourly_rate_for_reserve = work.hourly_rate
    elif work.income_mode == "monthly" and work.monthly_gross:
        annual_gross = work.monthly_gross * work.months_per_year
        hourly_rate_for_reserve = annual_gross / effective_work_hours if effective_work_hours > 0 else Decimal("0")
    else:
        annual_gross = Decimal("0")
        hourly_rate_for_reserve = Decimal("0")
    
    monthly_gross_equiv = annual_gross / Decimal("12") if annual_gross > 0 else Decimal("0")
    gross_after_time = annual_gross
    
    # === EXPENSES ===
    expense_breakdown, expense_rows = expenses.breakdown_expenses(scenario.expenses, work.year)
    
    # === CONTRIBUTIONS ===
    pension_annual, pension_recognized = contributions.calculate_pension_contribution(
        contrib, annual_gross
    )
    study_fund_annual, study_fund_recognized, study_fund_non_recog = contributions.calculate_study_fund_contribution(
        contrib, annual_gross, tax_settings.study_fund_ceiling
    )
    
    # === TAXABLE INCOME ===
    total_contribution_deductions = contributions.calculate_total_contribution_deductions(
        pension_recognized, study_fund_recognized
    )
    
    taxable_income = gross_after_time - expense_breakdown.recognized_annual - total_contribution_deductions
    taxable_income = max(Decimal("0"), taxable_income)
    
    # === TAX CALCULATIONS ===
    income_tax_result = taxes.calculate_progressive_tax(taxable_income, tax_settings.income_tax_brackets)
    income_tax_after_credits = taxes.apply_tax_credits(
        income_tax_result.total,
        tax_settings.tax_credit_point_value,
        tax_settings.number_of_tax_credit_points,
    )
    
    ni_result, health_result = taxes.calculate_national_insurance_and_health(
        taxable_income,
        tax_settings.national_insurance_brackets,
        tax_settings.health_brackets,
    )
    
    # === RESERVES ===
    monthly_reserve = worktime.calculate_monthly_reserve_vacation_sick(
        daily_hours=daily_hours,
        vacation_days=timeoff.vacation_days_per_year,
        sick_days=timeoff.sick_days_per_year,
        hourly_rate=hourly_rate_for_reserve,
    ) if hourly_rate_for_reserve > 0 else Decimal("0")
    
    # === NET INCOME ===
    total_taxes_and_ni = income_tax_after_credits + ni_result.total + health_result.total
    net_annual = annual_gross - expense_breakdown.total_annual - total_taxes_and_ni
    net_monthly = net_annual / Decimal("12") if net_annual > 0 else Decimal("0")
    
    # === EFFECTIVE DEDUCTION RATE ===
    if annual_gross > 0:
        total_deductions_value = expense_breakdown.total_annual + total_taxes_and_ni + pension_annual + study_fund_annual
        effective_deduction_rate = (total_deductions_value / annual_gross) * Decimal("100")
    else:
        effective_deduction_rate = Decimal("0")
    
    # === EXPLANATIONS ===
    calc_dict = {
        "daily_hours": daily_hours,
        "effective_workdays_per_year": effective_workdays,
        "effective_work_hours_per_year": effective_work_hours,
        "annual_gross": annual_gross,
        "total_lost_hours": total_lost_hours,
        "expenses_recognized": expense_breakdown.recognized_annual,
        "pension_recognized": pension_recognized,
        "study_fund_recognized": study_fund_recognized,
        "taxable_income": taxable_income,
        "income_tax_total": income_tax_after_credits,
        "ni_and_health_total": ni_result.total + health_result.total,
        "gross_after_time_adjustment": gross_after_time,
        "net_annual": net_annual,
        "lost_income_amount": total_lost_hours * hourly_rate_for_reserve if hourly_rate_for_reserve > 0 else Decimal("0"),
    }
    
    explain_steps = create_explain_steps(calc_dict)
    breakdown_rows = create_breakdown_table_rows(calc_dict)
    
    return CalculationResults(
        daily_hours=daily_hours,
        effective_workdays_per_year=effective_workdays,
        effective_work_hours_per_year=effective_work_hours,
        annual_gross=annual_gross,
        monthly_gross_equivalent=monthly_gross_equiv,
        holiday_lost_hours=lost_hours_dict["holiday_lost_hours"],
        erev_holiday_lost_hours=lost_hours_dict["erev_holiday_lost_hours"],
        vacation_lost_hours=lost_hours_dict["vacation_lost_hours"],
        sick_lost_hours=lost_hours_dict["sick_lost_hours"],
        total_lost_hours=total_lost_hours,
        expenses_breakdown=expense_breakdown,
        pension_annual=pension_annual,
        study_fund_annual=study_fund_annual,
        pension_recognized=pension_recognized,
        study_fund_recognized=study_fund_recognized,
        gross_after_time_adjustment=gross_after_time,
        taxable_income=taxable_income,
        income_tax=income_tax_result,
        national_insurance=ni_result,
        health_payment=health_result,
        monthly_reserve_vacation_sick=monthly_reserve,
        net_annual=net_annual,
        net_monthly=net_monthly,
        effective_deduction_rate=effective_deduction_rate,
        explain_steps=explain_steps,
        breakdown_rows=breakdown_rows,
    )
