import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from drift_engine import DriftDetector

# Page configuration
st.set_page_config(
    page_title="Security Control Drift Detector",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Security Control Drift Detector")
st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load REAL data from your drift_engine.py
@st.cache_data(ttl=60)
def load_real_data():
    detector = DriftDetector()
    df = detector.load_data()
    drifts = detector.detect_drifts(df)
    summary = detector.get_summary(drifts)
    return drifts, summary

# Load the data
drifts, summary = load_real_data()

# Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📊 Total Drifts", summary['total_drifts'])
with col2:
    st.metric("🔴 Critical", summary['critical'], delta="URGENT" if summary['critical'] > 0 else None, delta_color="inverse")
with col3:
    st.metric("🟠 High", summary['high'])
with col4:
    st.metric("📈 Avg Risk Score", f"{summary['avg_risk_score']}/100")
with col5:
    compliance_score = max(0, 100 - (summary['total_drifts'] // 10))
    st.metric("✅ Compliance Score", f"{compliance_score}%")

st.divider()

# Charts - Only show if we have data
col1, col2 = st.columns(2)

with col1:
    st.subheader("Drifts by Risk Level")
    if summary['critical'] > 0 or summary['high'] > 0:
        risk_data = pd.DataFrame({
            'Risk Level': ['Critical', 'High', 'Medium'],
            'Count': [summary['critical'], summary['high'], summary['medium']]
        })
        risk_data = risk_data[risk_data['Count'] > 0]
        fig = px.bar(risk_data, x='Risk Level', y='Count', color='Risk Level',
                     color_discrete_map={'Critical': '#ff0000', 'High': '#ff6600', 'Medium': '#ffcc00'})
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No risk data available")

with col2:
    st.subheader("Drifts by Control Type")
    if summary['by_type']:
        type_data = pd.DataFrame({
            'Control Type': list(summary['by_type'].keys()),
            'Count': list(summary['by_type'].values())
        })
        fig = px.pie(type_data, values='Count', names='Control Type', hole=0.4)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No drift data by type")

st.divider()

# ============================================
# COMPLIANCE FRAMEWORK IMPACT - WITH GRAPHS
# ============================================
st.subheader("📋 Compliance Framework Impact")

# Create compliance data from drifts
compliance_data = summary.get('compliance_impact', {})

if compliance_data:
    # Prepare data for charts
    compliance_df = pd.DataFrame({
        'Framework': list(compliance_data.keys()),
        'Violations': list(compliance_data.values())
    }).sort_values('Violations', ascending=False)
    
    # Calculate critical counts per framework
    framework_critical = {}
    framework_high = {}
    for d in drifts:
        for comp in d['compliance']:
            if d['risk_level'] == 'CRITICAL':
                framework_critical[comp] = framework_critical.get(comp, 0) + 1
            elif d['risk_level'] == 'HIGH':
                framework_high[comp] = framework_high.get(comp, 0) + 1
    
    # Two columns for compliance charts
    comp_col1, comp_col2 = st.columns(2)
    
    with comp_col1:
        # Bar chart for compliance violations
        fig_bar = px.bar(compliance_df, x='Framework', y='Violations', 
                         title="Violations by Framework",
                         color='Violations', 
                         color_continuous_scale='Reds',
                         text='Violations')
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', 
                              paper_bgcolor='rgba(0,0,0,0)', 
                              height=350,
                              showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with comp_col2:
        # Donut chart for compliance distribution
        fig_donut = px.pie(compliance_df, values='Violations', names='Framework',
                           title="Compliance Violation Distribution",
                           hole=0.5,
                           color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_donut.update_layout(height=350)
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)
    
    # Detailed compliance table with severity breakdown
    st.markdown("### 📊 Detailed Compliance Impact")
    
    # Build detailed table
    detailed_compliance = []
    for fw in compliance_df['Framework']:
        total = compliance_data.get(fw, 0)
        critical = framework_critical.get(fw, 0)
        high = framework_high.get(fw, 0)
        medium = total - critical - high
        
        # Calculate framework health score
        fw_health = max(0, 100 - (critical * 20 + high * 10 + medium * 5))
        
        detailed_compliance.append({
            'Framework': fw,
            'Total Violations': total,
            '🔴 Critical': critical,
            '🟠 High': high,
            '🟡 Medium': medium,
            'Health Score': f"{fw_health}%",
            'Status': '🔴 Critical' if fw_health < 40 else '🟠 Warning' if fw_health < 70 else '✅ Good'
        })
    
    detail_df = pd.DataFrame(detailed_compliance)
    st.dataframe(detail_df, use_container_width=True, hide_index=True)
    
    # ============================================
    # ENHANCED OVERALL COMPLIANCE HEALTH SECTION
    # ============================================
    st.markdown("---")
    st.markdown("## 🏥 Overall Compliance Health")
    
    # Calculate overall metrics
    total_violations = summary['total_drifts']
    total_critical = summary['critical']
    total_high = summary['high']
    total_medium = summary['medium']
    overall_score = max(0, 100 - (total_critical * 8 + total_high * 4 + total_medium * 2))
    overall_score = min(100, overall_score)
    
    # Determine status
    if overall_score >= 80:
        status = "🟢 HEALTHY"
        status_color = "#22c55e"
        status_bg = "rgba(34,197,94,0.1)"
        recommendation = "✅ Compliance is good. Continue monitoring for any new drifts."
        icon = "✅"
    elif overall_score >= 60:
        status = "🟡 AT RISK"
        status_color = "#eab308"
        status_bg = "rgba(234,179,8,0.1)"
        recommendation = "⚠️ Multiple violations detected. Review and remediate within 7 days."
        icon = "⚠️"
    elif overall_score >= 40:
        status = "🟠 DEGRADED"
        status_color = "#f97316"
        status_bg = "rgba(249,115,22,0.1)"
        recommendation = "🔴 Critical issues found. Remediate within 48 hours."
        icon = "🔴"
    else:
        status = "🔴 CRITICAL"
        status_color = "#ef4444"
        status_bg = "rgba(239,68,68,0.1)"
        recommendation = "🚨 IMMEDIATE ACTION REQUIRED! Security posture is compromised."
        icon = "🚨"
    
    # Create 3 columns for the enhanced health section
    health_col1, health_col2, health_col3 = st.columns([1, 1, 1.5])
    
    with health_col1:
        # Gauge chart for overall score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={"text": "Compliance Score", "font": {"size": 14, "color": "#8892a4"}},
            number={"font": {"size": 40, "color": status_color}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#4a5568", "tickwidth": 1},
                "bar": {"color": status_color},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(239,68,68,0.15)"},
                    {"range": [40, 60], "color": "rgba(249,115,22,0.12)"},
                    {"range": [60, 80], "color": "rgba(234,179,8,0.1)"},
                    {"range": [80, 100], "color": "rgba(34,197,94,0.08)"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": overall_score
                }
            }
        ))
        fig_gauge.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with health_col2:
        # Severity breakdown card
        st.markdown(f"""
        <div style="background:#111520;border-radius:10px;padding:1rem;height:100%;">
            <div style="font-size:0.8rem;color:#8892a4;margin-bottom:0.8rem;">📊 Severity Breakdown</div>
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span>🔴 Critical</span>
                    <span style="color:#ef4444;font-weight:700;">{total_critical}</span>
                </div>
                <div style="width:100%;height:6px;background:rgba(239,68,68,0.2);border-radius:3px;">
                    <div style="width:{min(100, total_critical * 5)}%;height:100%;background:#ef4444;border-radius:3px;"></div>
                </div>
            </div>
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span>🟠 High</span>
                    <span style="color:#f97316;font-weight:700;">{total_high}</span>
                </div>
                <div style="width:100%;height:6px;background:rgba(249,115,22,0.2);border-radius:3px;">
                    <div style="width:{min(100, total_high * 4)}%;height:100%;background:#f97316;border-radius:3px;"></div>
                </div>
            </div>
            <div style="margin-bottom:0.8rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span>🟡 Medium</span>
                    <span style="color:#eab308;font-weight:700;">{total_medium}</span>
                </div>
                <div style="width:100%;height:6px;background:rgba(234,179,8,0.2);border-radius:3px;">
                    <div style="width:{min(100, total_medium * 3)}%;height:100%;background:#eab308;border-radius:3px;"></div>
                </div>
            </div>
            <div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid rgba(255,255,255,0.07);">
                <div style="display:flex;justify-content:space-between;">
                    <span>📊 Total Drifts</span>
                    <span style="color:#e8eaf0;font-weight:700;">{total_violations}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with health_col3:
        # Status and recommendations card
        st.markdown(f"""
        <div style="background:{status_bg};border:1px solid {status_color};border-radius:10px;padding:1rem;height:100%;">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;">
                <div style="font-size:1.5rem;">{icon}</div>
                <div style="font-size:1.1rem;font-weight:700;color:{status_color};">{status}</div>
            </div>
            <div style="font-size:0.8rem;color:#8892a4;margin-bottom:0.8rem;">
                {recommendation}
            </div>
            <div style="margin-top:0.5rem;">
                <div style="font-size:0.7rem;color:#4a5568;">Priority Actions:</div>
                <ul style="font-size:0.7rem;color:#8892a4;margin-top:0.3rem;padding-left:1rem;">
                    <li>Fix {total_critical} critical drift{'s' if total_critical != 1 else ''} immediately</li>
                    <li>Review {total_high} high severity issue{'s' if total_high != 1 else ''} within 48 hours</li>
                    <li>Focus on frameworks with most violations</li>
                    <li>Document approved exceptions for remaining drifts</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add a trend indicator
    st.markdown("---")
    trend_col1, trend_col2, trend_col3, trend_col4 = st.columns(4)
    
    with trend_col1:
        st.metric("Critical Drifts", total_critical, delta="URGENT", delta_color="inverse")
    with trend_col2:
        st.metric("High Drifts", total_high)
    with trend_col3:
        st.metric("Compliance Score", f"{overall_score}%", delta=f"{overall_score - 50}%" if overall_score != 50 else None)
    with trend_col4:
        at_risk_pct = round((total_critical + total_high) / max(total_violations, 1) * 100, 1)
        st.metric("At Risk %", f"{at_risk_pct}%", delta="HIGH" if at_risk_pct > 50 else "MEDIUM" if at_risk_pct > 25 else "LOW", delta_color="inverse" if at_risk_pct > 50 else "normal")

else:
    st.info("No compliance violations detected")

st.divider()

# ============================================
# DRIFTS LIST WITH SEARCH AND FILTER
# ============================================
st.subheader("🚨 Active Configuration Drifts")

# Create filter columns
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])

