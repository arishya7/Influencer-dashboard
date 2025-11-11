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

        if total is not None:
            st.session_state.total_results = total

        return df

    except Exception as e:
        st.error(f"Failed to load data from API: {e}")
        return pd.DataFrame()

def login_user(username, password):
    """Authenticate user and retrieve access token."""
    try:
        response = requests.post(
            f"{API_URL}/login", 
            json={"username": username, "password": password},
            timeout=10
        )
        
        # Check status code before raising
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token", None)
        elif response.status_code == 401:
            print("Invalid credentials provided")
            return None
        else:
            st.error(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
    
#ADD COLUMN
def add_influencer_column(column_name):
    """Add a new influencer column via API."""
    try:
        payload = {"column": column_name}
        response = requests.post(
            f"{API_URL}/influencers/add-column", 
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to add influencer column: {e}")
        return None
    
#ADD ROW
def add_influencer_row(row_data):
    """Add a new influencer row via API."""
    try:
        response = requests.post(
            f"{API_URL}/influencers/add-row", 
            json=row_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to add influencer row: {e}")
        return None
    
def update_creator(creator_id, update_data):
    """PATCH update to an existing creator."""
    try:
        response = requests.patch(
            f"{API_URL}/influencers/update-creator/{creator_id}",
            json=update_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to update creator: {e}")
        return None

def save_added_columns(rows):
    try:
        payload = {"rows": rows}
        response = requests.post(
            f"{API_URL}/influencers/save-added",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to save added column changes: {e}")
        return None
def export_influencers_csv(username):
    try:
        response = requests.get(
            f"{API_URL}/influencers/export",
            params={"username": username},
            timeout=10
        )
        if response.status_code == 200:
            return response.text  
        else:
            return None
    except:
        return None
def update_mentions(creator_id, mentions_list):
    try:
        response = requests.patch(
            f"{API_URL}/influencers/update-mentions/{creator_id}",
            json={"mentions": mentions_list},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to save mentions: {e}")
        return None
