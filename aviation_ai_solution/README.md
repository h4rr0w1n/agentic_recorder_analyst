# ✈️ Agentic AI Solution for Aviation Records Analysis & Predictive Advisory

## 🎯 Overview

This system implements an agentic AI architecture for retrieving, analyzing aviation records (scattered and streamed), and delivering predictive/advisory/warning outputs for ATC operations enhancement.

**Designed for:** ATC Operators, Team Leaders, and Aviation Safety Personnel  
**No IT expertise required!** See [USER_MANUAL.md](USER_MANUAL.md) for complete instructions.

---

## 🚀 Quick Start (For Non-Technical Users)

### Step 1: Install the Software

**On Windows:**
```
Double-click: install.bat
```

**On Mac/Linux:**
```
Open Terminal in this folder and run: ./install.sh
```

### Step 2: Launch the User Interface

**On Windows:**
```
Double-click: run_ui.bat
```

**On Mac/Linux:**
```
./run_ui.sh
```

Your web browser will automatically open to the application!

### Step 3: Start Analyzing Flights

1. Click "🔍 Flight Analysis" in the sidebar
2. Enter flight details (e.g., DLH456)
3. Click "🚀 Start Analysis"
4. Review results and recommendations

📖 **Need help?** Read the complete [User Manual](USER_MANUAL.md)

---

## 📁 Project Structure

```
aviation_ai_solution/
├── 📘 USER_MANUAL.md       # Complete user guide (START HERE!)
├── 📦 install.sh / install.bat    # Automated installer
├── 🚀 run_ui.sh / run_ui.bat      # Launch the UI
├── 💻 run_cli.sh / run_cli.bat    # Command-line mode
├│
├── ui/                     # User interface (Streamlit)
│   └── app.py             # Main UI application
├── agents/                 # Multi-agent framework
│   ├── orchestrator_agent.py   # Coordinates all agents
│   ├── retriever_agent.py      # Data retrieval
│   ├── analyzer_agent.py       # NLP & TOKAI analysis
│   ├── predictor_agent.py      # Risk prediction
│   ├── advisor_agent.py        # Recommendations
│   └── guardian_agent.py       # Compliance checking
├── pipelines/              # Data processing
│   └── stream_processor.py # Streaming data handler
├── models/                 # AI/ML models
├── config/                 # Configuration
├── data_lake/              # Data storage
├── output/                 # Generated reports
└── tests/                  # Test suites
```

---

## 🎨 User Interface Features

### 🔍 Flight Analysis
- Enter flight code, airports, date, and time window
- Configure data sources (weather, NOTAMs, ATC transcripts)
- Get risk scores, TOKAI factor analysis, and recommendations
- Export reports as PDF or email to supervisors

### 📊 Risk Dashboard
- Real-time overview of all active flights
- FIR risk heatmap
- Recent alerts feed
- Sortable flight list with risk levels

### 📁 Data Upload
- Drag & drop file upload (CSV, JSON, XML, WAV, MP3)
- Connect to live streams (ADS-B, radar, ATC audio)
- Automatic session grouping by date

### ⚙️ Settings
- Customize analysis preferences
- Configure notifications (email, SMS)
- Manage data and history

### ❓ Help
- Built-in tutorials
- FAQ section
- Contact information for support

---

## 🤖 Agent Architecture

The system uses six specialized AI agents working together:

| Agent | Role | Output |
|-------|------|--------|
| **Retriever** | Queries data sources, semantic search | Structured context bundles |
| **Analyzer** | NLP on transcripts, TOKAI extraction | Annotated factors (A-1 to A-5) |
| **Predictor** | Risk modeling (RF+LSTM+GNN) | Risk scores with confidence |
| **Advisor** | Generates recommendations | Prioritized actions (HIGH/MED/LOW) |
| **Guardian** | ICAO compliance validation | Audit trails, escalation flags |
| **Orchestrator** | Coordinates workflow | Unified assessment report |

---

## 📥 Handling Inputs

### From Files (Directory)
Place your aviation records in any folder:
```bash
python -m aviation_ai_solution.main --input /path/to/your/data --output ./output
```

Supported formats: CSV, JSON, XML, WAV, MP3, PDF

### From Online Streams
The system can download and process streaming data:
```bash
python -m aviation_ai_solution.pipelines.stream_processor \
  --stream-url "rtsp://ads-b.example.com/stream" \
  --session-date "2026-01-09" \
  --output-dir ./data_lake
```

**Features:**
- Automatic download and extraction
- Chronological ordering
- Session grouping by specified date
- Support for ADS-B, radar tracks, ACARS, ATC voice streams

---

## 🔧 Technical Details (For IT Support)

### Technology Stack

| Component | Technology |
|-----------|------------|
| User Interface | Streamlit |
| AI Framework | LangGraph + Custom Agents |
| NLP | spaCy + Transformers |
| Risk Models | Random Forest + LSTM + GNN |
| Stream Processing | Apache Flink + Kafka |
| Data Lake | Apache Iceberg |
| Vector Search | FAISS |
| Graph Database | Neo4j |
| ASR | Whisper (aviation-tuned) |

### System Requirements

- **OS:** Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)
- **Python:** 3.8 or higher
- **RAM:** 8 GB minimum, 16 GB recommended
- **Storage:** 10 GB free space
- **Internet:** Broadband connection

### Installation (Technical)

```bash
# Clone or download the repository
cd aviation_ai_solution

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the UI
streamlit run ui/app.py
```

---

## 📊 Expected Outcomes

| Capability | Target Metric |
|-----------|---------------|
| Record Linking | ≥95% success rate |
| Search Precision | ≥90% precision@5 |
| Risk Prediction AUC | ≥0.85 |
| Advisory Acceptance | ≥75% |
| Warning Latency | <30 seconds |
| ICAO Compliance | ≥98% |

---

## 🛡️ Safety & Compliance

This system is designed to comply with:
- ICAO Annex 10 (Phraseology)
- ICAO Annex 11 (ATC Services)
- EUROCONTROL TOKAI Taxonomy
- GDPR (Data Privacy)
- EASA/FAA guidelines

**Important:** This is an advisory tool. All critical decisions require human oversight.

---

## 📞 Support

| Need | Contact |
|------|---------|
| Technical Support | support@aviation-ai.com |
| Training | training@aviation-ai.com |
| Emergency (24/7) | +49 123 456 7899 |

---

## 📄 Documentation

- **[USER_MANUAL.md](USER_MANUAL.md)** - Complete user guide with tutorials
- **[README.md](README.md)** - This file (technical overview)
- **In-App Help** - Click "❓ Help" in the UI

---

## 📝 License

MIT License - See LICENSE file for details.

---

**✈️ Fly Safe!**

*Built with ❤️ for safer aviation operations.*
