import os
import sys
import boto3
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def fetch_target_deployment(application_name, deployment_group_name, pre_deploy_id):
    try:
        deploy_id = None
        instance_ids = []
        client = boto3.client("codedeploy")
        wait_period = 0
        response = client.get_deployment_group(
            applicationName=application_name,
            deploymentGroupName=deployment_group_name
        )
        deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]
        deployment_status = ""
        while deploy_id == pre_deploy_id or deployment_status == "Created" or deployment_status == "Pending":
            response = client.get_deployment_group(
                applicationName=application_name,
                deploymentGroupName=deployment_group_name
            )
            deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]
            deployment_status = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["status"]
            if deploy_id == pre_deploy_id:
                wait_period += 5
                wait_timeout = int(os.getenv("DEPLOYMENT_START_TIMEOUT", "180"))
                if wait_period > wait_timeout:
                    logger.error(f"[Script timeout]: CodeDeploy deployment didn't change within {wait_timeout} seconds.")
                    exit(1)

                time.sleep(5)
            logger.info("Waiting for CodeDeploy Deployment to start...")

        response = client.list_deployment_instances(
            deploymentId=deploy_id
        )
        instance_ids = response["instancesList"]

        logger.info(f"CodeDeploy deployment started. ID: {deploy_id}")
        logger.info(f"List of Instance IDs to be updated: {instance_ids}")

        return deploy_id, instance_ids
    except (boto3.exceptions.Boto3Error, KeyError) as e:
        logger.error(f"Error occurred while fetching target deployment: {str(e)}")
        exit(1)

def fetch_target_status(deploy_id, target_id):
    try:
        client = boto3.client("codedeploy")

        response = client.get_deployment_target(
            deploymentId=deploy_id,
            targetId=target_id
        )
        status = response["deploymentTarget"]["instanceTarget"]["status"]

        return target_id, status
    except (boto3.exceptions.Boto3Error, KeyError) as e:
        logger.error(f"Error occurred while fetching target status: {str(e)}")
        exit(1)

def fetch_code_deploy_status(application_name, deployment_group_name, pre_deploy_id):
    try:
        deploy_id, instance_ids = fetch_target_deployment(application_name, deployment_group_name, pre_deploy_id)

        if deploy_id is None:
            logger.error("Deployment ID doesn't match the pre-deploy ID.")
            return 1

        with ThreadPoolExecutor() as executor:
            wait_period = 0
            while True:
                time.sleep(5)
                completed_count = 0
                in_progress_count = 0
                failed_count = 0
                stopped_count = 0
                pending_count = 0
                ready_count = 0
                skipped_count = 0
                futures = [executor.submit(fetch_target_status, deploy_id, target_id) for target_id in instance_ids]

                for future in as_completed(futures):
                    target_id, status = future.result()
                    logger.info(f"Deployment status for Instance ID: {target_id}, Status: {status}")

                    if status == "Succeeded":
                        completed_count += 1
                    elif status == "InProgress":
                        in_progress_count += 1
                    elif status == "Failed":
                        failed_count += 1
                    elif status == "Stopped":
                        stopped_count += 1
                    elif status == "Pending":
                        pending_count += 1
                    elif status == "Ready":
                        ready_count += 1
                    elif status == "Skipped":
                        skipped_count += 1

                if completed_count == len(instance_ids):
                    logger.info("All instances succeeded.")
                    return 0

                if failed_count > 0:
                    logger.error(f"{failed_count} instances failed.")
                    return 1

                if stopped_count > 0:
                    logger.error(f"{stopped_count} instances stopped.")
                    return 1

                if skipped_count > 0:
                    logger.error(f"{skipped_count} instances skipped.")
                    return 1

                if in_progress_count == 0 and completed_count < len(instance_ids):
                    wait_period += 5
                    deploy_timeout = int(os.getenv("DEPLOYMENT_COMPLETION_TIMEOUT", "600"))
                    if wait_period > deploy_timeout:
                        logger.error(f"[Script timeout]: CodeDeploy deployment not completed in {deploy_timeout} seconds.")
                        return 1
    except (boto3.exceptions.Boto3Error, KeyError) as e:
        logger.error(f"Error occurred while fetching CodeDeploy status: {str(e)}")
        exit(1)

def fetch_deployment_id(application_name, deployment_group_name):
    try:
        client = boto3.client("codedeploy")

        response = client.get_deployment_group(
            applicationName=application_name,
            deploymentGroupName=deployment_group_name
        )
        deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]
        print(deploy_id)
        logger.info(f"Deployment ID: {deploy_id}")
    except (boto3.exceptions.Boto3Error, KeyError) as e:
        logger.error(f"Error occurred while fetching deployment ID: {str(e)}")
        exit(1)

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2 or sys.argv[1] not in ["--get-deployment-status", "--get-deployment-id"]:
            logger.error("Usage: python script.py --get-deployment-status <application_name> <deployment_group_name> <pre-deploy-id>")
            logger.error("       python script.py --get-deployment-id <application_name> <deployment_group_name>")
            exit(1)

        flag = sys.argv[1]
        application_name = sys.argv[2]
        deployment_group_name = sys.argv[3]

        if flag == "--get-deployment-status":
            pre_deploy_id = sys.argv[4]
            exit_code = fetch_code_deploy_status(application_name, deployment_group_name, pre_deploy_id)
        elif flag == "--get-deployment-id":
            fetch_deployment_id(application_name, deployment_group_name)
            exit_code = 0
        else:
            logger.error("Invalid flag.")
            exit_code = 1

        exit(exit_code)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        exit(1)