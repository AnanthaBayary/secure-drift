# 🔒 SecureDrift - Security Control Drift Detection System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

**SecureDrift** detects configuration drifts across your infrastructure, assesses risk levels, and provides one-click remediation commands.

### 🎯 The Problem
- 40% of breaches come from misconfigured controls
- 72+ hours spent on manual audits
- No single source of truth for configurations

### ✨ Features
- 📊 Real-time dashboard with live metrics
- 🎯 Risk scoring (Critical/High/Medium/Low)
- 📋 Compliance mapping (NIST, GDPR, CIS)
- 🔧 One-click remediation commands
- 🔍 Search, filter, and export CSV

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Total Drifts | 505 |
| Critical | 104 |
| High | 91 |
| Detection Rate | >85% |
| False Positive | <15% |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Visualization | Plotly |
| Data Processing | Pandas |
| Runtime | Python 3.12+ |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/AnanthaBayary/secure-drift.git
cd secure-drift

# 2. Install
python -m pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

The detector loads `sample_data/` relative to the project, so it works from
any working directory on Linux, macOS, or Windows.

## Project status

This repository contains a hackathon proof of concept. The detector supports
the included JSONL baselines and CSV event history, normalizes source severity
values, identifies approved versus unapproved changes, and presents the
results in the Streamlit dashboard.

## Recommended next steps

1. Add read-only connectors for AWS, Azure, firewalls, and endpoint platforms.
2. Store baselines and drift events in a durable database instead of local files.
3. Add alert delivery for critical and unapproved drifts.
4. Evaluate precision and recall against labeled events before enabling
   automated remediation.
