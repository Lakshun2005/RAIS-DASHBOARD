# RAIS Dashboard

A Streamlit-based Rejection Analysis & Insights System (RAIS) dashboard for manufacturing quality control.

## Features

- **Executive Summary**: Monthly production vs. rejection trends with dual-axis charts
- **Visual Inspection Analysis**: Pareto charts for visual defects (COAG, SD, PS, BM, etc.)
- **Shop Floor Analysis**: Dipping section defect breakdown
- **Integrity Analysis**: Balloon & Valve inspection defect tracking

## Data Sources

The dashboard reads from the following Excel files:
- `YEARLY PRODUCTION COMMULATIVE 2025-26.xlsx` - Monthly production and rejection data
- `VISUAL INSPECTION REPORT 2025.xlsx` - Visual inspection defects
- `SHOPFLOOR REJECTION REPORT.xlsx` - Shop floor defects
- `BALLOON & VALVE INTEGRITY INSPECTION REPORT FILE 2025.xlsx` - Integrity test data

## Installation

```bash
pip install streamlit pandas plotly openpyxl
```

## Running the Dashboard

```bash
streamlit run RAIS.py
```

Open http://localhost:8501 in your browser.

## Files

- `RAIS.py` - Main Streamlit dashboard application
- `data_loader.py` - Data extraction module for reading Excel files

## Requirements

- Python 3.8+
- streamlit
- pandas
- plotly
- openpyxl
