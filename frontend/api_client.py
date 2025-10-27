# api_client.py
import requests
import pandas as pd
import streamlit as st

API_URL = "http://api:8000/influencers"

def fetch_influencers(params=None):
    """Fetch influencer data and unpack nested JSON."""
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and "items" in data:
            items = data.get("items", [])
            total = data.get("total", None)
        else:
            items = data
            total = None

        df = pd.DataFrame(items)

        # Optionally attach total count
        if total is not None:
            st.session_state.total_results = total

        return df

    except Exception as e:
        st.error(f"Failed to load data from API: {e}")
        return pd.DataFrame()
