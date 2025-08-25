import json
from typing import Dict, Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools import ToolContext
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

from .config import settings

# A key to store the full credential object (with refresh token) in the session state for local dev
GOOGLE_TOKENS_KEY = "google_tool_tokens"

def authenticate_google_services(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Establishes and verifies authentication with Google services for the current session.
    This MUST be the first tool called in any workflow that requires accessing Google APIs like Drive or Gmail.
    It intelligently handles different environments: deployed on Agentspace and local development (OAuth pop-up).
    """
    # This function contains all the logic to check state, refresh, or initiate a new auth flow.
    creds = get_authenticated_credentials(tool_context, initiate_auth_flow=True)

    if creds and creds.valid:
        return {"status": "success", "message": "Authentication is active."}
    else:
        # This case is triggered when we are waiting for the user to complete the pop-up flow locally.
        return {
            "status": "pending_auth",
            "message": "I need you to log in to your Google Account to proceed. Please follow the pop-up window.",
        }


def get_authenticated_credentials(
    tool_context: ToolContext, initiate_auth_flow: bool = False
) -> Optional[Credentials]:
    """
    Gets Google credentials by checking state, prioritizing the Agentspace-injected token.
    Falls back to the local ADK OAuth flow if necessary.

    Args:
        tool_context: The context for the current tool call.
        initiate_auth_flow: If True, will trigger the OAuth pop-up for local dev if no other credentials are found.

    Returns:
        A valid Credentials object or None.
    """
    creds = None

    # --- Priority 1: Agentspace-injected token (as per official docs) ---
    # This is the primary method for agents deployed on Agentspace.
    agentspace_auth_id = settings.AUTH_ID
    if agentspace_auth_id:
        agentspace_token_key = f"temp:{agentspace_auth_id}"
        if agentspace_token_key in tool_context.state:
            print(f"✅ Using Agentspace token from state key: '{agentspace_token_key}'")
            access_token = tool_context.state[agentspace_token_key]
            return Credentials(token=access_token, scopes=settings.SCOPES)

    # --- Priority 2: Locally stored tokens (from a previous pop-up login) ---
    # This block handles local development, allowing the agent to reuse credentials within a session.
    if GOOGLE_TOKENS_KEY in tool_context.state:
        try:
            creds = Credentials.from_authorized_user_info(
                tool_context.state[GOOGLE_TOKENS_KEY], settings.SCOPES
            )
        except Exception as e:
            print(f"⚠️ Could not load local credentials from state: {e}.")
            creds = None

    # Refresh if needed (for local dev tokens)
    if creds and not creds.valid and creds.expired and creds.refresh_token:
        print("...Refreshing expired local credentials...")
        try:
            creds.refresh(Request())
            tool_context.state[GOOGLE_TOKENS_KEY] = json.loads(creds.to_json())
        except Exception as e:
            print(f"❌ Failed to refresh credentials: {e}")
            creds = None

    if creds and creds.valid:
        print("✅ Using valid, existing local credentials.")
        return creds

    # --- Priority 3 (Optional): Initiate the full OAuth pop-up flow ---
    # This is the fallback for local development when no valid credentials exist at all.
    if not initiate_auth_flow:
        return None

    print(
        "...No valid credentials. Initiating ADK OAuth pop-up flow for local development."
    )
    auth_config = _get_local_auth_config()
    auth_response = tool_context.get_auth_response(auth_config)

    if auth_response:
        print("...Processing OAuth pop-up response...")
        creds = Credentials(
            token=auth_response.oauth2.access_token,
            refresh_token=auth_response.oauth2.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            scopes=settings.SCOPES,
        )
        tool_context.state[GOOGLE_TOKENS_KEY] = json.loads(creds.to_json())
        print("✅ Local authentication successful! Tokens stored.")
        return creds
    else:
        print("...Requesting new credentials from user via pop-up...")
        tool_context.request_credential(auth_config)
        return None  # Signal that we are waiting for user auth


def _get_local_auth_config() -> AuthConfig:
    """Helper to build the AuthConfig for the local dev pop-up flow."""
    auth_scheme = OAuth2(
        flows=OAuthFlows(
            authorizationCode=OAuthFlowAuthorizationCode(
                authorizationUrl="https://accounts.google.com/o/oauth2/auth",
                tokenUrl="https://oauth2.googleapis.com/token",
                scopes={scope: "" for scope in settings.SCOPES},
            )
        )
    )
    auth_credential = AuthCredential(
        auth_type=AuthCredentialTypes.OAUTH2,
        oauth2=OAuth2Auth(
            client_id=settings.OAUTH_CLIENT_ID,
            client_secret=settings.OAUTH_CLIENT_SECRET,
        ),
    )
    return AuthConfig(auth_scheme=auth_scheme, raw_auth_credential=auth_credential)
