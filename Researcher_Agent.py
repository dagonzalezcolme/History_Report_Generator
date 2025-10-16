from typing import TypedDict, Optional, List
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool, Tool
from langchain_groq import ChatGroq
from langchain_community.utilities import SerpAPIWrapper, WikipediaAPIWrapper
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent

from langchain_community.tools import WikipediaQueryRun
from groq import Groq

from IPython.display import display, Image
from dotenv import load_dotenv
import os
import requests

load_dotenv() 

# Load Secrets (raise early if missing)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
DPLA_API_KEY = os.getenv("DPLA_API_KEY")

# Check if the API key was retrieved successfully
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please add it.")

if not SERP_API_KEY:
    raise ValueError("SERP_API_KEY not found. Please add it.")

if not DPLA_API_KEY:
    raise ValueError("DPLA_API_KEY not found. Please add it.")

# Set up the Groq client
client = Groq(api_key = GROQ_API_KEY)

llm = "meta-llama/llama-4-scout-17b-16e-instruct"
chat_groq_llm = ChatGroq(model_name=llm, groq_api_key=GROQ_API_KEY)

# AGENT STATE
class AgentState(TypedDict):
    query: str
    research_plan: Optional[str]
    research_findings: Optional[str]

class DPLASearchSchema(TypedDict):
    query: str
    
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

def dpla_search(query: str) -> str:
    """Searches the Digital Public Library of America (DPLA) for primary sources.

    This helper is a plain function (not registered as a langchain tool decorator here)
    so it can be composed into a Tool by the class below.
    """
    api_key = DPLA_API_KEY
    base_url = "https://api.dp.la/v2/items"
    params = {"q": query, "api_key": api_key, "page_size": 5}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("docs"):
            return "No primary sources found in the DPLA for that query."

        results = []
        for item in data["docs"]:
            title = item.get("sourceResource", {}).get("title", "No Title")
            provider = item.get("provider", {}).get("name", "Unknown Provider")
            link = item.get("isShownAt", "No Link")
            results.append(f"Title: {title}\nProvider: {provider}\nLink: {link}\n---")

        return "\n".join(results)

    except requests.exceptions.RequestException as e:
        return f"Error accessing DPLA API: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


class Researcher_Agent:
    """
    Responsibilities:
    - initialize LLM and tools
    - build the planning and researcher agents
    - provide a run_plan() method that executes the graph and returns findings
    """

    def __init__(self):
        self.model = chat_groq_llm
        self.prompt = ChatPromptTemplate.from_template("{input}\n" + researcher_agent_message)     
        
        self.search = SerpAPIWrapper(serpapi_api_key=SERP_API_KEY)
        self.google_search_tool = Tool(
            name="google_search",
            description="General web searches.",
            func=self.search.run
        )
        self.dpla_tool = Tool(
            name="dpla_search",
            description="Searches the Digital Public Library of America for primary sources.",
            func=dpla_search,
            args_schema=TypedDict("DPLASearchSchema", {"query": str})
        )
        self.wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        self.tools = [self.dpla_tool, self.google_search_tool,self.wikipedia_tool]

        self.researcher_agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self.prompt,
        )

        self.researcher_executor = AgentExecutor(agent=self.researcher_agent, 
                                                 tools=self.tools, 
                                                 verbose=True)

        # Optionally build the planning agent if the project provides planning pieces
        # (left out here to keep single-responsibility)

    def visualize_graph(self):
        return display(Image(self.researcher_agent.get_graph().draw_mermaid_png()))
    
    
    def run_research(self, plan: str) -> str:
        """Run the researcher agent on a provided research plan string and return findings."""
        if not plan:
            raise ValueError("There is no researching plan")

        print("--- EXECUTING RESEARCH NODE ---")
        response = self.researcher_executor.invoke({"input": plan})

        # AgentExecutor returns a complex structure; keep compatibility with previous code
        output = response.get("output") if isinstance(response, dict) else str(response)
        return output


# def build_and_display_graph():
#     """Utility to build the simple two-node graph shown originally.

#     Returns the compiled app (StateGraph compiled object). This mirrors the original
#     behavior but is intentionally not executed at import time.
#     """
#     # A minimal planning node that forwards the query to produce a 'research_plan' key.
#     # The original planning agent pieces (planning_prompt, planning tools) were not
#     # defined in this file; the function below is a placeholder demonstrating structure.

#     @tool
#     def research_node(state: AgentState):
#         agent = ResearcherAgent()
#         return {"research_findings": agent.run_plan(state.get("research_plan"))}



# if __name__ == "__main__":
#     # Example usage when executed as a script (keeps import-time side effects away)
#     app = build_and_display_graph()
#     display(Image(app.get_graph().draw_mermaid_png()))



#     test_query = "Find primary source documents or letters related to the signing of the US Declaration of Independence."
#     final_state = app.invoke({"query": test_query})
#     print("\n\n--- FINAL GRAPH OUTPUT ---")
#     print(final_state.get("research_findings"))


