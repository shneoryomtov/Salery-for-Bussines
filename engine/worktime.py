"""Workday and working hours calculation engine."""

from decimal import Decimal
from .models import WorkProfile, CalendarSettings, TimeOffSettings, TaxSettings


def calculate_daily_hours(weekly_hours: Decimal, workdays_per_week: Decimal) -> Decimal:
    """
    Calculate hours per workday.
    
    Formula: daily_hours = weekly_hours / workdays_per_week
    """
    if workdays_per_week <= 0:
        return Decimal("0")
    return weekly_hours / workdays_per_week


def calculate_potential_workdays(
    yearly_workday_assumption: int,
    holiday_days: int,
    erev_holiday_days: int = 0,
) -> int:
    """
    Calculate workdays available after removing holidays.
    
    Formula: potential_workdays = yearly_assumption - holiday_days - erev_holiday_days
    """
    total_removed = holiday_days + erev_holiday_days
    workdays = yearly_workday_assumption - total_removed
    return max(0, workdays)


def calculate_workdays_after_timeoff(
    potential_workdays: int,
    vacation_days: int,
    sick_days: int,
    treat_vacation_as_lost: bool,
    treat_sick_as_lost: bool,
) -> int:
    """
    Calculate workdays after removing vacation and sick days.
    
    Formula: workdays_after_timeoff = potential_workdays - (vacation if enabled) - (sick if enabled)
    """
    removed = 0
    if treat_vacation_as_lost:
        removed += vacation_days
    if treat_sick_as_lost:
        removed += sick_days
    
    final_workdays = potential_workdays - removed
    return max(0, final_workdays)


def calculate_lost_hours(
    daily_hours: Decimal,
    holiday_days: int,
    erev_holiday_days: int,
    erev_holiday_hours_reduction: Decimal,
    vacation_days: int,
    vacation_treat_as_lost: bool,
    sick_days: int,
    sick_treat_as_lost: bool,
) -> dict:
    """
    Calculate all lost hours from various sources.
    
    Returns dict with breakdown of lost hours.
    """
    holiday_lost = Decimal(holiday_days) * daily_hours
    erev_lost = Decimal(erev_holiday_days) * erev_holiday_hours_reduction
    
    vacation_lost = Decimal("0")
    if vacation_treat_as_lost:
        vacation_lost = Decimal(vacation_days) * daily_hours
    
    sick_lost = Decimal("0")
    if sick_treat_as_lost:
        sick_lost = Decimal(sick_days) * daily_hours
    
    total_lost = holiday_lost + erev_lost + vacation_lost + sick_lost
    
    return {
        "holiday_lost_hours": holiday_lost,
        "erev_holiday_lost_hours": erev_lost,
        "vacation_lost_hours": vacation_lost,
        "sick_lost_hours": sick_lost,
        "total_lost_hours": total_lost,
    }


def calculate_effective_work_hours(
    potential_hours: Decimal,
    total_lost_hours: Decimal,
) -> Decimal:
    """
    Calculate billable/effective work hours.
    
    Formula: effective_hours = potential_hours - total_lost_hours
    """
    effective = potential_hours - total_lost_hours
    return max(Decimal("0"), effective)


def calculate_monthly_reserve_vacation_sick(
    daily_hours: Decimal,
    vacation_days: int,
    sick_days: int,
    hourly_rate: Decimal,
) -> Decimal:
    """
    Calculate recommended monthly reserve for vacation and sick days.
    
    Formula: monthly_reserve = (vacation_days + sick_days) * daily_hours * hourly_rate / 12
    """
    total_reserve_hours = Decimal(vacation_days + sick_days) * daily_hours
    total_reserve_amount = total_reserve_hours * hourly_rate
    monthly_reserve = total_reserve_amount / Decimal("12")
    return monthly_reserve
