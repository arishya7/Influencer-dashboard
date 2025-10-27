# api_client.py
import requests
import pandas as pd
import streamlit as st


INFLUENCER = "http://127.0.0.1:8000/influencers"
API_URL = "http://127.0.0.1:8000"

def fetch_influencers(params=None):
    """Fetch influencer data and unpack nested JSON."""
    try:
        response = requests.get(INFLUENCER, params=params)
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

def login_user(username, password):
    """Authenticate user and retrieve access token."""
    try:
        response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        response.raise_for_status()
        data = response.json()
        return data.get("access_token", None)
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None