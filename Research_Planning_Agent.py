from typing import Dict, TypedDict, Optional, List, Any, Annotated
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq

from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
from dotenv import load_dotenv
from groq import Groq
import os

# load secrets
load_dotenv() 

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

# Set up the Groq client
client = Groq(api_key = GROQ_API_KEY)

llm = "llama-3.1-8b-instant"
chat_groq_llm = ChatGroq(model_name=llm, groq_api_key=GROQ_API_KEY)

# AGENT MESSAGE
research_planning_message = """
You are a Research Planning Agent. Your goal is to create a structured plan to get the necessary information for a given research topic provided by the user.

Responsibilities:
- Understand the user's research topic.
- Break down the research topic into key questions or areas to investigate.
- Structure the research process into a clear, step-by-step plan.
- Highlight important aspects or keywords from the prompt that should be prioritized in the research.

Behavior:
- Analyze the input prompt carefully to grasp the core research need.
- Present the plan in a clear, organized, and easy-to-follow format.
- Be concise and focused on the planning aspect, not the research execution itself.

Outputs:
- A structured research plan, potentially including:
    - A breakdown of the topic into sub-questions.
    - Suggested keywords for searching
    - Key points from the original prompt to keep in mind.
"""

# PLANNING AGENT TOOLS 
@tool
def extract_info(query: str):
    """
    Understands the user's input/query and breaks it down into the historical topic and time period, returning.

    Parameters:
        str: The user's historical query.

    Returns:
        str: A formatted string containing the extracted information.
    """
    # Use the LLM to extract the historical topic and time period from the query
    # Instruct the LLM to format the output as a simple string
    prompt = f"""
    From the following historical research query, extract the main historical topic, the specific time period, location, and group of people involved.
    If a value is not present in the query, use the general value linked to the topic.

    Query: {query}

    Format the output as a single string like this:
    Topic: [Extracted Topic] | Time Period: [Extracted Time Period] | Location: [Extracted Location] | Group of People involved: [Extracted Group of People]
    """
    response = chat_groq_llm.invoke(prompt)
    return response.content


@tool
def generate_plan(info_string: str):
    """
    Takes a formatted string from extract_info to plan the research.

    Args:
        str: Expected format: "Topic: [...] | Time Period: [...] | Location: [...] | Group of People involved: [...]"

    Returns:
        str: A structured research plan based on the extracted information.
    """
    # Parse the information from the formatted string
    info = {}
    for part in info_string.split(" | "):
        if ":" in part:
            key, value = part.split(":", 1)
            info[key.strip()] = value.strip()

    # Get the extracted information, defaulting to "N/A" if parsing fails or key is missing
    topic = info.get("Topic", "N/A")
    time_period = info.get("Time Period", "N/A")
    location = info.get("Location", "N/A")
    group_involved = info.get("Group of People involved", "N/A")

    # Use the LLM to generate a research plan based on the extracted information
    prompt = f"""
    Based on the following historical information:

    Topic: {topic}
    Time Period: {time_period}
    Location: {location}
    Group of People involved: {group_involved}

    Create a plan that includes:
    - Five specific research questions to answer based on the topic, time period, location, and group involved.
    - Ten suggested keywords for searching the historical topic
    -  and search strategies.

    Format the output like this:
    Research Questions:
      questuion1
      question2
      question3
      question4
      question5

    Suggested Keywords:
      keyword1
      keyword2
      keyword3
      keyword4
      keyword5
      keyword6
      keyword7
      keyword8
      keyword9
      keyword10
    """

    response = chat_groq_llm.invoke(prompt)
    return response.content

# Agent Class 
class Research_Planning_Agent():
    def __init__(self): 
        self.model = chat_groq_llm
        self.tools = [extract_info, generate_plan]
        self.prompt = research_planning_message
        self.inner_message : str = None
        self.research_planning_agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self.prompt,
            name="research_planning_agent"
        )

    def visualize_graph(self):
        return display(Image(self.research_planning_agent.get_graph().draw_mermaid_png()))
    

    def show_inner_workings(self): 
        return getattr(self, 'inner_message', [])


    def run(self, query: str): 
        response = self.research_planning_agent.invoke({"messages": [{"role": "user", "content": query}]})
        self.inner_message = response['messages']
        # for message in response['messages']:
        #     message.pretty_print()
        return response['messages'][-2].content
