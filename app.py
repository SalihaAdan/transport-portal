import streamlit as st

st.set_page_config(page_title="Transport Portal", page_icon="🚌", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "poll"

st.sidebar.title("Navigation")
if st.sidebar.button("🗳️ Submit Vote"):
    st.session_state.page = "poll"
if st.sidebar.button("🚌 Check My Bus"):
    st.session_state.page = "student_view"
if st.sidebar.button("📊 Transport Office"):
    st.session_state.page = "dashboard"

st.sidebar.markdown("---")
st.sidebar.caption("Poll closes 30 min before fleet departure")

if st.session_state.page == "poll":
    from src.ui.poll_form import show_poll_form
    show_poll_form()
elif st.session_state.page == "student_view":
    try:
        from src.ui.student_view import show_student_view
        show_student_view()
    except ImportError:
        st.warning("Check My Bus page under construction.")
elif st.session_state.page == "dashboard":
    try:
        from src.ui.dashboard import show_dashboard
        show_dashboard()
    except ImportError:
        st.warning("Transport Office page under construction.")
