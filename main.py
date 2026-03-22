"""Main Streamlit application entry point."""

import streamlit as st
from decimal import Decimal
from app.ui import init_session_state, render_work_profile_section, render_calendar_section
from app.ui import render_timeoff_section, render_contribution_section, render_expenses_section
from app.ui import render_results
from engine.calculator import calculate_all
from engine.io_utils import save_scenario, load_scenario, list_saved_scenarios
from engine import solver


# Page configuration
st.set_page_config(
    page_title="מחשבון הכנסה לעצמאים",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    st.title("💰 מחשבון הכנסה לעצמאים בישראל")
    st.markdown("---")
    
    st.write("### תרחישים")
    
    col1, col2 = st.columns(2)
    with col1:
        scenario_name = st.text_input("שם התרחיש", value=st.session_state.scenario.name)
        st.session_state.scenario.name = scenario_name
    
    with col2:
        if st.button("💾 שמור"):
            save_scenario(st.session_state.scenario, f"saved/{scenario_name}.json")
            st.success("שמור בהצלחה!")
    
    st.markdown("---")
    st.write("### תוכן אפליקציה")
    st.info("""
    **מחשבון אישי לתישראל**
    
    כלי לתכנון וניתוח הכנסה עבור עצמאים.
    
    ⚠️ **כללי חשוב**: זהו כלי תכנון בלבד. לא תייעוץ מס רשמי.
    """)


# Main content
st.title("📊 מחשבון הכנסה לעצמאים")
st.write("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["פרופיל עבודה", "הוצאות", "תוצאות", "פתרון יעד", "השוואה"]
)

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### הזנת נתוני עבודה")
        render_work_profile_section()
        st.write("---")
        render_calendar_section()
        st.write("---")
        render_timeoff_section()
        st.write("---")
        render_contribution_section()
    
    with col2:
        st.write("### פעולות")
        if st.button("🧮 חשב תוצאות", use_container_width=True, type="primary"):
            st.session_state.result = calculate_all(st.session_state.scenario)
            st.rerun()

with tab2:
    render_expenses_section()
    
    if st.button("🧮 חשב מחדש", use_container_width=True):
        st.session_state.result = calculate_all(st.session_state.scenario)
        st.rerun()

with tab3:
    if st.session_state.result:
        render_results(st.session_state.result)
    else:
        st.info("חישבו את התוצאות בעמוד ראשון או לחצו חישוב")

with tab4:
    st.write("### חישוב הכנסה מינימלית לשאיפה")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mode = st.radio("בחר יעד", ["חודשי", "שנתי"], horizontal=True)
    
    with col2:
        if mode == "חודשי":
            target = Decimal(st.number_input("הכנסה נטו חודשית מינימלית (₪)", min_value=0.0))
            target_annual = target * Decimal("12")
        else:
            target = Decimal(st.number_input("הכנסה נטו שנתית מינימלית (₪)", min_value=0.0))
            target_annual = target
    
    if st.button("🎯 חשב הכנסה ברוטו הדרושה"):
        if target_annual > 0:
            solve_result = solver.solve_for_target_net_annual(
                st.session_state.scenario,
                target_annual,
            )
            st.success(f"✅ ברוטו שנתי הדרוש: {solve_result.required_gross_annual:,.0f} ₪")
            st.info(f"ברוטו חודשי: {solve_result.required_gross_monthly:,.0f} ₪")
            st.info(f"נטו שנתי המתקבל: {solve_result.resulting_net_annual:,.0f} ₪")
            st.caption(f"איטרציות חיפוש: {solve_result.iterations}")

with tab5:
    st.write("### השוואת תרחישים")
    st.info("בקרוב: יכולת השוואה בין תרחישים שומרים")


# Footer
st.markdown("---")
st.caption("© 2026 - כלי אישי להערכת הכנסות לעצמאים בישראל. לא תייעוץ מס רשמי.")
