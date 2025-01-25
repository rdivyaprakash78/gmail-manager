import csv
from googleapiclient.errors import HttpError
from auth import main as get_gmail_service  # Import the main function from auth.py
import base64
import datetime


def decode_base64url(data):
    """Decodes a base64url-encoded string."""
    padding = '=' * (4 - len(data) % 4)  # Ensure proper padding
    data = data + padding
    return base64.urlsafe_b64decode(data).decode('utf-8')


def fetch_emails_for_keywords_and_combinations(keyword_combinations, output_file="emails.csv"):
    """
    Fetch a specific number of emails for each keyword/combo and save them to the same CSV file.
    """
    try:
        # Get the authenticated Gmail service
        service = get_gmail_service()

        email_data = []

        for keywords, num_emails in keyword_combinations.items():
            print(f"Fetching {num_emails} emails for keywords: '{keywords}'")

            # Build the query string for the keyword combination
            query = ' AND '.join([f"'{keyword}'" for keyword in keywords.split()])

            # Call the Gmail API to retrieve messages (limited to the specified number of emails)
            results = service.users().messages().list(userId='me', q=query, maxResults=num_emails).execute()
            messages = results.get('messages', [])

            if not messages:
                print(f"No emails found containing the keywords '{keywords}'.")
                continue

            for message in messages:
                # Retrieve the full email message
                msg = service.users().messages().get(userId='me', id=message['id']).execute()

                # Extract headers for subject and sender
                headers = msg['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
                sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")
                received_time = datetime.datetime.fromtimestamp(int(msg['internalDate']) / 1000).strftime('%Y-%m-%d %H:%M:%S')

                # Extract email body
                body = None
                parts = msg['payload'].get('parts', [])
                if parts:
                    for part in parts:
                        mime_type = part['mimeType']
                        if mime_type == 'text/plain' or mime_type == 'text/html':
                            data = part['body'].get('data')
                            if data:
                                body = decode_base64url(data)
                                break
                else:
                    # If no parts, check the main payload for body
                    if 'body' in msg['payload']:
                        data = msg['payload']['body'].get('data')
                        if data:
                            body = decode_base64url(data)

                if not body:
                    body = "No body content found."

                # Append the email details to the email_data list
                email_data.append({
                    "from": sender,
                    "subject": subject,
                    "body": body,
                    "received_time": received_time,
                    "keywords": keywords  # Include the keyword(s) in the output
                })

        # Write the email data to a CSV file (storing all results in the same file)
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["from", "subject", "body", "received_time", "keywords"])
            writer.writeheader()
            writer.writerows(email_data)

        print(f"Emails for all keyword combinations have been saved to '{output_file}'.")

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == '__main__':
    # Define a dictionary with keyword combinations as keys and number of emails to fetch as values
    keyword_combinations = {
        'unfortunately': 100,   # Fetch 100 emails with both 'invoice' and 'meeting' in them
        'confirmation application': 100,     # Fetch 75 emails with both 'invoice' and 'project'
        '': 100,      # Fetch 50 emails with both 'meeting' and 'report'
    }
    fetch_emails_for_keywords_and_combinations(keyword_combinations, "emails.csv")  # Store all results in the same file
