# About 
This a helping material to properly deploy your custom agent created with ADK to Agent Engine and AgentSpace. 
Last update data: `25 Aug 2025` - please keep in mind this is can change with any new update, consult requirements.txt for proper versions and check the documentation for updates. 

## Create ADK agent 

TO BE FILLED. 

## How to Deploy your Agent to AgentSpace 

1. Create your agent using ADK 
    - if you have any authentication required make sure to utilize `f"temp:{agentspace_auth_id}"` inside your auth_tools, this tool shall be used at the start 
    - for local development of for the deployment on other platforms use classic Credentials API with Oauth2
    - test your agent with ADK Web, do not proceed till this agent is fully functioning 
2. Deploy your ADK agent to Agent Engine 
    - use local_test script to validate that your `app` folder will be properly serialized and called 
    - follow the instructions of setting .env, requirements.txt and extra-packages from the documentation 
    - deploy using api 
3. Deploy to AgentSpace 
    - before deploying create authorization with the script create_auth(make sure it has a unique name per agent deployed)
    - list your current agents (make sure you new agent has a unique name)
    - use script create_agent to deploy to AgentSpace 
        - pay attention to the region, EU anf global will have different URLs and may break the flow.
     
## IMPORTANT TO READ 
Here is what you need to avoid/do, to make is a success: 
- XX
- XX
- 
## Things to do for improvement: 
TO BE FILLED 
