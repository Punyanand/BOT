import requests

# Replace with your actual PagerDuty API key
PAGERDUTY_API_KEY = "u+ijzSKE6mAqvt8_DG4A"

# Replace with the URL of your Slack webhook endpoint
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

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

def get_all_users():
    """
    Fetch all users from PagerDuty.

    Returns:
        list: A list of user dictionaries, or an empty list if none are found.
    """
    url = "https://api.pagerduty.com/users"
    headers = {
        "Authorization": f"Token token={PAGERDUTY_API_KEY}",
        "Accept": "application/vnd.pagerduty+json;version=2"
    }
    users = []
    offset = 0
    limit = 100

    while True:
        params = {"limit": limit, "offset": offset}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Append users from the current page
            users.extend(data.get("users", []))

            # Break if no more users to fetch
            if not data.get("more"):
                break
            offset += limit
        except requests.exceptions.RequestException as e:
            print(f"Error fetching users: {e}")
            break

    return users

def get_user_contact_methods(user_id):
    """
    Fetch the contact methods for a specified user.

    Args:
        user_id (str): The ID of the user.

    Returns:
        list: A list of contact methods, or an empty list if none are found.
    """
    url = f"https://api.pagerduty.com/users/{user_id}/contact_methods"
    headers = {
        "Authorization": f"Token token={PAGERDUTY_API_KEY}",
        "Accept": "application/vnd.pagerduty+json;version=2"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("contact_methods", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contact methods for user {user_id}: {e}")
        return []

def list_users_without_phone_number():
    """
    Lists all users who do not have a phone contact number in PagerDuty.

    Returns:
        list: A list of user dictionaries for users without a phone number.
    """
    users_without_phone = []
    all_users = get_all_users()

    for user in all_users:
        user_id = user.get("id")
        user_name = user.get("name", "Unknown")
        contact_methods = get_user_contact_methods(user_id)

        # Debugging: Print the contact methods to see the structure
        print(f"Contact methods for {user_name} ({user_id}): {contact_methods}")

        # Check if there is a contact method with type 'phone_contact_method'
        has_phone = False
        for contact in contact_methods:
            if contact.get("type", "") == "phone_contact_method":
                has_phone = True
                break

        if not has_phone:
            print(f"User {user_name} ({user_id}) does not have a phone number.")
            send_slack_message(f"User {user_name} does not have a phone number.")
            users_without_phone.append({
                "id": user_id,
                "name": user_name
            })
        else:
            print(f"User {user_name} ({user_id}) has a phone number.")

    return users_without_phone

def get_latest_incident():
    """
    Fetch the latest triggered incident from PagerDuty.

    Returns:
        dict: A dictionary containing the incident details, or None if no incident is found.
    """
    url = "https://api.pagerduty.com/incidents"
    headers = {
        "Authorization": f"Token token={PAGERDUTY_API_KEY}",
        "Accept": "application/vnd.pagerduty+json;version=2"
    }
    params = {
        "statuses[]": "triggered",  # Only triggered incidents
        "sort_by": "created_at:desc",  # Sort by most recent
        "limit": 1  # Fetch only the most recent incident
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Check for incidents in the response
        if "incidents" in data and data["incidents"]:
            return data["incidents"][0]  # Return the most recent incident
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching incidents: {e}")
        return None

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    This will be triggered when the Lambda function is invoked.
    """
    print("Lambda function started.")

    # Step 1: Get the latest triggered incident and send to Slack
    latest_incident = get_latest_incident()

    if not latest_incident:
        print("No triggered incidents found.")
        send_slack_message("No triggered incidents found.")
    else:
        # Extract details from the incident
        incident_title = latest_incident.get("title", "No title provided")
        incident_description = latest_incident.get("description", "No description provided")
        incident_url = latest_incident.get("html_url", "No URL available")

        # Format the Slack message for the incident
        incident_message = (
            f"*Incident Triggered*\n"
            f"Title: {incident_title}\n"
            f"Description: {incident_description}\n"
            f"More Details: {incident_url}"
        )

        # Send the incident message to Slack
        print(incident_message)
        send_slack_message(incident_message)

    # Step 2: Get users without a phone number
    users_without_phone_number = list_users_without_phone_number()
    print("\nSummary: Users without a phone number")
    for user in users_without_phone_number:
        print(f"- {user['name']} (ID: {user['id']})")

    return {
        "statusCode": 200,
        "body": "Execution completed successfully"
    }

