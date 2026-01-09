import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def download_csv(year: int, week: int, output_dir: Path, data_type: str = "zensu") -> Path | None:
    """
    Download CSV file for specified year and week

    Args:
        year: Year
        week: Week number (1-52)
        output_dir: Output directory
        data_type: Data type, "zensu", "ari", "teiten" or "trend"

    Returns:
        Path to downloaded file, or None if failed
    """
    # Build URL based on year and data type
    output_file = output_dir / f"{year}-{week:02d}-{data_type if data_type != 'trend' else 'trend'}.csv"
    
    # 2012W37 to 2022W52: Old format using /niid/images/idwr/sokuho/
    if (year == 2012 and week >= 37) or (2013 <= year <= 2022) or (year == 2023 and week <= 1):
        year_week_folder = f"{year}{week:02d}"
        if data_type == "trend":
            url = f"https://id-info.jihs.go.jp/niid/images/idwr/sokuho/idwr-{year}/{year_week_folder}/week{week:02d}-trend.csv"
        elif data_type in ["zensu", "teiten"]:
            url = f"https://id-info.jihs.go.jp/niid/images/idwr/sokuho/idwr-{year}/{year_week_folder}/{year}-{week:02d}-{data_type}.csv"
        else:  # ari - may not exist in old format, but use consistent pattern
            url = f"https://id-info.jihs.go.jp/niid/images/idwr/sokuho/idwr-{year}/{year_week_folder}/{year}-{week:02d}-{data_type}.csv"
    # 2023 onwards (from around week 2): New format using /surveillance/idwr/rapid/
    elif data_type == "trend":
        if year >= 2025 and week >= 11:
            url = f"https://id-info.jihs.go.jp/surveillance/idwr/jp/rapid/{year}/{week}/week{week:02d}-trend.csv"
        else:
            url = f"https://id-info.jihs.go.jp/surveillance/idwr/rapid/{year}/{week}/week{week:02d}-trend.csv"
    # Starting from 2025, teiten data path changed to /jp/rapid/
    # ari data always uses /jp/rapid/
    # zensu data path changed to /jp/rapid/ from 2025 week 12 onwards
    elif data_type == "zensu" and (year > 2025 or (year == 2025 and week >= 12)):
        url = f"https://id-info.jihs.go.jp/surveillance/idwr/jp/rapid/{year}/{week}/{year}-{week:02d}-{data_type}.csv"
    elif data_type == "ari" or (data_type == "teiten" and year >= 2025):
        url = f"https://id-info.jihs.go.jp/surveillance/idwr/jp/rapid/{year}/{week}/{year}-{week:02d}-{data_type}.csv"
    else:
        url = f"https://id-info.jihs.go.jp/surveillance/idwr/rapid/{year}/{week}/{year}-{week:02d}-{data_type}.csv"

    # Skip download if file already exists
    if output_file.exists():
        print(f"  File already exists: {output_file.name}")
        return output_file

    try:
        print(f"  Downloading: {url}")
        urllib.request.urlretrieve(url, output_file)
        print(f"  ✓ Saved to: {output_file.name}")
        time.sleep(0.5)  # Polite delay
        return output_file
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return None


