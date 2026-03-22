"""JSON I/O utilities for scenarios and results."""

import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from .models import ScenarioInput, CalculationResults


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal objects."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def scenario_to_dict(scenario: ScenarioInput) -> dict:
    """Convert ScenarioInput to dictionary."""
    return {
        "name": scenario.name,
        "work_profile": {
            "year": scenario.work_profile.year,
            "workdays_per_week": float(scenario.work_profile.workdays_per_week),
            "weekly_hours": float(scenario.work_profile.weekly_hours),
            "income_mode": scenario.work_profile.income_mode,
            "hourly_rate": float(scenario.work_profile.hourly_rate) if scenario.work_profile.hourly_rate else None,
            "monthly_gross": float(scenario.work_profile.monthly_gross) if scenario.work_profile.monthly_gross else None,
            "months_per_year": float(scenario.work_profile.months_per_year),
        },
        "calendar_settings": {
            "holiday_mode": scenario.calendar_settings.holiday_mode,
            "holiday_days": scenario.calendar_settings.holiday_days,
            "erev_holiday_days": scenario.calendar_settings.erev_holiday_days,
            "erev_holiday_hours_reduction": float(scenario.calendar_settings.erev_holiday_hours_reduction),
        },
        "time_off_settings": {
            "vacation_days_per_year": scenario.time_off_settings.vacation_days_per_year,
            "sick_days_per_year": scenario.time_off_settings.sick_days_per_year,
            "treat_vacation_as_lost_income": scenario.time_off_settings.treat_vacation_as_lost_income,
            "treat_sick_as_lost_income": scenario.time_off_settings.treat_sick_as_lost_income,
        },
        "contribution_settings": {
            "pension_mode": scenario.contribution_settings.pension_mode,
            "pension_value": float(scenario.contribution_settings.pension_value),
            "study_fund_mode": scenario.contribution_settings.study_fund_mode,
            "study_fund_value": float(scenario.contribution_settings.study_fund_value),
            "maximize_study_to_ceiling": scenario.contribution_settings.maximize_study_to_ceiling,
        },
        "expenses": [
            {
                "name": e.name,
                "category": e.category,
                "amount": float(e.amount),
                "frequency": e.frequency,
                "tax_recognition_pct": float(e.tax_recognition_pct),
                "expense_type": e.expense_type,
            }
            for e in scenario.expenses
        ],
    }


def save_scenario(scenario: ScenarioInput, filepath: str) -> bool:
    """Save scenario to JSON file."""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        scenario_dict = scenario_to_dict(scenario)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(scenario_dict, f, indent=2, cls=DecimalEncoder, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving scenario: {e}")
        return False


def load_scenario(filepath: str) -> ScenarioInput:
    """Load scenario from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ScenarioInput(name=data.get("name", "Loaded"))
    except Exception:
        return ScenarioInput()


def list_saved_scenarios(directory: str = "saved") -> list:
    """List all saved scenario files."""
    path = Path(directory)
    if not path.exists():
        return []
    return sorted([str(f.name) for f in path.glob("*.json")])
