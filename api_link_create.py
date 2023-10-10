from app import *

base_url = base_url = "http://127.0.0.1:5000"

def mentor_confirm_link(mentor, contestant):
    # Construct the complete URL for the mentor_confirm endpoint with query parameters
    endpoint = "/mentor_confirm"
    query_parameters = f"?mentor={mentor}&contestant={contestant}"
    full_url = f"{base_url}{endpoint}{query_parameters}"

    return full_url
