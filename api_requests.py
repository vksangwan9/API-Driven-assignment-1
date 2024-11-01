import requests
from pprint import pprint, pformat
from datetime import datetime
import credentials
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

base_url = f"https://api.prefect.cloud/api/accounts/{credentials.account_id}/workspaces/{credentials.workspace_id}"
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

# Function to get deployments
def get_deployment(deployment_id):
    url = f"{base_url}/deployments/{deployment_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        deployment_data = response.json()
        logger.info("Deployment data retrieved:\n%s", pformat(deployment_data))
        return deployment_data
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve deployment data:\n%s", pformat({"deployment_id": deployment_id, "error": str(e)}))
        return None

# Function to display deployment details
def display_deployment_info(deployment, pipeline_name):
    if deployment:
        try:
            details = {
                "Name of deployment": deployment.get("name"),
                "Flow ID": deployment.get("flow_id"),
                "Created at": datetime.strptime(deployment["created"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%m-%Y %H:%M:%S %Z"),
                "Last Updated at": datetime.strptime(deployment["updated"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%m-%Y %H:%M:%S %Z"),
                "Schedule": deployment.get("schedule", {}).get("cron"),
                "Tags": deployment.get("tags", [])
            }
            logger.info("Details about deployment for %s:\n%s", pipeline_name, pformat(details))
        except KeyError as e:
            logger.error("Error in deployment details:\n%s", pformat({"pipeline_name": pipeline_name, "error": str(e)}))
    else:
        logger.warning("No deployment data available for %s", pipeline_name)

def get_flow(flow_name):
    url = f"{base_url}/flows/{flow_name}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        flow_data = response.json()
        logger.info("Flow data retrieved:\n%s", pformat(flow_data))
        return flow_data
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve flow data:\n%s", pformat({"flow_name": flow_name, "error": str(e)}))
        return None

def display_flow_run_details(flow_run, pipeline_name):
    if flow_run:
        try:
            details = {
                "Flow Run ID": flow_run.get("id"),
                "Flow Name": flow_run.get("name"),
                "Created at": datetime.strptime(flow_run["created"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%m-%Y %H:%M:%S %Z"),
                "Updated at": datetime.strptime(flow_run["updated"], "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%d-%m-%Y %H:%M:%S %Z")
            }
            logger.info("Last successful flow for %s:\n%s", pipeline_name, pformat(details))
        except KeyError as e:
            logger.error("Error in flow run details:\n%s", pformat({"pipeline_name": pipeline_name, "error": str(e)}))
    else:
        logger.warning("No successful flow runs found for %s", pipeline_name)

def get_logs(logs_count):
    url = f"{base_url}/logs/filter"
    data = {
        "offset": 0,
        "sort": "TIMESTAMP_ASC",
        "logs": {
            "operator": "and_",
            "flow_run_id": {
                "any_": [
                    credentials.data_processing_flow_run_id, credentials.machine_learning_flow_run_id
                ]
            }
        },
        "limit": logs_count
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logs = response.json()
        if logs:
            logger.info("Logs retrieved:\n%s", pformat(logs))
        else:
            logger.info("No logs found for the given run.")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to retrieve logs:\n%s", pformat({"error": str(e)}))

def main():
    while True:
        print("\n" + "*"*100)
        print("\nMenu:")
        print("1. Get DataOps pipeline deployment details")
        print("2. Get MLOps pipeline deployment details")
        print("3. Get DataOps flow details")
        print("4. Get MLOps flow details")
        print("5. Get logs")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")
        print("\n" + "#"*100)

        if choice == "1":
            deployment = get_deployment(credentials.data_pipeline_deployment_id)
            display_deployment_info(deployment, 'DataOps')
        elif choice == "2":
            deployment = get_deployment(credentials.ml_pipeline_deployment_id)
            display_deployment_info(deployment, 'MLOps')
        elif choice == "3":
            flow_run = get_flow(credentials.data_processing_flow_id)
            display_flow_run_details(flow_run, "DataOps")
        elif choice == "4":
            flow_run = get_flow(credentials.machine_learning_flow_id)
            display_flow_run_details(flow_run, "MLOps")
        elif choice == "5":
            try:
                logs_count = int(input("Enter the number of latest logs to fetch: "))
                get_logs(logs_count)
            except ValueError:
                logger.error("Invalid input for logs count. Please enter an integer.")
        elif choice == "6":
            logger.info("Exiting program. Goodbye!")
            break
        else:
            logger.warning("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()