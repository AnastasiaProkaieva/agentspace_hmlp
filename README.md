# About
This project presence a detailed walkthrough how to deploy custom ADK agent to AgentEngine and Agentspace with the Human in the Loop feedback (via email validation on the external backend). Once the validation is accepted by another user, the agent will proceed by generating and presenting the final report to the user. The report will be also saved to the user Gdrive and GDoc in 3 formats: docx, pdf, md.


## Configuration 
Check README.md under 2 folders. 

## Create custom Agent using ADK

### Test your agent 
There are few ways you can test your agent, the most efficient is to use `adk web`. It supports local and deployed remote agents. 
- To use adk web, simply run this command in your terminal `adk web`
- To attached a deployed agent to the ADK session use this command `adk web --session_db_url=agentengine://${agent_engine_id}`

## Deploy to Agent Engine 
Use script to deploy to AgentEngine, recommended to run `local_test.py` prior to this to ensure your package will be properly serialized and all dependencies were included. Consult the documentation for any update. 

## Deploy to AgentSpace 
Use scripts under folder scripts to deploy your custom agent from AgentEngine to Agentspace using bash scripts. You can also run CURL commands, but this is less reproducible and error prone.


