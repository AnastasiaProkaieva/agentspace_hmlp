import requests
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import BaseTool, ToolContext

from google.genai import types
from typing import Optional, Dict, Any

from .config import settings


def check_review_status(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    state = callback_context.state
    report_review_id = state.get(settings.REPORT_REVIEW_ID_KEY)
    if not report_review_id:
        return None
    try:
        response = requests.get(
            f"{settings.REVIEW_APP_BASE_URL}/reviews/{report_review_id}/status"
        )
        response.raise_for_status()
        review_data = response.json()
        status = review_data.get("status")
    except requests.RequestException as e:
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(text=f"Sorry, I couldn't reach the review service: {e}")
                ]
            )
        )
    if status == "pending":
        return LlmResponse(
            content=types.Content(
                parts=[
                    types.Part(
                        text="The report is still awaiting review. I will check again later."
                    )
                ]
            )
        )
    state[settings.REPORT_REVIEW_ID_KEY] = None
    comment = review_data.get("comment")
    final_report_text = review_data.get("outline")
    if status == "approved":
        system_message = f"SYSTEM: The user has APPROVED the report. Their comment was: '{comment if comment else 'No comment.'}' You must now finalize the report. Call the `save_report_formats` tool with this final approved text and a suitable title. The final text is:\n\n---\n{final_report_text}\n---"
        llm_request.contents.append(
            types.Content(parts=[types.Part(text=system_message)], role="user")
        )
    elif status == "disapproved":
        system_message = f"SYSTEM: The user has DISAPPROVED the report. You MUST revise the report based on their feedback: '{comment}'. Use the `research_assistant_tool` to find new information and then write a new version of the report."
        llm_request.contents.append(
            types.Content(parts=[types.Part(text=system_message)], role="user")
        )
    return None


def save_review_id(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[LlmResponse]:
    """
    This callback has two purposes:
    1. If 'submit_report_for_verification' ran, it saves the review_id.
    2. It ALSO forces a safe, canned response to the user to prevent the report from leaking.
    For all other tools, it does nothing.
    """
    if tool.name == "submit_report_for_verification":
        if "review_id" in tool_response:
            tool_context.state[settings.REPORT_REVIEW_ID_KEY] = tool_response[
                "review_id"
            ]

        canned_message = "The generated report requires human verification and has been sent for review."
        return LlmResponse(
            content=types.Content(parts=[types.Part(text=canned_message)])
        )

    # For any other tool, do nothing and return None immediately.
    return None
