import requests
import time

# Set the URL for the Puppet Code Manager API
CODE_MANAGER_API_URL = "https://your-puppet-server:8170/code-manager/v1"
TOKEN = "your-rbac-token"  # Replace with your actual token
HEADERS = {
    "Content-Type": "application/json",
    "X-Authentication": TOKEN
}

def trigger_deploy_all(wait=True):
    url = f"{CODE_MANAGER_API_URL}/deploys"
    response = requests.post(url, headers=HEADERS)
    
    if response.status_code == 202:
        print("Deploy triggered for all environments.")
        if wait:
            check_deploy_status(response.json()['deploy_id'])
    else:
        print(f"Failed to trigger deploy. Status code: {response.status_code}")
        print(response.text)

def trigger_deploy_specific(environment, wait=True):
    url = f"{CODE_MANAGER_API_URL}/deploys"
    data = {
        "environments": [environment]
    }
    response = requests.post(url, headers=HEADERS, json=data)
    
    if response.status_code == 202:
        print(f"Deploy triggered for environment: {environment}.")
        if wait:
            check_deploy_status(response.json()['deploy_id'])
    else:
        print(f"Failed to trigger deploy for {environment}. Status code: {response.status_code}")
        print(response.text)

def check_deploy_status(deploy_id):
    url = f"{CODE_MANAGER_API_URL}/deploys/{deploy_id}"
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            status = response.json()['state']
            print(f"Deploy status: {status}")
            if status in ['complete', 'failed', 'cancelled']:
                break
        else:
            print(f"Failed to check deploy status. Status code: {response.status_code}")
            print(response.text)
            break
        time.sleep(10)

# Example usage
trigger_deploy_all(wait=True)
# trigger_deploy_specific("production", wait=True)

