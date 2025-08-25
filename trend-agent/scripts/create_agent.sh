#!/bin/bash

# =============================================================================
# CREATE AGENTSPACE AGENT
# =============================================================================
# This script creates the Agent in AgentSpace
# Run this AFTER creating authorization and deploying the reasoning engine

set -e  # Exit on any error

# This finds the directory where the script is located, so it can reliably find the .env file.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ENV_FILE="$SCRIPT_DIR/.env" # Assuming .env is one directory above the script

# Load environment variables
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    echo "✅ Loaded .env file from $ENV_FILE"
else
    # ## CHANGE ##: Improved error message with the full path.
    echo "❌ Error: .env file not found at the expected location: $ENV_FILE"
    echo "   Please ensure it exists one directory above your 'scripts' folder."
    exit 1
fi


# Validate required variables
required_vars=("GOOGLE_CLOUD_PROJECT" "GOOGLE_CLOUD_PROJECT_NUMBER" "GOOGLE_CLOUD_LOCATION" "AS_APP_ID" "ASSISTANT_ID" "AGENT_NAME" "AGENT_DISPLAY_NAME" "AGENT_DESCRIPTION" "AGENT_TOOL_DESCRIPTION" "AUTH_ID")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set in .env"
        exit 1
    fi
done

# Check if REASONING_ENGINE is set
if [ -z "$REASONING_ENGINE" ]; then
    echo "❌ Error: REASONING_ENGINE is not set in .env"
    echo "   Deploy your agent first using: python agents/meeting_prep_agent.py"
    echo "   Then update REASONING_ENGINE in .env with the resource name"
    exit 1
fi

echo "🚀 Creating AgentSpace Agent..."
echo "   Project: $GOOGLE_CLOUD_PROJECT"
echo "   Agent Name: $AGENT_NAME"
echo "   Display Name: $AGENT_DISPLAY_NAME"
echo "   Reasoning Engine: $REASONING_ENGINE"

# --- Script Body ---
AUTH_TOKEN=$(gcloud auth print-access-token)
DISCOVERY_ENGINE_API_BASE_URL="https://eu-discoveryengine.googleapis.com"
URL_USE="${DISCOVERY_ENGINE_API_BASE_URL}/v1alpha/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/${GOOGLE_CLOUD_LOCATION_AS}/collections/default_collection/engines/${AS_APP_ID}"


echo "📡 Making API request..."
response=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: Bearer ${AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${GOOGLE_CLOUD_PROJECT}" \
  "${URL_USE}/assistants/${ASSISTANT_ID}/agents" \
  -d '{
    "name": "projects/'"${GOOGLE_CLOUD_PROJECT_NUMBER}"'/locations/'"${GOOGLE_CLOUD_LOCATION_AS}}"'/collections/default_collection/engines/'"${AS_APP_ID}"'/assistants/'"${ASSISTANT_ID}"'/agents/'"${AGENT_NAME}"'",
    "displayName": "'"${AGENT_DISPLAY_NAME}"'",
    "description": "'"${AGENT_DESCRIPTION}"'",
    "adk_agent_definition": {
      "tool_settings": {
        "tool_description": "'"${AGENT_TOOL_DESCRIPTION}"'"
      },
      "provisioned_reasoning_engine": {
        "reasoning_engine": "'"${REASONING_ENGINE}"'"
      },
      "authorizations": [
        "projects/'"${GOOGLE_CLOUD_PROJECT_NUMBER}"'/locations/eu/authorizations/'"${AUTH_ID}"'"
      ]
    }
  }')

# Extract response body and status code
http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | sed '$d')

echo "📋 Response:"
echo "$response_body" | jq . 2>/dev/null || echo "$response_body"

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
    echo "✅ Agent created successfully!"
    echo "   Agent Name: $AGENT_NAME"
    echo "   Display Name: $AGENT_DISPLAY_NAME"
    echo "   Next step: Test the agent in AgentSpace web interface"
else
    echo "❌ Failed to create agent (HTTP $http_code)"
    echo "   Check your configuration and try again"
    exit 1
fi
