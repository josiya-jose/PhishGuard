import streamlit as st


def show():
    

    st.markdown("""
    <div style="padding:120px;color:white;">
        <h1>Is this link safe?</h1>
        <p>AI-powered phishing detection system</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Get Started"):
        st.session_state.page = "login"
        st.rerun()
