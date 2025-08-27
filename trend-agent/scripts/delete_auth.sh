#!/bin/bash

#source ../.env

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
required_vars=("GOOGLE_CLOUD_PROJECT" "AUTH_ID" "OAUTH_CLIENT_ID" "OAUTH_CLIENT_SECRET" "SCOPES")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set in .env"
        exit 1
    fi
done

echo "🚀 Creating AgentSpace Authorization..."
echo "   Project: $GOOGLE_CLOUD_PROJECT"
echo "   Auth ID: $AUTH_ID"
echo "   Scopes: $SCOPES"

# --- Configuration ---
# TODO: Replace with your project ID and location
LOCATION="eu" # Or your specific location

# --- Main Script ---

# 1. Get the access token
TOKEN=$(gcloud auth print-access-token)

# 2. List all authorizations and extract their names
AUTHORIZATIONS=$(curl -X GET \
  "https://eu-discoveryengine.googleapis.com/v1alpha/projects/${GOOGLE_CLOUD_PROJECT}/locations/${LOCATION}/authorizations" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" | jq -r '.authorizations[].name')

# 3. Check if any authorizations were found
if [ -z "$AUTHORIZATIONS" ]; then
  echo "No authorizations found."
  exit 0
fi

# 4. Loop through and delete each authorization
for AUTH in $AUTHORIZATIONS; do
  echo "Deleting authorization: ${AUTH}"
  curl -X DELETE \
    "https://eu-discoveryengine.googleapis.com/v1alpha/${AUTH}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json"
  echo ""
done

echo "All authorizations have been deleted."
