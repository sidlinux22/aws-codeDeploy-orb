
#!/bin/bash

# Retrieve Python script from GitHub
curl -sSLJO https://github.com/sidlinux22/aws-codeDeploy-orb/blob/main/src/scripts/aws-codeDeploy-orb.py

# Run the Python script with the parameters
PRE_Deployment_ID=$(python aws-codeDeploy-status.py $APP_NAME $DEPLOY_GROUP_NAME)

# Export the variable to the $BASH_ENV file
echo "export PRE_Deployment_ID=$PRE_Deployment_ID" >> $BASH_ENV

# Print the result
echo "Latest Deployment ID is $PRE_Deployment_ID"
