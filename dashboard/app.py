import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

csv_path = BASE_DIR / "data" / "processed" / "insurance_clean.csv"

df = pd.read_csv(csv_path)

st.title("Insurance Risk Dashboard")

st.write(df.head())