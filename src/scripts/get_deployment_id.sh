#!/bin/bash

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if pip3 is installed
if ! command_exists pip3; then
    echo "pip3 is not installed. Installing..."
    if command_exists apt-get; then
        sudo apt-get update  > /dev/null
        sudo apt-get install -y python3-pip  > /dev/null
        elif command_exists dnf; then
        sudo dnf install -y python3-pip  > /dev/null
        elif command_exists brew; then
        brew install python3  > /dev/null
    else
        echo "Unable to install pip3."
        exit 1
    fi
fi

# Check if boto3 is installed
if ! python3 -c "import boto3" >/dev/null 2>&1; then
    echo "boto3 is not installed. Installing..."
    pip3 install boto3 > /dev/null
fi

# Define the URL for the Python script
script_url="https://raw.githubusercontent.com/sidlinux22/aws-codeDeploy-orb/0.1.2/src/scripts/aws_codeDeploy_orb.py"

# Retrieve Python script from GitHub and save it as a file
curl -sSLJO "$script_url"

# Run the Python script with the parameters and capture the output
PRE_Deployment_ID=$(python3 aws_codeDeploy_orb.py --get-deployment-id "${APP_NAME}" "${DEPLOY_GROUP_NAME}")

# Print the result
echo "Latest Deployment ID is $PRE_Deployment_ID"

# Export the variable to the $BASH_ENV file
echo "export PRE_Deployment_ID=$PRE_Deployment_ID" >> "$BASH_ENV"