from google.adk.agents import LlmAgent
from google.adk.tools import google_search

# Define the research sub-agent
research_agent = LlmAgent(
    name="research_agent",
    model="gemini-2.5-flash",
    description="Use this tool to delegate research on a specific topic. Provide a clear, detailed query for the assistant to search for.",
    instruction="""
        You are a research assistant. Your only purpose is to use the provided Google Search tool
        to find information in response to a user's query.
        Synthesize the search results into a concise summary and provide it as your final answer.
    """,
    tools=[google_search],
)
