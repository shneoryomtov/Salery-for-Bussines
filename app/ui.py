"""Streamlit UI components and app state management."""

import streamlit as st
from decimal import Decimal
from datetime import datetime
from engine.models import (
    ScenarioInput,
    WorkProfile,
    CalendarSettings,
    TimeOffSettings,
    ContributionSettings,
    ExpenseItem,
    TaxSettings,
)
from engine.calculator import calculate_all
from engine.io_utils import save_scenario, load_scenario, list_saved_scenarios
from engine import solver
from app.formatters import format_currency, format_percentage, format_hours, format_number
import json


def load_config():
    """Load configuration from JSON."""
    try:
        with open("config/settings_2026_israel.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def init_session_state():
    """Initialize Streamlit session state."""
    if "scenario" not in st.session_state:
        st.session_state.scenario = ScenarioInput(
            name="תרחיש חדש",
            work_profile=WorkProfile(
                year=2026,
                workdays_per_week=Decimal("5"),
                weekly_hours=Decimal("40"),
                income_mode="hourly",
                hourly_rate=Decimal("150"),
                months_per_year=Decimal("12"),
            ),
            calendar_settings=CalendarSettings(
                holiday_mode="builtin",
                holiday_days=15,
                erev_holiday_days=5,
                erev_holiday_hours_reduction=Decimal("4"),
            ),
            time_off_settings=TimeOffSettings(
                vacation_days_per_year=14,
                sick_days_per_year=6,
                treat_vacation_as_lost_income=True,
                treat_sick_as_lost_income=True,
            ),
            contribution_settings=ContributionSettings(
                pension_mode="percentage",
                pension_value=Decimal("5"),
                study_fund_mode="percentage",
                study_fund_value=Decimal("2"),
                maximize_study_to_ceiling=True,
            ),
            tax_settings=TaxSettings(
                income_tax_brackets=[
                    {"threshold": 0, "rate": 0.1},
                    {"threshold": 75000, "rate": 0.14},
                    {"threshold": 110000, "rate": 0.205},
                    {"threshold": 170000, "rate": 0.23},
                    {"threshold": 240000, "rate": 0.3},
                    {"threshold": 400000, "rate": 0.35},
                    {"threshold": 640000, "rate": 0.49},
                ],
                national_insurance_brackets=[
                    {"threshold": 0, "rate": 0.0711},
                ],
                health_brackets=[
                    {"threshold": 0, "rate": 0.053},
                ],
                tax_credit_point_value=Decimal("2700"),
                study_fund_ceiling=Decimal("12000"),
                yearly_workday_assumption=260,
            ),
        )
    
    if "result" not in st.session_state:
        st.session_state.result = None
    
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = []


def render_work_profile_section():
    """Render work profile input section."""
    st.subheader("📋 פרופיל עבודה")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.scenario.work_profile.year = st.number_input(
            "שנה",
            value=st.session_state.scenario.work_profile.year,
            min_value=2020,
            max_value=2030,
        )
        
        st.session_state.scenario.work_profile.workdays_per_week = Decimal(
            st.number_input(
                "ימי עבודה בשבוע",
                value=float(st.session_state.scenario.work_profile.workdays_per_week),
                min_value=1.0,
                max_value=6.0,
                step=0.5,
            )
        )
        
        st.session_state.scenario.work_profile.weekly_hours = Decimal(
            st.number_input(
                "שעות עבודה בשבוע",
                value=float(st.session_state.scenario.work_profile.weekly_hours),
                min_value=1.0,
                max_value=60.0,
                step=1.0,
            )
        )
    
    with col2:
        income_mode = st.radio(
            "דרך הכנסה",
            ["hourly", "monthly"],
            format_func=lambda x: "שיעור שעתי" if x == "hourly" else "משכורת חודשית קבועה",
        )
        st.session_state.scenario.work_profile.income_mode = income_mode
        
        if income_mode == "hourly":
            st.session_state.scenario.work_profile.hourly_rate = Decimal(
                st.number_input(
                    "שיעור שעתי (₪)",
                    value=float(st.session_state.scenario.work_profile.hourly_rate or 150),
                    min_value=1.0,
                )
            )
            st.session_state.scenario.work_profile.monthly_gross = None
        else:
            st.session_state.scenario.work_profile.monthly_gross = Decimal(
                st.number_input(
                    "משכורת חודשית (₪)",
                    value=float(st.session_state.scenario.work_profile.monthly_gross or 6000),
                    min_value=1.0,
                )
            )
            st.session_state.scenario.work_profile.hourly_rate = None
        
        st.session_state.scenario.work_profile.months_per_year = Decimal(
            st.number_input(
                "חודשי עבודה בשנה",
                value=float(st.session_state.scenario.work_profile.months_per_year),
                min_value=1.0,
                max_value=12.0,
                step=1.0,
            )
        )


def render_calendar_section():
    """Render calendar and holidays section."""
    st.subheader("📅 חגים וימי עבודה")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.scenario.calendar_settings.holiday_days = st.number_input(
            "ימי חג על ימי עבודה",
            value=st.session_state.scenario.calendar_settings.holiday_days,
            min_value=0,
            max_value=30,
        )
    
    with col2:
        st.session_state.scenario.calendar_settings.erev_holiday_days = st.number_input(
            "ימי ערב חג",
            value=st.session_state.scenario.calendar_settings.erev_holiday_days,
            min_value=0,
            max_value=30,
        )
    
    st.session_state.scenario.calendar_settings.erev_holiday_hours_reduction = Decimal(
        st.slider(
            "שעות עבודה בימי ערב חג",
            min_value=0.0,
            max_value=8.0,
            value=float(st.session_state.scenario.calendar_settings.erev_holiday_hours_reduction),
            step=0.5,
        )
    )


def render_timeoff_section():
    """Render vacation and sick days section."""
    st.subheader("🏖️ חופשה ומחלה")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.scenario.time_off_settings.vacation_days_per_year = st.number_input(
            "ימי חופשה בשנה",
            value=st.session_state.scenario.time_off_settings.vacation_days_per_year,
            min_value=0,
            max_value=60,
        )
    
    with col2:
        st.session_state.scenario.time_off_settings.sick_days_per_year = st.number_input(
            "ימי מחלה בשנה",
            value=st.session_state.scenario.time_off_settings.sick_days_per_year,
            min_value=0,
            max_value=60,
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.scenario.time_off_settings.treat_vacation_as_lost_income = st.checkbox(
            "חופשה מפחיתה הכנסה",
            value=st.session_state.scenario.time_off_settings.treat_vacation_as_lost_income,
        )
    
    with col2:
        st.session_state.scenario.time_off_settings.treat_sick_as_lost_income = st.checkbox(
            "מחלה מפחיתה הכנסה",
            value=st.session_state.scenario.time_off_settings.treat_sick_as_lost_income,
        )


def render_contribution_section():
    """Render pension and study fund section."""
    st.subheader("🏢 פנסיה וקרן השתלמות")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.scenario.contribution_settings.pension_mode = st.selectbox(
            "ויתור פנסיה",
            ["percentage", "fixed_annual", "fixed_monthly"],
            format_func=lambda x: {"percentage": "אחוז", "fixed_annual": "סכום שנתי", "fixed_monthly": "סכום חודשי"}[x],
            key="pension_mode",
        )
        
        if st.session_state.scenario.contribution_settings.pension_mode == "percentage":
            st.session_state.scenario.contribution_settings.pension_value = Decimal(
                st.number_input("אחוז פנסיה (%)", value=float(st.session_state.scenario.contribution_settings.pension_value), min_value=0.0, max_value=20.0, step=0.5)
            )
        else:
            st.session_state.scenario.contribution_settings.pension_value = Decimal(
                st.number_input("סכום פנסיה", value=float(st.session_state.scenario.contribution_settings.pension_value), min_value=0.0, step=100.0)
            )
    
    with col2:
        st.session_state.scenario.contribution_settings.study_fund_mode = st.selectbox(
            "קרן השתלמות",
            ["percentage", "fixed_annual", "fixed_monthly"],
            format_func=lambda x: {"percentage": "אחוז", "fixed_annual": "סכום שנתי", "fixed_monthly": "סכום חודשי"}[x],
            key="study_fund_mode",
        )
        
        if st.session_state.scenario.contribution_settings.study_fund_mode == "percentage":
            st.session_state.scenario.contribution_settings.study_fund_value = Decimal(
                st.number_input("אחוז קרן (%)", value=float(st.session_state.scenario.contribution_settings.study_fund_value), min_value=0.0, max_value=20.0, step=0.5)
            )
        else:
            st.session_state.scenario.contribution_settings.study_fund_value = Decimal(
                st.number_input("סכום קרן", value=float(st.session_state.scenario.contribution_settings.study_fund_value), min_value=0.0, step=100.0)
            )
    
    st.session_state.scenario.contribution_settings.maximize_study_to_ceiling = st.checkbox(
        "הגבל קרן להתאמה",
        value=st.session_state.scenario.contribution_settings.maximize_study_to_ceiling,
    )


def render_expenses_section():
    """Render expenses input section."""
    st.subheader("💰 הוצאות מוכרות")
    
    if "expenses_list" not in st.session_state:
        st.session_state.expenses_list = [exp.__dict__ for exp in st.session_state.scenario.expenses]
    
    if st.button("➕ הוסף הוצאה", key="add_expense"):
        st.session_state.expenses_list.append({
            "name": "",
            "category": "other",
            "amount": 0,
            "frequency": "monthly",
            "tax_recognition_pct": 100,
            "expense_type": "recurring",
        })
    
    for i, exp in enumerate(st.session_state.expenses_list):
        with st.expander(f"הוצאה #{i+1}: {exp.get('name', 'לא קרא שם')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                exp["name"] = st.text_input("שם הוצאה", value=exp.get("name", ""), key=f"exp_name_{i}")
                exp["category"] = st.selectbox(
                    "קטגוריה",
                    ["office", "equipment", "marketing", "travel", "other"],
                    index=0,
                    key=f"exp_cat_{i}",
                )
                exp["amount"] = st.number_input("סכום", value=float(exp.get("amount", 0)), min_value=0.0, key=f"exp_amount_{i}")
            
            with col2:
                exp["frequency"] = st.selectbox(
                    "תדירות",
                    ["monthly", "yearly", "one-time"],
                    format_func=lambda x: {"monthly": "חודשי", "yearly": "שנתי", "one-time": "חד פעמי"}[x],
                    key=f"exp_freq_{i}",
                )
                exp["tax_recognition_pct"] = st.slider(
                    "% הכרה",
                    min_value=0,
                    max_value=100,
                    value=int(exp.get("tax_recognition_pct", 100)),
                    key=f"exp_recog_{i}",
                )
                exp["expense_type"] = st.selectbox(
                    "סוג הוצאה",
                    ["recurring", "depreciation_asset", "leasing"],
                    format_func=lambda x: {"recurring": "קבועה", "depreciation_asset": "נכס בהפחתה", "leasing": "השכרה"}[x],
                    key=f"exp_type_{i}",
                )
            
            if st.button("🗑️ מחק", key=f"del_exp_{i}"):
                st.session_state.expenses_list.pop(i)
                st.rerun()
    
    # Convert expense dicts back to ExpenseItem objects
    st.session_state.scenario.expenses = [
        ExpenseItem(**{k: v for k, v in exp.items() if k in ExpenseItem.__dataclass_fields__})
        for exp in st.session_state.expenses_list
    ]


def render_results(result):
    """Render calculation results."""
    st.subheader("📊 תוצאות החישוב")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("הכנסה ברוטו שנתית", format_currency(result.annual_gross))
    with col2:
        st.metric("הכנסה נטו שנתית", format_currency(result.net_annual))
    with col3:
        st.metric("הכנסה נטו חודשית", format_currency(result.net_monthly))
    with col4:
        st.metric("שיעור ניכויים", format_percentage(result.effective_deduction_rate))
    
    # Detailed breakdown
    st.write("### פירוט מלא")
    
    breakdown_data = []
    for row in result.breakdown_rows:
        breakdown_data.append({
            "תיאור": row["description"],
            "סכום": format_currency(row["amount"]) if isinstance(row["amount"], (Decimal, float, int)) else row["amount"],
        })
    
    st.table(breakdown_data)
    
    # Explanations
    with st.expander("📖 הסברים נוסחאות"):
        for step in result.explain_steps:
            st.write(f"**{step.label}**: {step.formula}")
            st.write(f"*= {step.value}*")
            st.divider()
