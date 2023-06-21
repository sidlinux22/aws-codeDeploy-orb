#!/bin/bash
# Check if boto3 is installed
if ! python3 -c "import boto3" >/dev/null 2>&1; then
    echo "boto3 is not installed. Installing..."
    pip3 install boto3 > /dev/null
fi

# Define the URL for the Python script
script_url="https://raw.githubusercontent.com/sidlinux22/aws-codeDeploy-orb/dev-0.0.1/src/scripts/aws-codeDeploy-orb.py"

# Retrieve Python script from GitHub and save it as a file
curl -sSLJO "$script_url"

# Run the Python script with the parameters and capture the output
PRE_Deployment_ID=$(python3 aws-codeDeploy-orb.py --get-deployment-id "${APP_NAME}" "${DEPLOY_GROUP_NAME}")

# Print the result
echo "Latest Deployment ID is $PRE_Deployment_ID"

# Export the variable to the $BASH_ENV file
echo "export PRE_Deployment_ID=$PRE_Deployment_ID" >> "$BASH_ENV"