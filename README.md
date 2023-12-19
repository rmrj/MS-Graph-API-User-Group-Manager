# MS-Graph-API-User-Group-Manager
# Microsoft Graph API User Group Management Tool

## Overview
This tool utilizes the Microsoft Graph API to manage user groups based on application access. It reads user data from a CSV file and updates groups on Microsoft 365 accordingly.

## Features
- Authenticate with Microsoft Azure AD using MSAL.
- Read user and application data from a CSV file.
- Create or update user groups in Microsoft 365.
- Add users to respective groups based on application access.

## Requirements
- Python 3.x
- MSAL Python library
- `requests` library

## Setup
1. Install the required Python libraries:
   ```bash
   pip install msal requests
## Set the required environment variables:
export MSAL_CLIENT_ID='Your-Client-ID'
export MSAL_CLIENT_SECRET='Your-Client-Secret'
export MSAL_TENANT_ID='Your-Tenant-ID'
export CUSTOM_DOMAIN='Your-Custom-Domain'
