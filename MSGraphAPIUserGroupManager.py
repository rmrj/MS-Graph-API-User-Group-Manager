import csv
from msal import ConfidentialClientApplication
import requests
import os
import time

# Fetch credentials and domain from environment variables
CLIENT_ID = os.environ['MSAL_CLIENT_ID']
CLIENT_SECRET = os.environ['MSAL_CLIENT_SECRET']
TENANT_ID = os.environ['MSAL_TENANT_ID']
CUSTOM_DOMAIN = os.environ['CUSTOM_DOMAIN']

# Authenticate and obtain an access token
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
scopes = ["https://graph.microsoft.com/.default"]

app = ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=authority
)

result = app.acquire_token_silent(scopes=scopes, account=None)
if not result:
    result = app.acquire_token_for_client(scopes=scopes)
access_token = result['access_token']

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

csv_file_path = "<NAME_OF_THE_FILE>.csv"
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        app_name = row['app']
        users = row['users'].split(',')
        users = [user.strip() for user in users]
        
        display_name = f"{app_name}_users"
        mail_nickname = f"{app_name}_users"

       # Check if DL already exists
        check_dl_url = f"https://graph.microsoft.com/v1.0/groups?$filter=mailNickname eq '{mail_nickname}'"
        check_response = requests.get(check_dl_url, headers=headers)

        dl_exists = check_response.status_code == 200 and 'value' in check_response.json() and len(check_response.json()['value']) > 0

        if dl_exists:
            dl_id = check_response.json()['value'][0]['id']

            # Fetch the members of the DL
            get_members_url = f"https://graph.microsoft.com/v1.0/groups/{dl_id}/members"
            get_members_response = requests.get(get_members_url, headers=headers)
            
            if get_members_response.status_code == 200:
                current_members_data = get_members_response.json()
                current_members = [member['mail'] for member in current_members_data['value']]
            else:
                print(f"Failed to fetch members of DL {display_name}. HTTP status code: {get_members_response.status_code}")
                print(get_members_response.content)
                current_members = []

            new_users_to_add = [user for user in users if user not in current_members]
            
        else:
            # DL does not exist, create it
            create_dl_url = "https://graph.microsoft.com/v1.0/groups"
            payload = {
                "displayName": display_name,
                "mailEnabled": True,
                "mailNickname": mail_nickname,
                "securityEnabled": False,
                "groupTypes": ["Unified"],
                "resourceBehaviorOptions": ["WelcomeEmailDisabled"],
            }

            create_response = requests.post(create_dl_url, headers=headers, json=payload)
            if create_response.status_code == 201:
                new_dl = create_response.json()
                new_dl_id = new_dl['id']
        
                # Update the mailNickname property to match the desired email address
                update_dl_url = f"https://graph.microsoft.com/v1.0/groups/{new_dl_id}"
                update_payload = {
                    "mailNickname": mail_nickname
                }

                update_response = requests.patch(update_dl_url, headers=headers, json=update_payload)
                if update_response.status_code in [200, 204]:
                    print(f"Created DL: {display_name}")
                    time.sleep(10)  # Wait for 10 seconds after creating a group before adding members
                else:
                    print(f"Failed to update DL mailNickname for {display_name}. HTTP status code: {update_response.status_code}")
                    print(update_response.content)
            else:
                print(f"Failed to create DL: {display_name}. HTTP status code: {create_response.status_code}")
                print(create_response.content)
            new_users_to_add = users
            dl_id = new_dl['id']
        
        # After finding or creating the DL, disable the welcome message
        # disable_group_welcome_message(dl_id, headers)

        add_members_url = f"https://graph.microsoft.com/v1.0/groups/{dl_id}/members/$ref"
        for user_email in new_users_to_add:
            if not user_email.lower().startswith(('admin', 'service', 'ftp')) and "@rodanandfields" in user_email.lower():
                member_payload = {
                    "@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_email}"
                }
                
                add_members_response = requests.post(add_members_url, headers=headers, json=member_payload)
                if add_members_response.status_code == 204:
                    print(f"Added user {user_email} to the DL {display_name}")
                else:
                    print(f"Failed to add user {user_email} to the DL {display_name}. HTTP status code: {add_members_response.status_code}")
                    print(add_members_response.content)
            else:
                print(f"Skipping user {user_email}. Excluded from DL {display_name}.")



