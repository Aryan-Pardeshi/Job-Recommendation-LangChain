import requests
import streamlit as st

@st.cache_data
def get_location_by_ip() -> str:
    """Fetches the user's current city and country based on their public IP."""
    try:
        # Use ip-api which has a very generous free tier (45 req/minute)
        response = requests.get('http://ip-api.com/json/', timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            city = data.get("city", "")
            country = data.get("country", "")
            return f"{city}, {country}".strip(", ")
        return "Unknown"
    except Exception:
        # Fallback if the API fails, blocks the request, or times out
        return "Unknown"
