import streamlit as st

st.set_page_config(
    page_title="About SecureDrift",
    page_icon="🔒",
    layout="wide",
)

st.title("🔒 About SecureDrift")
st.subheader("Société Générale Hackathon Project")

st.markdown(
    """
SecureDrift was created for a Société Générale hackathon challenge focused on
continuously monitoring security control configuration drift, reducing manual
compliance review, and explaining why a change may create security or
regulatory risk.

The application compares configuration changes with expected baseline values,
prioritizes risky changes, maps findings to compliance frameworks, and provides
remediation guidance through an interactive dashboard.
"""
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### What it detects")
    st.markdown(
        """
        - Configuration values that differ from their baseline
        - Critical, high, medium, and low-risk changes
        - Approved and unapproved changes
        - Stale configuration drift
        - Compliance impact across NIST, GDPR, CIS, ISO, and PCI
        """
    )

with col2:
    st.markdown("### Technology")
    st.markdown(
        """
        - **Python** for the detection engine
        - **Pandas** for event processing
        - **Streamlit** for the dashboard
        - **Plotly** for interactive visualizations
        - **JSON and CSV** for the sample baseline and event data
        """
    )

st.divider()

st.markdown("### Current scope")
st.info(
    "This is a hackathon proof of concept using local sample data. "
    "The remediation commands shown in the dashboard are recommendations only; "
    "the application does not execute infrastructure changes."
)

st.markdown("### Sample dataset")
st.markdown(
    """
The included dataset contains **1,000 configuration events** and currently
produces **505 detected drifts**, including **104 critical** and **91 high-risk**
findings.
"""
)
