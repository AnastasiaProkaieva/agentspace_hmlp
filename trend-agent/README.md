# About 
This a helping material to properly deploy your custom agent created with ADK to Agent Engine and AgentSpace. 
Last update data: `25 Aug 2025` - please keep in mind this is can change with any new update, consult requirements.txt for proper versions and check the documentation for updates. 

## Create ADK agent 

The best way to create a custom ADK agent is to consult these resources:
- [official documentation]("here")
- [github samples for adk]("here")

Sctructure of the current agent is the following: 
1) Authenticate the Google Services: gets credentials to work with APIs
2) Classify the Topic: checks if the user is asking for something forbidden
3) Reaserch Agent: a subagent wtih Google Search conducts a study
4) Check Report for Verification: if the report contains mention of the competitor or exceeds lenght of 500 chars the report would need to be verified by "verifier" before given to the user. 
5) Submit Report for Verification: the report is submitted to the "verifier" as a link to the backend with UI that contains the report that can be edited, approved and dissaproved. 
6) Save Report Formats: if the report get approved the user will recieve it in the chat as well as links to the GDoc and Gdrive.  

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
- currently there is a bug on Agentspace side - you require to use `AUTH_ID` to connect to any services but ADK will not be able to use it so you still have to keep a classical Oauth2.
- make your tools and code as modular as possible
- while working with the agent use `adk web` and consult Event part, usually it indicates what's going on and if there is anythign wrong. 

## Things to do for improvement: 
1) add the possibility to save files only if user requested
2) try LongruningFunc, to avoid user to ask if the report was verified
3) add a state persistance to the Database
4) Add Short and LontTerm memory with the memory bank or Database ?
