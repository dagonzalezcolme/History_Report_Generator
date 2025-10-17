import os
from dotenv import load_dotenv

# Import agent classes
from Research_Planning_Agent import Research_Planning_Agent
from Researcher_Agent import Researcher_Agent
from Checker_Agent import CheckerAgent
from report_agent import report_workflow

def main():
    """
    Main function to orchestrate the multi-agent history report generation workflow.
    This version uses a simple, robust, linear chain.
    """
    load_dotenv()
    print("🔑 Environment variables loaded.")

    if not all([os.getenv("GROQ_API_KEY"), os.getenv("SERP_API_KEY"), os.getenv("DPLA_API_KEY")]):
        print("\n ERROR: Missing API keys in .env file.")
        return

    user_query = "What was the significance of the Silk Road in connecting ancient civilizations?"
    print(f"\n Starting research process for query: '{user_query}'")

    print("\n Instantiating agents...")
    planning_agent = Research_Planning_Agent()
    researcher_agent = Researcher_Agent()
    checker_agent = CheckerAgent()
    report_generator_graph = report_workflow()
    print("Agents are ready.")

    try:
        # STEP 1: PLANNING
        print("\n--- [STEP 1/4] EXECUTING PLANNING AGENT ---")
        research_plan = planning_agent.run(user_query)
        print("Research Plan Generated.")

        # STEP 2: RESEARCHING
        print("\n--- [STEP 2/4] EXECUTING RESEARCHER AGENT ---")
        print("This may take a few moments...")
        research_findings = researcher_agent.run_research(research_plan)
        print("Research Findings Compiled.")

        # STEP 3: CHECKING & VERIFYING
        print("\n--- [STEP 3/4] EXECUTING CHECKER AGENT ---")
        check_result = checker_agent.evaluate(agent_input=user_query, agent_output=research_findings)
        rewritten_output = check_result.rewritten_output
        print("Findings Checked and Verified.")

        # STEP 4: REPORT GENERATION
        print("\n--- [STEP 4/4] EXECUTING REPORT GENERATOR ---")
        report_input = {"rewritten_output": rewritten_output}
        final_report_state = report_generator_graph.invoke(report_input)
        pdf_path = final_report_state.get("pdf_path")

        print("\n--- [PROCESS COMPLETE] ---")
        print(f"\n Success! Your report has been generated.")
        print(f"📄 You can find it here: {os.path.abspath(pdf_path)}")

    except Exception as e:
        print(f"\n An error occurred during the workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()