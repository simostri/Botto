# analysis/data_loader.py

import pandas as pd
import json
from pathlib import Path
from typing import List, Tuple, Optional

def load_etfs_from_json(json_file: str) -> List[Tuple[str, str]]:
    with open(json_file, 'r') as f:
        return [(item['file'], item['name']) for item in json.load(f)]

def read_etf_data(filepath: Path, start_date: pd.Timestamp, end_date: Optional[pd.Timestamp]) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=['Date'], usecols=['Date', 'Close'], index_col='Date')
    df.index = pd.to_datetime(df.index, utc=True)
    df.index = pd.to_datetime(df.index.date)  # normalize to date only
    return df.loc[start_date:end_date] if end_date else df.loc[start_date:]
