import requests
# Replace with your actual PagerDuty API key
PAGERDUTY_API_KEY = "u+ijzSKE6mAqvt8_DG4A"

# Replace with the URL of your Slack webhook endpoint
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# def get_latest_incident():
#     """
#     Fetch the latest triggered incident from PagerDuty.

#     Returns:
#         dict: A dictionary containing the incident details, or None if no incident is found.
#     """
#     url = "https://api.pagerduty.com/incidents"
#     headers = {
#         "Authorization": f"Token token={PAGERDUTY_API_KEY}",
#         "Accept": "application/vnd.pagerduty+json;version=2"
#     }
#     params = {
#         "statuses[]": "triggered",  # Only triggered incidents
#         "sort_by": "created_at:desc",  # Sort by most recent
#         "limit": 1  # Fetch only the most recent incident
#     }

#     try:
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()
#         data = response.json()

#         # Check for incidents in the response
#         if "incidents" in data and data["incidents"]:
#             return data["incidents"][0]  # Return the most recent incident
#         return None
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching incidents: {e}")
#         return None

def send_slack_message(message):
    """
    Sends a message to the specified Slack webhook URL.

    Args:
        message (str): The message to be sent.
    """
    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Message sent to Slack.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack message: {e}")

# if __name__ == "__main__":
#     # Fetch the most recent triggered incident
#     latest_incident = get_latest_incident()

#     if not latest_incident:
#         print("No triggered incidents found.")
#         send_slack_message("No triggered incidents found.")
#     else:
#         # Extract details from the incident
#         incident_title = latest_incident.get("title", "No title provided")
#         incident_description = latest_incident.get("description", "No description provided")
#         incident_url = latest_incident.get("html_url", "No URL available")

#         # Format the Slack message
#         message = (
#             f"*Incident Triggered*\n"
#             f"Title: {incident_title}\n"
#             f"Description: {incident_description}\n"
#             f"More Details: {incident_url}"
#         )

#         # Log and send the message to Slack
#         print(message)
#         send_slack_message(message)
