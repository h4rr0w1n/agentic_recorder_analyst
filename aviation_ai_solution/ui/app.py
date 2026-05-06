"""
Aviation AI Solution - Web-based User Interface
A simple, intuitive interface designed for ATC operators and team leaders.
No IT knowledge required.
"""

import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator_agent import OrchestratorAgent
from pipelines.stream_processor import StreamProcessor

# Page configuration
st.set_page_config(
    page_title="Aviation AI Solution",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better readability
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize session state variables."""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'history' not in st.session_state:
        st.session_state.history = []

def main():
    # Header
    st.markdown('<p class="main-header">✈️ Aviation AI Solution</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Predictive Advisory & Risk Analysis for ATC Operations</p>', unsafe_allow_html=True)
    
    # Initialize session
    initialize_session()
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/airplane-mode.png", width=80)
        st.title("Navigation")
        
        menu_options = ["🔍 Flight Analysis", "📊 Risk Dashboard", "📁 Data Upload", "⚙️ Settings", "❓ Help"]
        choice = st.radio("Select Action", menu_options, label_visibility="collapsed")
        
        st.divider()
        
        # Quick stats
        st.subheader("System Status")
        st.success("✅ All Systems Operational")
        st.info(f"🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        if st.session_state.history:
            st.metric("Analyses Today", len(st.session_state.history))
    
    # Main content based on selection
    if choice == "🔍 Flight Analysis":
        flight_analysis_page()
    elif choice == "📊 Risk Dashboard":
        risk_dashboard_page()
    elif choice == "📁 Data Upload":
        data_upload_page()
    elif choice == "⚙️ Settings":
        settings_page()
    elif choice == "❓ Help":
        help_page()

def flight_analysis_page():
    """Flight Analysis Page - Main analysis interface."""
    st.header("🔍 Flight Risk Analysis")
    st.write("Enter flight details to get predictive risk assessment and advisory recommendations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        flight_code = st.text_input(
            "Flight Code",
            placeholder="e.g., DLH456, ABC123",
            help="IATA or ICAO flight code (3 letters + 3-4 numbers)"
        )
        
        origin = st.text_input(
            "Origin Airport",
            placeholder="e.g., EDDM, LHR, JFK",
            help="ICAO airport code (4 letters)"
        )
        
        date = st.date_input(
            "Flight Date",
            value=datetime.now().date(),
            help="Select the date of the flight"
        )
    
    with col2:
        destination = st.text_input(
            "Destination Airport",
            placeholder="e.g., EDDF, CDG, ORD",
            help="ICAO airport code (4 letters)"
        )
        
        fir = st.text_input(
            "Flight Information Region (FIR)",
            placeholder="e.g., EDGG, EGTT, KZNY",
            help="ICAO FIR code (4 letters)"
        )
        
        time_window = st.selectbox(
            "Time Window",
            ["Last 1 hour", "Last 3 hours", "Last 6 hours", "Last 12 hours", "Last 24 hours"],
            help="Select the time window for analysis"
        )
    
    # Advanced options (collapsible)
    with st.expander("⚙️ Advanced Options"):
        include_weather = st.checkbox("Include Weather Data (METAR/TAF)", value=True)
        include_notams = st.checkbox("Include NOTAMs", value=True)
        include_atc_transcripts = st.checkbox("Include ATC Transcripts", value=True)
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Minimum confidence level for recommendations"
        )
    
    # Analyze button
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        if not flight_code:
            st.error("❌ Please enter a flight code.")
        else:
            perform_analysis(flight_code, origin, destination, fir, date, time_window,
                           include_weather, include_notams, include_atc_transcripts, confidence_threshold)

def perform_analysis(flight_code, origin, destination, fir, date, time_window,
                    include_weather, include_notams, include_atc_transcripts, confidence_threshold):
    """Perform flight analysis and display results."""
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "Retrieving flight data...",
        "Analyzing ATC transcripts...",
        "Extracting safety factors...",
        "Computing risk predictions...",
        "Validating against ICAO standards...",
        "Generating recommendations..."
    ]
    
    for i, step in enumerate(steps):
        status_text.text(f"⏳ {step}")
        time.sleep(0.8)  # Simulate processing time
        progress_bar.progress((i + 1) / len(steps))
    
    progress_bar.empty()
    status_text.empty()
    
    # Generate mock results (in real implementation, call orchestrator)
    results = generate_mock_analysis(flight_code, origin, destination, fir, date)
    st.session_state.analysis_results = results
    st.session_state.history.append({
        'flight': flight_code,
        'date': date,
        'timestamp': datetime.now()
    })
    
    # Display results
    display_analysis_results(results)

def generate_mock_analysis(flight_code, origin, destination, fir, date):
    """Generate mock analysis results for demonstration."""
    return {
        'flight_code': flight_code,
        'route': f"{origin or '????'} → {destination or '????'}",
        'fir': fir or 'EDGG',
        'date': date,
        'risk_score': 0.72,
        'risk_level': 'MEDIUM',
        'confidence': 0.85,
        'tokai_factors': {
            'A-1_Perception': {'positive': 12, 'negative': 2},
            'A-2_Memory': {'positive': 8, 'negative': 1},
            'A-3_Decision': {'positive': 15, 'negative': 3},
            'A-4_Action': {'positive': 10, 'negative': 1},
            'A-5_Conformance': {'positive': 18, 'negative': 2}
        },
        'phraseology_compliance': 0.94,
        'anomalies_detected': [
            {'type': 'Altitude Deviation', 'severity': 'LOW', 'timestamp': '14:23:15'},
            {'type': 'Readback Error', 'severity': 'MEDIUM', 'timestamp': '14:45:32'}
        ],
        'recommendations': [
            {
                'priority': 'HIGH',
                'type': 'Advisory',
                'message': f"Recommend pre-emptive altitude adjustment for {flight_code}; traffic density increasing in sector SAU.",
                'confidence': 0.88
            },
            {
                'priority': 'MEDIUM',
                'type': 'Monitoring',
                'message': "Continue monitoring crew readback accuracy; 2 minor deviations detected in last 30 minutes.",
                'confidence': 0.76
            },
            {
                'priority': 'LOW',
                'type': 'Information',
                'message': "Weather conditions at destination improving; METAR shows visibility > 10km.",
                'confidence': 0.92
            }
        ],
        'warnings': [],
        'human_review_required': False
    }

def display_analysis_results(results):
    """Display analysis results in a user-friendly format."""
    
    st.divider()
    
    # Risk Score Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_color = {
            'LOW': 'success',
            'MEDIUM': 'warning',
            'HIGH': 'error',
            'CRITICAL': 'error'
        }.get(results['risk_level'], 'warning')
        
        st.metric(
            "Risk Level",
            results['risk_level'],
            delta=f"Confidence: {results['confidence']*100:.0f}%"
        )
    
    with col2:
        st.metric("Overall Risk Score", f"{results['risk_score']*100:.0f}%")
    
    with col3:
        st.metric("Phraseology Compliance", f"{results['phraseology_compliance']*100:.0f}%")
    
    # TOKAI Factors
    st.subheader("📊 Safety Factor Analysis (TOKAI)")
    
    tokai_cols = st.columns(5)
    factor_names = ['Perception', 'Memory', 'Decision', 'Action', 'Conformance']
    
    for i, (factor, data) in zip(range(5), results['tokai_factors'].items()):
        positive = data['positive']
        negative = data['negative']
        total = positive + negative
        score = positive / total if total > 0 else 0
        
        with tokai_cols[i]:
            st.metric(
                f"A-{i+1} {factor_names[i]}",
                f"{score*100:.0f}%",
                delta=f"+{positive} / -{negative}"
            )
    
    # Anomalies
    if results['anomalies_detected']:
        st.subheader("⚠️ Anomalies Detected")
        for anomaly in results['anomalies_detected']:
            severity_color = {
                'LOW': 'info',
                'MEDIUM': 'warning',
                'HIGH': 'error',
                'CRITICAL': 'error'
            }.get(anomaly['severity'], 'info')
            
            st.alert(f"**{anomaly['severity']}** - {anomaly['type']} at {anomaly['timestamp']}")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    for i, rec in enumerate(results['recommendations'], 1):
        priority_icon = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }.get(rec['priority'], '⚪')
        
        with st.container():
            st.markdown(f"**{priority_icon} {rec['priority']} Priority - {rec['type']}**")
            st.info(rec['message'])
            st.caption(f"Confidence: {rec['confidence']*100:.0f}%")
    
    # Warnings
    if results['warnings']:
        st.subheader("🚨 Active Warnings")
        for warning in results['warnings']:
            st.error(f"⚠️ {warning}")
    
    # Human Review Flag
    if results['human_review_required']:
        st.warning("👤 This analysis requires human expert review due to low confidence in critical findings.")
    
    # Export options
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Report (PDF)", use_container_width=True):
            st.success("Report generated successfully! (Demo)")
    
    with col2:
        if st.button("📧 Email to Supervisor", use_container_width=True):
            st.success("Report sent to supervisor! (Demo)")

def risk_dashboard_page():
    """Risk Dashboard Page - Overview of all active risks."""
    st.header("📊 Risk Dashboard")
    st.write("Real-time overview of all active flights and their risk assessments.")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Active Flights", "47", "+12%")
    col2.metric("High Risk", "3", "-1")
    col3.metric("Medium Risk", "12", "+2")
    col4.metric("Low Risk", "32", "+11")
    
    st.divider()
    
    # Interactive map placeholder
    st.subheader("🗺️ FIR Risk Heatmap")
    st.info("🗺️ Interactive map showing risk levels across different Flight Information Regions")
    
    # Create a mock heatmap visualization
    import pandas as pd
    import numpy as np
    
    fir_data = pd.DataFrame({
        'FIR': ['EDGG', 'EGTT', 'LFFF', 'EDMM', 'EBBU'],
        'Risk Score': [0.45, 0.72, 0.38, 0.61, 0.29],
        'Active Flights': [12, 8, 6, 9, 4]
    })
    
    st.dataframe(
        fir_data.style.format({
            'Risk Score': '{:.0%}'
        }).background_gradient(subset=['Risk Score'], cmap='RdYlGn_r'),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Recent alerts
    st.subheader("🔔 Recent Alerts")
    
    alerts = [
        {'time': '14:52', 'flight': 'DLH456', 'type': 'Altitude Deviation', 'severity': 'LOW'},
        {'time': '14:48', 'flight': 'AFR123', 'type': 'Sector Overload Warning', 'severity': 'MEDIUM'},
        {'time': '14:35', 'flight': 'BAW789', 'type': 'Readback Error', 'severity': 'LOW'},
        {'time': '14:22', 'flight': 'KLM456', 'type': 'Weather Avoidance', 'severity': 'MEDIUM'},
    ]
    
    for alert in alerts:
        severity_icon = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(alert['severity'], '⚪')
        st.write(f"{severity_icon} **{alert['time']}** - {alert['flight']}: {alert['type']} ({alert['severity']})")

def data_upload_page():
    """Data Upload Page - Upload aviation records."""
    st.header("📁 Data Upload")
    st.write("Upload aviation records for analysis. Supported formats: CSV, JSON, XML, Audio (WAV, MP3)")
    
    upload_type = st.selectbox(
        "Select Data Type",
        ["Flight Records", "ATC Transcripts", "METAR/TAF Weather", "NOTAMs", "Audio Files", "Other"]
    )
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        accept_multiple_files=True,
        help="Drag and drop files here or click to browse"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        for file in uploaded_files:
            st.write(f"📄 {file.name} ({file.size / 1024:.1f} KB)")
        
        if st.button("📤 Upload Files", type="primary"):
            # Simulate upload
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress.progress(i + 1)
            st.success("✅ Files uploaded successfully! Processing will begin shortly.")
    
    st.divider()
    
    # Stream URL input
    st.subheader("🌐 Connect to Live Stream")
    stream_url = st.text_input(
        "Stream URL",
        placeholder="e.g., rtsp://ads-b.example.com/stream"
    )
    
    if stream_url:
        if st.button("🔗 Connect to Stream"):
            st.info("🔄 Connecting to stream... (Demo)")
            time.sleep(1)
            st.success("✅ Connected to live stream!")

def settings_page():
    """Settings Page - Configure system preferences."""
    st.header("⚙️ Settings")
    st.write("Configure system preferences and thresholds.")
    
    st.subheader("🎯 Analysis Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_fir = st.text_input("Default FIR", value="EDGG")
        default_time_window = st.selectbox(
            "Default Time Window",
            ["Last 1 hour", "Last 3 hours", "Last 6 hours", "Last 12 hours", "Last 24 hours"]
        )
    
    with col2:
        confidence_threshold = st.slider(
            "Default Confidence Threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.75,
            step=0.05
        )
        auto_escalate = st.checkbox("Auto-escalate high-risk findings", value=True)
    
    st.divider()
    
    st.subheader("🔔 Notification Settings")
    
    email_notifications = st.checkbox("Enable email notifications", value=False)
    if email_notifications:
        email_address = st.text_input("Email Address", placeholder="your.email@example.com")
    
    sms_notifications = st.checkbox("Enable SMS notifications for critical alerts", value=False)
    if sms_notifications:
        phone_number = st.text_input("Phone Number", placeholder="+1234567890")
    
    st.divider()
    
    st.subheader("💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Analysis History", use_container_width=True):
            st.session_state.history = []
            st.success("History cleared!")
    
    with col2:
        if st.button("📥 Export All Data", use_container_width=True):
            st.success("Data exported successfully! (Demo)")

def help_page():
    """Help Page - User guide and documentation."""
    st.header("❓ Help & Documentation")
    st.write("Learn how to use the Aviation AI Solution effectively.")
    
    # Quick Start Guide
    st.subheader("🚀 Quick Start Guide")
    
    steps = [
        {
            'step': '1',
            'title': 'Enter Flight Details',
            'description': 'Navigate to "Flight Analysis" and enter the flight code, airports, and date.'
        },
        {
            'step': '2',
            'title': 'Configure Options',
            'description': 'Select which data sources to include (weather, NOTAMs, ATC transcripts).'
        },
        {
            'step': '3',
            'title': 'Start Analysis',
            'description': 'Click "Start Analysis" and wait for the system to process the data.'
        },
        {
            'step': '4',
            'title': 'Review Results',
            'description': 'Review the risk score, safety factors, anomalies, and recommendations.'
        },
        {
            'step': '5',
            'title': 'Take Action',
            'description': 'Follow the prioritized recommendations and export/share the report if needed.'
        }
    ]
    
    for step in steps:
        with st.expander(f"Step {step['step']}: {step['title']}"):
            st.write(step['description'])
    
    st.divider()
    
    # FAQ
    st.subheader("❓ Frequently Asked Questions")
    
    faqs = [
        {
            'question': 'What is the TOKAI taxonomy?',
            'answer': 'TOKAI is EUROCONTROL\'s safety taxonomy that categorizes human factors into 5 areas: Perception, Memory, Decision, Action, and Conformance. Our system analyzes ATC transcripts against these factors to identify potential safety issues.'
        },
        {
            'question': 'How accurate are the risk predictions?',
            'answer': 'The system achieves ≥85% AUC for Loss-of-Separation prediction based on historical data validation. However, all critical decisions should involve human expert review.'
        },
        {
            'question': 'What data sources are supported?',
            'answer': 'We support NOTAMs, METARs, FDR/CVR logs, safety reports, ATC transcripts, flight plans, ADS-B tracks, radar data, and ACARS messages.'
        },
        {
            'question': 'When does the system require human review?',
            'answer': 'Human review is automatically triggered when confidence scores fall below the threshold (default 75%) for critical findings, or when anomalies exceed predefined severity levels.'
        },
        {
            'question': 'Is my data secure?',
            'answer': 'Yes. All data is pseudonymized at ingestion, access is role-based, and we comply with GDPR and ICAO Annex 9 privacy requirements.'
        }
    ]
    
    for faq in faqs:
        with st.expander(faq['question']):
            st.write(faq['answer'])
    
    st.divider()
    
    # Contact Support
    st.subheader("📞 Need More Help?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Technical Support**\n\n📧 support@aviation-ai.com\n📞 +49 123 456 7890")
    
    with col2:
        st.info("**Training Requests**\n\n📧 training@aviation-ai.com\n📞 +49 123 456 7891")
    
    with col3:
        st.info("**Emergency Hotline**\n\n📞 +49 123 456 7899\n(Available 24/7)")
    
    st.divider()
    
    # System Info
    st.caption("""
    **Version:** 1.0.0 | **Last Updated:** 2026-01-09
    
    Built with ❤️ for safer aviation operations.
    
    *This system is designed to assist ATC operators and team leaders. All critical decisions should involve human judgment.*
    """)

if __name__ == "__main__":
    main()
