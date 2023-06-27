# CircleCi Orbs [sidlinux22/aws-code-deploy](https://circleci.com/developer/orbs/orb/sidlinux22/aws-code-deploy)

[![CircleCI Build Status](https://circleci.com/gh/sidlinux22/aws-codeDeploy-orb.svg?style=shield "CircleCI Build Status")](https://circleci.com/gh/sidlinux22/aws-codeDeploy-orb) [![CircleCI Orb Version](https://badges.circleci.com/orbs/sidlinux22/aws-codeDeploy-orb.svg)](https://circleci.com/developer/orbs/orb/sidlinux22/aws-codeDeploy-orb) [![GitHub License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://raw.githubusercontent.com/sidlinux22/aws-codeDeploy-orb/master/LICENSE) [![CircleCI Community](https://img.shields.io/badge/community-CircleCI%20Discuss-343434.svg)](https://discuss.circleci.com/c/ecosystem/orbs)


This CircleCi Orb is designed to interact with AWS CodeDeploy and retrieve deployment-related information. It has several functions to perform different tasks related to CodeDeploy deployments.

## Script Components

1. Import Statements:
   - The script imports necessary modules such as `os`, `sys`, `boto3`, `time`, `logging`, and `ThreadPoolExecutor` from the `concurrent.futures` module.

2. Logging Configuration:
   - The logging module is configured to log messages with a specific format and level.

3. `fetch_target_deployment` Function:
   - This function fetches information about a target deployment in CodeDeploy.
   - It takes the `application_name`, `deployment_group_name`, and `pre_deploy_id` as input parameters.
   - It uses the `boto3` client for CodeDeploy to retrieve the deployment information.
   - The function waits for the deployment to start and checks for any errors or timeouts.
   - It returns the `deploy_id` and `instance_ids` associated with the deployment.

4. `fetch_target_status` Function:
   - This function retrieves the status of a specific target instance in a CodeDeploy deployment.
   - It takes the `deploy_id` and `target_id` as input parameters.
   - It uses the `boto3` client for CodeDeploy to fetch the target's status.
   - It returns the `target_id` and `status` of the target instance.

5. `fetch_code_deploy_status` Function:
   - This function fetches the status of all target instances in a CodeDeploy deployment.
   - It calls the `fetch_target_deployment` function to get the `deploy_id` and `instance_ids`.
   - It continuously checks the status of each instance in the deployment until completion.
   - It counts the instances in different status categories such as completed, in progress, failed, stopped, pending, ready, and skipped.
   - It checks for various conditions such as completion, failure, timeouts, and returns appropriate exit codes.

6. `fetch_deployment_id` Function:
   - This function retrieves the deployment ID for a specified application and deployment group.
   - It takes the `application_name` and `deployment_group_name` as input parameters.
   - It uses the `boto3` client for CodeDeploy to fetch the deployment ID.
   - It prints the deployment ID and logs the information.

7. Main Execution Block:
   - The script checks the command-line arguments provided and validates them.
   - It determines the appropriate action based on the provided flag (`--get-deployment-status` or `--get-deployment-id`).
   - It retrieves the `application_name` and `deployment_group_name` from the command-line arguments.
   - If the flag is `--get-deployment-status`, it

 fetches the `pre_deploy_id` and calls the `fetch_code_deploy_status` function.
   - If the flag is `--get-deployment-id`, it calls the `fetch_deployment_id` function.
   - It handles any errors that occur during execution and logs them.
   - It exits with an appropriate exit code based on the execution result.

This script is designed to be run from the command line and provides two main functionalities: fetching the status of a CodeDeploy deployment and retrieving the deployment ID. It utilizes the `boto3` library to interact with AWS CodeDeploy and requires AWS credentials to be set up properly.

Please note that certain values in the script, such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`, are expected to be provided as environment variables. Additionally, when running the script, specific command-line arguments are required depending on the desired functionality.

For detailed usage instructions, you can refer to the comments in the `__main__` block of the script, which provide usage examples for each flag.

---

## Resources

- [CircleCI Orb Registry Page](https://circleci.com/developer/orbs/orb/sidlinux22/aws-code-deploy) - The official registry page of this orb for all versions, executors, commands, and jobs described.
- [CircleCI Orb Docs](https://circleci.com/docs/orb-intro/#section=configuration) - Docs for using, creating, and publishing CircleCI Orbs.

### How to Contribute

We welcome [issues](https://github.com/sidlinux22/aws-codeDeploy-orb/issues) and [pull requests](https://github.com/sidlinux22/aws-codeDeploy-orb/pulls) to this repository!

### How to Publish An Update

1. Merge pull requests with desired changes to the main branch.
    - For the best experience, squash-and-merge and use [Conventional Commit Messages](https://conventionalcommits.org/).
2. Find the current version of the orb.
    - You can run `circleci orb info sidlinux22/aws-code-deploy | grep "Latest"` to see the current version.
3. Create a [new Release](https://github.com/sidlinux22/aws-code-deploy/releases/new) on GitHub.
    - Click "Choose a tag" and create a new [semantically versioned](http://semver.org/) tag (e.g., v1.0.0).
      - We will have an opportunity to change this before we publish if needed after the next step.
4. Click "+ Auto-generate release notes".
    - This will create a summary of all the merged pull requests since the previous release.
    - If you have used [Conventional Commit Messages](https://conventionalcommits.org/), it will be easy to determine what types of changes were made, allowing you to ensure the correct version tag is being published.
5. Ensure the selected version tag is semantically accurate based on the included changes.
6. Click "Publish Release".
    - This will push a new tag and trigger your publishing pipeline on CircleCI.