with filter_col1:
    # Search box
    search_term = st.text_input("🔍 Search drifts", placeholder="Search by Control ID, Name, Changed By...")

with filter_col2:
    # Risk level filter - Multiselect dropdown
    risk_filter = st.multiselect(
        "Risk Level",
        options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default=["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    )
    # Helper text showing what's selected
    if risk_filter:
        st.caption(f"✅ Selected: {', '.join(risk_filter)}")
    else:
        st.warning("⚠️ No risk levels selected - showing no drifts")

with filter_col3:
    # Approval status filter
    approval_filter = st.selectbox(
        "Approval Status",
        options=["All", "Approved Only", "Unapproved Only"]
    )

with filter_col4:
    # Stale filter
    stale_filter = st.selectbox(
        "Duration",
        options=["All", "Stale (>90 days)", "Recent (≤90 days)"]
    )

# Apply filters to drifts
filtered_drifts = drifts.copy()

# Apply search filter
if search_term:
    filtered_drifts = [d for d in filtered_drifts if 
                       search_term.lower() in d['control_id'].lower() or 
                       search_term.lower() in d['name'].lower() or
                       search_term.lower() in d['changed_by'].lower() or
                       search_term.lower() in d.get('control_type', '').lower()]

# Apply risk filter
if risk_filter:
    filtered_drifts = [d for d in filtered_drifts if d['risk_level'] in risk_filter]
else:
    # If no risk levels selected, show no drifts
    filtered_drifts = []

# Apply approval filter
if approval_filter == "Approved Only":
    filtered_drifts = [d for d in filtered_drifts if d['approved']]
elif approval_filter == "Unapproved Only":
    filtered_drifts = [d for d in filtered_drifts if not d['approved']]

# Apply stale filter
if stale_filter == "Stale (>90 days)":
    filtered_drifts = [d for d in filtered_drifts if d['duration_days'] > 90]
elif stale_filter == "Recent (≤90 days)":
    filtered_drifts = [d for d in filtered_drifts if d['duration_days'] <= 90]

# Show filter results summary
st.caption(f"Showing {len(filtered_drifts)} of {len(drifts)} drifts")

# Export filtered data button
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("📥 Export to CSV", use_container_width=True):
        export_df = pd.DataFrame([{
            "Control ID": d['control_id'],
            "Name": d['name'],
            "Risk Level": d['risk_level'],
            "Current": d['current'],
            "Expected": d['expected'],
            "Duration Days": d['duration_days'],
            "Changed By": d['changed_by'],
            "Approved": "Yes" if d['approved'] else "No",
            "Risk Score": d['risk_score'],
            "Compliance": ', '.join(d['compliance'])
        } for d in filtered_drifts])
        csv = export_df.to_csv(index=False)
        st.download_button("Download CSV", csv, f"drift_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")

st.markdown("---")

# Display filtered drifts
if filtered_drifts:
    # Show top results
    display_drifts = filtered_drifts[:50] if len(filtered_drifts) > 50 else filtered_drifts
    
    if len(filtered_drifts) > 50:
        st.caption(f"Showing top 50 of {len(filtered_drifts)} drifts. Refine filters to see more.")
    
    # Use enumerate to create unique keys for each drift
    for idx, drift in enumerate(display_drifts):
        icon = "🔴" if drift['risk_level'] == 'CRITICAL' else "🟠" if drift['risk_level'] == 'HIGH' else "🟡"
        
        # Add stale badge
        stale_badge = " ⏰ STALE" if drift['duration_days'] > 90 else ""
        unapproved_badge = " 🚫 UNAPPROVED" if not drift['approved'] else ""
        
        with st.expander(f"{icon} [{drift['risk_level']}] {drift['control_id']}: {drift['name']}{stale_badge}{unapproved_badge}", 
                        expanded=drift['risk_level'] == 'CRITICAL'):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**📝 Configuration Drift**")
                st.markdown(f"- **Current:** `{drift['current']}`")
                st.markdown(f"- **Expected:** `{drift['expected']}`")
                st.markdown(f"- **Duration:** ⏱️ {drift['duration_days']} days")
                st.markdown(f"- **Changed by:** 👤 {drift['changed_by']}")
                st.markdown(f"- **Approved:** {'✅ Yes' if drift['approved'] else '❌ No'}")
                st.markdown(f"- **Change Type:** {drift.get('change_type', 'Unknown')}")
                st.markdown(f"- **Status:** {drift.get('status', 'Unknown')}")
            
            with col2:
                st.markdown(f"**🎯 Risk Assessment**")
                st.markdown(f"- **Risk Score:** {drift['risk_score']}/100")
                st.progress(drift['risk_score']/100)
                st.markdown(f"- **Severity:** {drift['risk_level']}")
            
            st.markdown("---")
            
            st.markdown(f"**📋 Compliance Impact:**")
            for comp in drift['compliance']:
                st.markdown(f"- {comp}")
            
            st.markdown(f"**🔧 Remediation Steps:**")
            st.code(drift['remediation'], language='bash')
            
            # Quick action buttons - Using index to create unique keys
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button(f"📋 Copy Fix", key=f"copy_{drift['control_id']}_{idx}"):
                    st.success("Command copied!")
            with btn_col2:
                if st.button(f"📧 Escalate", key=f"esc_{drift['control_id']}_{idx}"):
                    st.success(f"Escalated {drift['control_id']}")
            with btn_col3:
                if st.button(f"✅ Mark Fixed", key=f"fix_{drift['control_id']}_{idx}"):
                    st.success(f"Marked {drift['control_id']} as resolved")
else:
    st.success("🎉 No drifts match your filters! All controls are compliant.")

st.divider()

# Footer
st.caption("🔒 Security Control Drift Detection System | Continuous Compliance Monitoring")
st.caption("NIST SP 800-53 • GDPR • CIS Benchmarks")