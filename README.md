# SecureDrift

## Hackathon context

SecureDrift was created for a Société Générale hackathon challenge focused on
continuously monitoring security control configuration drift, reducing manual
compliance review, and explaining why a change may create security or
regulatory risk.

The project compares security configuration changes with expected baseline
values, prioritizes risky changes, maps them to compliance frameworks, and
displays the results in an interactive Streamlit dashboard.

## Problem

Security controls change frequently across cloud, network, identity, logging,
encryption, and endpoint systems. A change can be approved, temporary, or
legitimate, but it can also weaken a control and remain unnoticed.

The prototype focuses on:

- Detecting changes where the current value differs from the baseline.
- Classifying changes as Critical, High, Medium, or Low risk.
- Identifying approved and unapproved changes.
- Highlighting stale configuration drift.
- Showing compliance impact for NIST, GDPR, CIS, ISO, and PCI.
- Providing remediation guidance and CSV export from the dashboard.

## Current sample results

The included dataset contains 1,000 configuration events. Running the detector
currently produces:

| Metric | Result |
| --- | ---: |
| Configuration events | 1,000 |
| Detected drifts | 505 |
| Critical drifts | 104 |
| High-risk drifts | 91 |
| Medium-risk drifts | 135 |
| Low-risk drifts | 175 |

These are results from the included sample data, not production performance
measurements.

## How it works

1. Load baseline controls from `sample_data/baseline_configs.json`.
2. Load configuration events from `sample_data/config_drift_events.csv`.
3. Compare each event's current and baseline values.
4. Normalize severity, approval status, dates, and compliance labels.
5. Present prioritized findings in the Streamlit dashboard.

## Project structure

```text
.
├── app.py                         # Streamlit dashboard
├── drift_engine.py                # Data loading and drift detection
├── requirements.txt               # Python dependencies
├── sample_data/
│   ├── baseline_configs.json      # Example security baselines
│   └── config_drift_events.csv    # Example configuration events
└── Problem_02_Config_Drift/       # Original hackathon problem statement
```

## Run locally

Requirements: Python 3.12 or later.

```bash
git clone https://github.com/AnanthaBayary/secure-drift.git
cd secure-drift
python -m pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually
`http://localhost:8501`.

The application resolves the sample data relative to the project directory,
so it can be launched from any working directory.

## Limitations

This is a hackathon proof of concept. It currently uses local sample files and
does not connect directly to AWS, Azure, firewalls, endpoint platforms, or a
SIEM. The remediation commands shown in the UI are recommendations only; the
prototype does not execute changes against infrastructure.
