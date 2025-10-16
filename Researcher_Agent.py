from typing import TypedDict
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool,Tool
from langchain_groq import ChatGroq
from langchain_community.utilities import SerpAPIWrapper,WikipediaAPIWrapper
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools import WikipediaQueryRun

from IPython.display import display, Image
import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

SERP_API_KEY = os.getenv("SERP_API_KEY")
if not SERP_API_KEY:
    raise ValueError("SERP_API_KEY is not set in the environment.")

DPLA_API_KEY = os.getenv("DPLA_API_KEY")
if not DPLA_API_KEY:
    raise ValueError("DPLA_API_KEY is not set in the environment.")

llm = "meta-llama/llama-4-scout-17b-16e-instruct"
chat_groq_llm = ChatGroq(model_name=llm, groq_api_key=GROQ_API_KEY)

research_planning_message = """
You are a Research Planning Agent. Your goal is to create a structured plan to get the necessary information for a given research topic provided by the user.

Responsibilities:
- Understand the user's research topic.
- Break down the research topic into key questions or areas to investigate.
- Structure the research process into a clear, step-by-step plan.
- Highlight important aspects or keywords from the prompt that should be prioritized in the research.

Behavior:
- Analyze the input prompt carefully to grasp the core research need.
- If the query mentions "primary source documents" or "letters", ensure the plan includes a step instructing the use of the `dpla_search` tool.
- Present the plan in a clear, organized, and easy-to-follow format.
- Be concise and focused on the planning aspect, not the research execution itself.

Outputs:
- A structured research plan, potentially including:
    - A breakdown of the topic into sub-questions.
    - Suggested keywords for searching
    - Key points from the original prompt to keep in mind.
"""

researcher_agent_message = """
You are a highly skilled Archival Researcher Agent. Your mission is to write a COMPREHENSIVE and DETAILED report based on the provided research plan.

You MUST follow this workflow exactly:
1.  Analyze the research plan you are given. It contains multiple research questions.
2.  Address EACH research question ONE BY ONE, in sequence.
3.  For EACH individual question, you MUST use your search tools to gather detailed information. Find specific facts, dates, names, and context.
4.  After researching a question, write a thorough, multi-paragraph answer for that specific question.
5.  Once you have answered ALL of the questions in the plan, compile all your answers into a single, final report.
6.  The final report MUST be well-structured, using a clear heading for each research question from the original plan.
7.  DO NOT stop after answering only one question.
"""

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

# prompt template for input handling
planning_prompt = ChatPromptTemplate.from_messages([
    ("system", research_planning_message),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

planning_tools = [extract_info, generate_plan]

planning_agent_runnable = create_tool_calling_agent(
    llm=chat_groq_llm,
    tools=planning_tools,
    prompt=planning_prompt
)

planning_agent_executor = AgentExecutor(agent=planning_agent_runnable, tools=planning_tools, verbose=True,return_intermediate_steps=True)

search = SerpAPIWrapper(serpapi_api_key=SERP_API_KEY)
google_search_tool = Tool(
    name="google_search",
    description="Use this for general web searches, finding articles, and recent information.",
    func=search.run,
)

wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

@tool
def dpla_search(query: str) -> str:
    """
    Searches the Digital Public Library of America (DPLA) for primary source historical documents, images, and records.
    Use this to find original materials related to US history.
    """
    api_key = DPLA_API_KEY
    base_url = "https://api.dp.la/v2/items"
    params = {'q': query, 'api_key': api_key, 'page_size': 5}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get('docs'):
            return "No primary sources found in the DPLA for that query."

        results = []
        for item in data['docs']:
            title = item.get('sourceResource', {}).get('title', 'No Title')
            provider = item.get('provider', {}).get('name', 'Unknown Provider')
            link = item.get('isShownAt', 'No Link')
            results.append(f"Title: {title}\nProvider: {provider}\nLink: {link}\n---")

        return "\n".join(results)

    except requests.exceptions.RequestException as e:
        return f"Error accessing DPLA API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", researcher_agent_message),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

researcher_tools = [google_search_tool, wikipedia_tool, dpla_search]

researcher_agent_runnable = create_tool_calling_agent(
    llm=chat_groq_llm,
    tools=researcher_tools,
    prompt=researcher_prompt
)

researcher_executor = AgentExecutor(agent=researcher_agent_runnable, tools=researcher_tools, verbose=True)

class AgentState(TypedDict):
    query: str
    research_plan: str
    research_findings: str

def planning_node(state: AgentState):
    """Invokes the planning agent to create a research plan."""
    print("--- 💬 EXECUTING PLANNING NODE ---")
    response = planning_agent_executor.invoke({"input": state["query"]})

    clean_plan = response['intermediate_steps'][-1][1]

    return {"research_plan": clean_plan}

def research_node(state: AgentState):
    """Invokes the researcher agent to execute the research plan."""
    print("--- EXECUTING RESEARCH NODE ---")
    response = researcher_executor.invoke({"input": state["research_plan"]})
    return {"research_findings": response["output"]}

# Build and Run the Graph

workflow = StateGraph(AgentState)

workflow.add_node("planner", planning_node)
workflow.add_node("researcher", research_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", END)

app = workflow.compile()

print("--- Agent Workflow Graph ---")
display(Image(app.get_graph().draw_mermaid_png()))
user_query = "Research the causes and consequences of the French Revolution."
test_query = "Find primary source documents or letters related to the signing of the US Declaration of Independence."

final_state = app.invoke({"query": test_query})

print("\n\n--- FINAL GRAPH OUTPUT ---")
print(final_state['research_findings'])