def clean_csv(input_file: Path, output_file: Path, data_type: str = "zensu") -> bool:
    """
    Convert raw Shift-JIS encoded CSV to UTF-8 and clean headers

    Args:
        input_file: Input file path (Shift-JIS encoding)
        output_file: Output file path (UTF-8 encoding)
        data_type: Data type, used to determine file format

    Returns:
        Whether successful
    """
    try:
        # trend data has special format, parse wide table and reorganize into clear wide table format
        if data_type == "trend":
            df = pd.read_csv(input_file, encoding="shift_jis", header=None)
            
            # Extract year and week from filename
            filename_parts = input_file.stem.split("-")
            report_year = filename_parts[0]
            report_week = filename_parts[1]
            
            result_rows = []
            current_disease = None
            week_columns = []
            
            for idx in range(len(df)):
                row = df.iloc[idx]
                first_col = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                
                # Skip leading comments and empty lines
                if not first_col or first_col.startswith("注") or first_col.startswith("疾病"):
                    continue
                
                # Detect year range row (e.g., "2013年〜2023年")
                if "年〜" in first_col or "年～" in first_col:
                    continue
                
                # Detect disease name row (standalone row without year)
                if first_col and not first_col.endswith("年") and "週" not in str(row.iloc[1]):
                    # Check if next row is week header
                    if idx + 1 < len(df):
                        next_row = df.iloc[idx + 1]
                        if pd.notna(next_row.iloc[1]) and "週" in str(next_row.iloc[1]):
                            current_disease = first_col.strip()
                            # Extract week list
                            week_columns = []
                            for col_idx in range(1, len(next_row)):
                                col_val = next_row.iloc[col_idx]
                                if pd.notna(col_val) and "週" in str(col_val):
                                    week_num = str(col_val).replace("週", "").strip()
                                    week_columns.append((col_idx, week_num))
                    continue
                
                # Process data row (year + data)
                if first_col.endswith("年") and current_disease and week_columns:
                    year_str = first_col.replace("年", "").strip()
                    # Convert year format (e.g., "23年" -> "2023")
                    if len(year_str) == 2:
                        year = "20" + year_str if int(year_str) < 50 else "19" + year_str
                    else:
                        year = year_str
                    
                    # Build data for this row
                    row_data = {
                        "報告年": report_year,
                        "報告週": report_week,
                        "疾病": current_disease,
                        "年": year
                    }
                    
                    # Add weekly values
                    for col_idx, week_num in week_columns:
                        if col_idx < len(row):
                            value = row.iloc[col_idx]
                            if pd.notna(value) and str(value).strip() and str(value) != "-":
                                row_data[f"{week_num}週"] = str(value).strip()
                            else:
                                row_data[f"{week_num}週"] = ""
                    
                    result_rows.append(row_data)
            
            # Convert to DataFrame and save
            if result_rows:
                result_df = pd.DataFrame(result_rows)
                result_df.to_csv(output_file, index=False, encoding="utf-8")
            else:
                # If no data, create empty DataFrame
                result_df = pd.DataFrame(columns=["報告年", "報告週", "疾病", "年"])
                result_df.to_csv(output_file, index=False, encoding="utf-8")
            return True
        
        # Read raw CSV file (Shift-JIS encoding)
        df = pd.read_csv(input_file, encoding="shift_jis", header=None)

        # Extract row 3 (disease name) and row 4 (report/cumulative)
        disease_row = df.iloc[2]  # Row 3: disease name
        type_row = df.iloc[3]  # Row 4: report/cumulative

        # Build new column names
        new_columns = []
        current_disease = ""

        for i in range(len(disease_row)):
            disease = disease_row.iloc[i]
            report_type = type_row.iloc[i]

            # First column is region/prefecture column
            if i == 0:
                new_columns.append("都道府県")
                continue

            # If disease name is not empty, update current disease
            if pd.notna(disease) and str(disease).strip():
                current_disease = str(disease).strip()

            # Build column name: disease_name_report_type
            if pd.notna(report_type) and str(report_type).strip():
                report_type_str = str(report_type).strip()
                if current_disease:
                    new_columns.append(f"{current_disease}_{report_type_str}")
                else:
                    new_columns.append(report_type_str)
            else:
                new_columns.append(f"column_{i}")

        # Actual data starts from row 5
        data_df = df.iloc[4:].reset_index(drop=True)
        data_df.columns = new_columns

        # Add year and week information
        filename_parts = input_file.stem.split("-")
        if len(filename_parts) >= 2:
            data_df.insert(0, "年", filename_parts[0])
            data_df.insert(1, "週", filename_parts[1])

        # Save as UTF-8 encoded CSV
        data_df.to_csv(output_file, index=False, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  ✗ Processing failed: {e}")
        return False


def download_and_process_all(start_year: int = 2023, data_type: str = "zensu", start_week: int = 1):
    """
    Download and process all data starting from specified year

    Args:
        start_year: Starting year (default 2023)
        data_type: Data type, "zensu", "ari", "teiten" or "trend"
        start_week: Starting week for start_year (default 1)
    """
    current_year = datetime.now().year
    current_week = datetime.now().isocalendar()[1]

    raw_dir = Path(f"data/{data_type}/raw")
    processed_dir = Path(f"data/{data_type}/processed")

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    total_downloaded = 0
    total_processed = 0
    total_failed = 0

    print(f"Starting to download {data_type.upper()} data from {start_year}W{start_week:02d} to present...\n")

    for year in range(start_year, current_year + 1):
        # Determine starting week and max week for this year
        min_week = start_week if year == start_year else 1
        max_week = current_week if year == current_year else 52

        print(f"📅 {year} (Week {min_week}-{max_week})")

        for week in range(min_week, max_week + 1):
            # Download raw file
            raw_file = download_csv(year, week, raw_dir, data_type)

            if raw_file:
                total_downloaded += 1

                # Process file
                processed_file = processed_dir / f"{year}-{week:02d}-{data_type}-clean.csv"

                if processed_file.exists():
                    print(f"  Processed file already exists: {processed_file.name}")
                    total_processed += 1
                else:
                    print(f"  Processing: {raw_file.name}")
                    if clean_csv(raw_file, processed_file, data_type):
                        print(f"  ✓ Saved to: {processed_file.name}")
                        total_processed += 1
                    else:
                        total_failed += 1
            else:
                total_failed += 1

        print()  # Empty line separator between years

    print("=" * 60)
    print("📊 Summary:")
    print(f"  - Downloaded files: {total_downloaded}")
    print(f"  - Successfully processed: {total_processed}")
    print(f"  - Failed: {total_failed}")
    print(f"  - Raw data directory: {raw_dir}")
    print(f"  - Processed data directory: {processed_dir}")
    print("=" * 60)


def get_week_dates(year: int, week: int) -> tuple[str, str, int]:
    """
    Calculate start and end dates based on ISO week
    
    Args:
        year: Year
        week: ISO week number
    
    Returns:
        Tuple of (start_date, end_date, month)
    """
    # First day of ISO week is Monday
    # Find Monday of week 1 of the year
    jan_4 = datetime(year, 1, 4)  # ISO 8601: week containing Jan 4 is week 1
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    
    # Calculate Monday of target week
    target_monday = week_1_monday + timedelta(weeks=week - 1)
    # Calculate Sunday
    target_sunday = target_monday + timedelta(days=6)
    
    start_date = target_monday.strftime("%Y-%m-%d")
    end_date = target_sunday.strftime("%Y-%m-%d")
    month = target_monday.month
    
    return start_date, end_date, month


def merge_all_csv(data_type: str = "zensu"):
    """
    Merge all processed CSV files and add complete date information
    
    Args:
        data_type: Data type, "zensu", "ari", "teiten" or "trend"
    """
    processed_dir = Path(f"data/{data_type}/processed")
    output_csv = Path(f"data/{data_type}/merged_{data_type}.csv")
    output_parquet = Path(f"data/{data_type}/merged_{data_type}.parquet")
    
    print("\n" + "=" * 60)
    print(f"Starting to merge all {data_type.upper()} CSV files...")
    print("=" * 60)
    
    # Get all processed CSV files
    csv_files = sorted(processed_dir.glob(f"*-{data_type}-clean.csv"))
    
    if not csv_files:
        print("❌ No processed CSV files found!")
        return
    
    print(f"📁 Found {len(csv_files)} files")
    
    all_data = []
    
    for csv_file in csv_files:
        # Extract year and week from filename
        filename = csv_file.stem  # e.g.: "2023-01-zensu-clean"
        parts = filename.split("-")
        year = int(parts[0])
        week = int(parts[1])
        
        # Read CSV
        try:
            df = pd.read_csv(csv_file)
            
            # Calculate date information
            start_date, end_date, month = get_week_dates(year, week)
            
            # Add date columns (if not exist)
            if "年" not in df.columns:
                df.insert(0, "年", year)
            if "週" not in df.columns:
                df.insert(1, "週", week)
            
            # Add new date columns
            df.insert(2, "月", month)
            df.insert(3, "開始日", start_date)
            df.insert(4, "終了日", end_date)
            
            all_data.append(df)
            
        except Exception as e:
            print(f"  ✗ Failed to read file {csv_file.name}: {e}")
            continue
    
    if not all_data:
        print("❌ No data was successfully read!")
        return
    
    # Merge all data
    print(f"\n📊 Merging {len(all_data)} datasets...")
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Save merged CSV file
    merged_df.to_csv(output_csv, index=False, encoding="utf-8")
    
    # Save merged Parquet file
    print("💾 Saving Parquet file...")
    try:
        merged_df.to_parquet(output_parquet, index=False, engine="pyarrow", compression="snappy")
        parquet_size = output_parquet.stat().st_size / 1024 / 1024
        print(f"  ✓ Parquet file saved: {output_parquet}")
        print(f"  ✓ Parquet size: {parquet_size:.2f} MB")
    except Exception as e:
        print(f"  ✗ Failed to save Parquet file: {e}")
        print("  ℹ️  You may need to install pyarrow: pip install pyarrow")
    
    print("\n" + "=" * 60)
    print("✅ Merge completed!")
    print(f"  - Total rows: {len(merged_df):,}")
    print(f"  - Total columns: {len(merged_df.columns)}")
    print(f"  - CSV output: {output_csv}")
    print(f"  - CSV size: {output_csv.stat().st_size / 1024 / 1024:.2f} MB")
    if output_parquet.exists():
        print(f"  - Parquet output: {output_parquet}")
        print(f"  - Parquet size: {output_parquet.stat().st_size / 1024 / 1024:.2f} MB")
        csv_size = output_csv.stat().st_size / 1024 / 1024
        parquet_size = output_parquet.stat().st_size / 1024 / 1024
        compression_ratio = (1 - parquet_size / csv_size) * 100
        print(f"  - Compression: {compression_ratio:.1f}% smaller")
    print("\nFirst 8 columns:")
    for col in merged_df.columns[:8]:
        print(f"  - {col}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    command = sys.argv[1] if len(sys.argv) > 1 else None
    data_type = sys.argv[2] if len(sys.argv) > 2 else "both"
    
    if command == "merge":
        # Only execute merge operation
        if data_type == "both":
            merge_all_csv("zensu")
            merge_all_csv("ari")
            merge_all_csv("teiten")
            merge_all_csv("trend")
        else:
            merge_all_csv(data_type)
    elif command == "download":
        # Only download, don't merge
        if data_type == "both":
            download_and_process_all(start_year=2012, start_week=37, data_type="zensu")
            download_and_process_all(start_year=2012, start_week=37, data_type="teiten")
            download_and_process_all(start_year=2012, start_week=37, data_type="trend")
            download_and_process_all(start_year=2025, start_week=15, data_type="ari")
        else:
            start_year = 2012 if data_type in ["zensu", "teiten", "trend"] else 2025
            start_week = 37 if data_type in ["zensu", "teiten", "trend"] else 15
            download_and_process_all(start_year=start_year, start_week=start_week, data_type=data_type)
    else:
        # Default: download and merge all data
        print("=" * 60)
        print("Download and process all data types")
        print("=" * 60)
        
        # Download zensu data (from 2012W37)
        download_and_process_all(start_year=2012, start_week=37, data_type="zensu")
        merge_all_csv("zensu")
        
        # Download teiten data (from 2012W37)
        download_and_process_all(start_year=2012, start_week=37, data_type="teiten")
        merge_all_csv("teiten")
        
        # Download trend data (from 2012W37)
        download_and_process_all(start_year=2012, start_week=37, data_type="trend")
        merge_all_csv("trend")
        
        # Download ari data (from 2025W15)
        download_and_process_all(start_year=2025, start_week=15, data_type="ari")
        merge_all_csv("ari")
        
        print("\n" + "=" * 60)
        print("✅ All data processing completed!")
        print("=" * 60)
