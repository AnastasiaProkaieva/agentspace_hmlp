#!/bin/bash

# ==============================================================================
# Google Discovery Engine Agent Management Script
#
# This script provides a menu to list or delete agents using the API.
# It requires a .env file in the same directory with PROJECT_ID and APP_ID.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated (`gcloud auth login`)
#   - jq installed for pretty-printing JSON (`sudo apt-get install jq` or `brew install jq`)
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

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

# --- Validate Required Variables ---
if [ -z "$GOOGLE_CLOUD_PROJECT_NUMBER" ] || [ -z "$AS_APP_ID" ] || [-z "$GOOGLE_CLOUD_LOCATION_AS"]; then
    echo "❌ Error: PROJECT_ID or APP_ID or GOOGLE_CLOUD_LOCATION_AS is not set in your .env file."
    exit 1
fi

# --- API Base URL ---
BASE_URL="https://eu-discoveryengine.googleapis.com/v1alpha"
LIST_URL="${BASE_URL}/projects/${GOOGLE_CLOUD_PROJECT_NUMBER}/locations/${GOOGLE_CLOUD_LOCATION_AS}/collections/default_collection/engines/${AS_APP_ID}"

# --- Function to List Agents ---
list_agents() {
    echo "🔄 Fetching list of agents for App ID: $AS_APP_ID..."
    
    local LIST_URL="${LIST_URL}/assistants/${ASSISTANT_ID}/agents/"

    # The -s flag makes curl silent (no progress meter)
    curl -s -X GET \
         -H "Authorization: Bearer $(gcloud auth print-access-token)" \
         -H "Content-Type: application/json" \
         -H "X-Goog-User-Project: ${GOOGLE_CLOUD_PROJECT}" \
         "${LIST_URL}" | jq .
    
    echo "✅ Done."
}

BASE_URL="https://eu-discoveryengine.googleapis.com/v1alpha"
# --- Function to Delete an Agent ---
delete_agent() {
    echo "⚠️ This is a destructive action."
    read -p "Please enter the full AGENT_RESOURCE_NAME to delete: " AGENT_RESOURCE_NAME

    if [ -z "$AGENT_RESOURCE_NAME" ]; then
        echo "❌ Error: Agent Resource Name cannot be empty."
        return
    fi
    
    # Confirmation prompt
    read -p "Are you absolutely sure you want to delete '${AGENT_RESOURCE_NAME}'? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "🚫 Deletion cancelled."
        return
    fi

    echo "🔥 Deleting agent..."


    curl -s -X DELETE \
         -H "Authorization: Bearer $(gcloud auth print-access-token)" \
         -H "Content-Type: application/json" \
         -H "X-Goog-User-Project: ${GOOGLE_CLOUD_PROJECT}" \
         "${BASE_URL}/${AGENT_RESOURCE_NAME}"
    
    # A successful DELETE often returns an empty response, so we just confirm the action
    echo "✅ Deletion command sent for '${AGENT_RESOURCE_NAME}'."
}

# --- Main Menu ---
while true; do
    echo ""
    echo "--- Agent Management Menu ---"
    echo "Project: $GOOGLE_CLOUD_PROJECT | App: $AS_APP_ID"
    echo "-----------------------------"
    echo "1. List all agents"
    echo "2. Delete a specific agent"
    echo "3. Exit"
    echo "-----------------------------"
    read -p "Enter your choice [1-3]: " choice

    case $choice in
        1)
            list_agents
            ;;
        2)
            delete_agent
            ;;
        3)
            echo "👋 Exiting."
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please try again."
            ;;
    esac
done
