#!/bin/bash

# Check if boto3 is installed
if ! python3 -c "import boto3" >/dev/null 2>&1; then
    echo "boto3 is not installed. Installing..."
    pip3 install boto3 >/dev/null
fi

# Check if PRE_Deployment_ID is null or empty
if [[ -z "${PRE_Deployment_ID}" ]]; then
    echo "ERROR: PRE_Deployment_ID is missing or empty. Run the 'get-deployment-id' step to fetch the pre-deployment ID."
    exit 1
fi

# Define the URL for the Python script
script_url="https://raw.githubusercontent.com/sidlinux22/aws-codeDeploy-orb/0.0.1/src/scripts/aws_codeDeploy_orb.py"

# Retrieve Python script from GitHub and save it as a file
curl -sSLJO "$script_url"

# Run the Python script with the parameters and capture the output
python3 aws_codeDeploy_orb.py --get-deployment-status "${APP_NAME}" "${DEPLOY_GROUP_NAME}" "${PRE_Deployment_ID}"