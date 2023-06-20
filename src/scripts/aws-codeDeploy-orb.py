import sys
import boto3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_target_deployment(application_name, deployment_group_name, pre_deploy_id):
    deploy_id = None
    instance_ids = []

    client = boto3.client("codedeploy")

    wait_period = 0
    response = client.get_deployment_group(
        applicationName=application_name,
        deploymentGroupName=deployment_group_name
    )
    deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]
    while deploy_id == pre_deploy_id:
        response = client.get_deployment_group(
            applicationName=application_name,
            deploymentGroupName=deployment_group_name
        )
        deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]

        if deploy_id == pre_deploy_id:
            wait_period += 3
            if wait_period > 180:
                print("[Script timeout]: Deployment ID didn't change within 180 seconds.")
                return None, []

            time.sleep(3)
        print("Waiting for Deployment to start...")
    response = client.list_deployment_instances(
        deploymentId=deploy_id
    )
    instance_ids = response["instancesList"]

    print(f"Latest deployment ID: {deploy_id}")
    print(f"Instance IDs: {instance_ids}")
    print()

    return deploy_id, instance_ids

def fetch_target_status(deploy_id, target_id):
    client = boto3.client("codedeploy")

    response = client.get_deployment_target(
        deploymentId=deploy_id,
        targetId=target_id
    )
    status = response["deploymentTarget"]["instanceTarget"]["status"]

    return target_id, status

def fetch_code_deploy_status(application_name, deployment_group_name, pre_deploy_id):
    deploy_id, instance_ids = fetch_target_deployment(application_name, deployment_group_name, pre_deploy_id)

    if deploy_id is None:
        print("Deployment ID doesn't match the pre-deploy ID.")
        return 1

    print(instance_ids)
    print()

    with ThreadPoolExecutor() as executor:
        wait_period = 0
        while True:
            time.sleep(3)
            completed_count = 0
            in_progress_count = 0
            futures = [executor.submit(fetch_target_status, deploy_id, target_id) for target_id in instance_ids]

            for future in as_completed(futures):
                target_id, status = future.result()
                print(f"Instance ID: {target_id}, Status: {status}")

                if status == "Succeeded":
                    completed_count += 1
                elif status == "InProgress":
                    in_progress_count += 1

            if completed_count == len(instance_ids):
                print("All instances Succeeded.")
                return 0

            if in_progress_count == 0 and completed_count < len(instance_ids):
                wait_period += 3
                if wait_period > 300:
                    print("[Script timeout]: Code-Deploy deployment not started within 300 seconds.")
                    return 1

                print("Waiting for Code-Deploy deployment to start...")

def fetch_deployment_id(application_name, deployment_group_name):
    client = boto3.client("codedeploy")

    response = client.get_deployment_group(
        applicationName=application_name,
        deploymentGroupName=deployment_group_name
    )
    deploy_id = response["deploymentGroupInfo"]["lastAttemptedDeployment"]["deploymentId"]

    print(f"Latest deployment ID: {deploy_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["--get-deployment-status", "--get-deployment-id"]:
        print("Usage: python script.py --get-deployment-status <application-name> <deployment-group-name> <pre-deploy-id>")
        print("       python script.py --get-deployment-id <application-name> <deployment-group-name>")
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
        print("Invalid flag.")
        exit_code = 1

    exit(exit_code)