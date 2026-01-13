# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project collects, processes, and visualizes Japanese infectious disease surveillance data from the National Institute of Health Crisis Management (国立健康危機管理研究機構). It consists of:
- Python-based data pipeline for downloading and processing CSV data
- Vue 3 web application for data visualization using ECharts
- Automated GitHub Actions workflows for data updates and deployment

Data sources: https://id-info.jihs.go.jp/surveillance/idwr/

## Data Pipeline Architecture

### Data Types and Date Ranges

The system handles 4 distinct data types, each with different historical ranges and URL patterns:

1. **Zensu (総数)** - Total case counts
   - 2012W37 onwards
   - Path changed to `/jp/rapid/` from 2025W12

2. **Teiten (定点)** - Sentinel surveillance data (major diseases: influenza, COVID-19, RSV, etc.)
   - 2012W37 onwards
   - Path changed to `/jp/rapid/` from 2025W01

3. **Trend (トレンド)** - 10-year historical comparison data
   - 2012W37 onwards
   - Path changed to `/jp/rapid/` from 2025W11
   - Special wide-table format preserving 52 weeks of historical data

4. **ARI (急性呼吸器感染症)** - Acute respiratory infections
   - 2025W15 onwards (newer dataset)
   - Always uses `/jp/rapid/` path

### URL Pattern Changes

The data source URL structure changed over time:
- **2012W37-2023W01**: Old format using `/niid/images/idwr/sokuho/idwr-{year}/{yearweek}/`
- **2023W02+**: New format using `/surveillance/idwr/rapid/{year}/{week}/`
- **2025+**: Some types migrated to `/surveillance/idwr/jp/rapid/` (see function download_csv in main.py:9-72 for exact logic)

### Processing Pipeline

The main.py script handles three operations:

1. **Download** (`uv run main.py download [data_type]`)
   - Downloads raw CSV files (Shift-JIS encoded) from source
   - Stores in `data/{type}/raw/`
   - Implements polite 0.5s delay between requests

2. **Clean/Process** (automatic during download)
   - Converts Shift-JIS → UTF-8
   - Parses multi-row headers (row 3: disease names, row 4: report types)
   - Generates column names as `{disease}_{report_type}`
   - Special handling for trend data: maintains wide-table format with 報告年, 報告週, 疾病, 年, 1週-52週
   - Stores cleaned CSVs in `data/{type}/processed/`

3. **Merge** (`uv run main.py merge [data_type]`)
   - Combines all processed files into single dataset
   - Calculates ISO week dates (start/end dates, month) using get_week_dates function
   - Adds columns: 年, 週, 月, 開始日, 終了日
   - Normalizes placeholders (-, ―, ー, −) to NA
   - Removes thousands separators and coerces numeric columns
   - Outputs both CSV and Parquet formats
   - Parquet uses snappy compression (typically 80-90% smaller than CSV)

### Running the Data Pipeline

```bash
# Download and process all data types
uv run main.py

# Download specific data type only
uv run main.py download zensu
uv run main.py download teiten
uv run main.py download ari
uv run main.py download trend

# Merge processed files only (assumes raw files exist)
uv run main.py merge zensu
uv run main.py merge teiten
uv run main.py merge ari
uv run main.py merge trend

# Update README statistics only
uv run main.py update-readme
```

## Web Application

### Technology Stack

- **Framework**: Vue 3 with Vue Router (hash mode)
- **Build Tool**: Vite
- **Package Manager**: Bun
- **Charts**: ECharts via vue-echarts
- **Deployment**: Cloudflare Pages via Wrangler

### Development Commands

```bash
cd web

# Install dependencies
bun install
# or
make install

# Development server (copies data automatically)
make dev
# or
bun run dev

# Production build (copies data automatically)
make build
# or
bun run build

# Preview production build
make preview

# Clean build artifacts and copied data
make clean

# Copy data files only (without build/dev)
make copy-data
```

### Application Structure

- `web/src/main.js` - Router setup with 5 views (Home, ARI, Teiten, Zensu, Trend)
- `web/src/views/` - View components for each data type
- `web/src/components/` - Reusable chart components:
  - TimeSeriesChart.vue
  - HeatmapCalendarChart.vue
  - PrefectureComparisonChart.vue
  - MultiSeriesChart.vue
  - HistoricalTrendChart.vue
  - HistoricalComparisonWidget.vue

### Data Access in Web App

The build process copies merged data files to `web/public/data/`:
- CSV files: compressed as `.zip` (for download links)
- Parquet files: direct copy for analysis tools

## GitHub Actions Workflows

### update-data.yml
- **Trigger**: Daily at 1:00 AM UTC (cron) or manual
- **Action**: Runs `uv run python main.py` to download/process all data
- **Auto-commit**: Commits changes to `data/` and `README.md` if data updated

### deploy.yml
- **Trigger**: Push to main (web/** or data/** paths), after update-data workflow, or manual
- **Actions**:
  1. Regenerates Parquet files via `uv run main.py merge`
  2. Builds web app with Bun
  3. Deploys to Cloudflare Pages
- **Note**: Parquet regeneration ensures latest data even if CSV was pre-generated

## Python Environment

- **Python Version**: 3.14+
- **Package Manager**: uv (preferred) or pip
- **Dependencies** (pyproject.toml):
  - pandas: Data manipulation
  - matplotlib: Visualization (for standalone plots)
  - pyarrow: Parquet file I/O

Setup: `uv sync`

## Data Format Notes

### Encoding
- Raw source files: Shift-JIS (Japanese encoding)
- All processed files: UTF-8

### Date Calculations
ISO 8601 week date system:
- Week 1 = week containing January 4th
- Weeks run Monday-Sunday
- Implemented in get_week_dates() (main.py:305-330)

### Column Naming Convention
Format: `{疾病名}_{報告タイプ}`
- Example: `インフルエンザ_定点当たり報告数`
- Example: `COVID-19_報告数`

### Trend Data Format
Wide table with columns:
- 報告年, 報告週: When the report was generated
- 疾病: Disease name
- 年: Historical year being reported
- 1週, 2週, ..., 52週: Weekly values for that historical year

## Important File Locations

- `main.py` - Complete data pipeline logic
- `data/{type}/raw/` - Original Shift-JIS CSV files
- `data/{type}/processed/` - Cleaned UTF-8 CSV files
- `data/{type}/merged_{type}.csv` - Combined dataset (all weeks)
- `data/{type}/merged_{type}.parquet` - Combined dataset (Parquet format)
- `web/public/data/` - Build-time copy of data for web app
- `.github/workflows/` - Automated data update and deployment

## Data Licensing

Data is provided by 国立健康危機管理研究機構. See DATA_LICENSE.md and 利用規約.md for usage terms.
