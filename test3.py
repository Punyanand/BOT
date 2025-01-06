import requests

# Replace with your actual PagerDuty API key
PAGERDUTY_API_KEY = "u+ijzSKE6mAqvt8_DG4A"

# Replace with the URL of your Slack webhook endpoint
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

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

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    This will be triggered when the Lambda function is invoked.
    """
    print("Lambda function started.")

    # Step 1: Get users without a phone number
    users_without_phone_number = list_users_without_phone_number()
    print("\nSummary: Users without a phone number")
    for user in users_without_phone_number:
        print(f"- {user['name']} (ID: {user['id']})")

    # Step 2: Send a summary message to Slack
    if users_without_phone_number:
        slack_message = "The following users do not have a phone number:\n"
        for user in users_without_phone_number:
            slack_message += f"- {user['name']} (ID: {user['id']})\n"
        send_slack_message(slack_message)
    else:
        send_slack_message("All users have a phone number.")

    return {
        "statusCode": 200,
        "body": "Execution completed successfully"
    }

if __name__ == "__main__":
    # This part will not be executed in AWS Lambda
    users_without_phone_number = list_users_without_phone_number()
    print("\nSummary: Users without a phone number")
    for user in users_without_phone_number:
        print(f"- {user['name']} (ID: {user['id']})")
