import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import base64

from Research_Planning_Agent import Research_Planning_Agent
from Researcher_Agent import Researcher_Agent
from Checker_Agent import CheckerAgent
from report_agent import report_workflow

# Page config
st.set_page_config(page_title="Historical Research Generator", page_icon="📚", layout="wide")

# Simple CSS
st.markdown("""
<style>
    .main-title {font-size: 2.5rem; color: #667eea; text-align: center; font-weight: bold;}
    .subtitle {text-align: center; color: #666; margin-bottom: 2rem;}
    .status-box {padding: 1.2rem; border-radius: 12px; margin: 0.8rem 0; border-left: 5px solid; transition: all 0.3s;}
    .active {background: #e3f2fd; border-color: #2196f3; box-shadow: 0 4px 12px rgba(33,150,243,0.3);}
    .complete {background: #e8f5e9; border-color: #4caf50; box-shadow: 0 2px 8px rgba(76,175,80,0.2);}
    .waiting {background: #fafafa; border-color: #e0e0e0; opacity: 0.7;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {
        'Supervisor': 'waiting',
        'Planner': 'waiting',
        'Researcher': 'waiting',
        'Checker': 'waiting',
        'Reporter': 'waiting'
    }
if 'query_text' not in st.session_state:
    st.session_state.query_text = ""

def check_api_keys():
    load_dotenv()
    keys = ["GROQ_API_KEY", "SERP_API_KEY", "DPLA_API_KEY"]
    missing = [k for k in keys if not os.getenv(k)]
    return len(missing) == 0, missing

def set_example_query(example):
    """Set example query to the text area"""
    st.session_state.query_text = example

def render_agent_status(name, icon, desc, status, status_placeholder):
    """Render agent status card"""
    css_class = "waiting"
    status_text = "⏳ Waiting"
    
    if status == "complete":
        css_class = "complete"
        status_text = "✅ Complete"
    elif status == "active":
        css_class = "active"
        status_text = "⚡ Active - Running Now!"
    
    status_placeholder.markdown(f'''
    <div class="status-box {css_class}">
        <div style="font-size: 1.1rem;"><strong>{icon} {name}</strong></div>
        <div style="color: #666; margin: 0.3rem 0;">{desc}</div>
        <div style="font-weight: 600; color: {"#2196f3" if css_class == "active" else "#4caf50" if css_class == "complete" else "#999"};">{status_text}</div>
    </div>
    ''', unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">📚 Historical Research Report Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Multi-Agent AI System for Historical Research</p>', unsafe_allow_html=True)

# Check API keys
keys_ok, missing = check_api_keys()
if not keys_ok:
    st.error(f"⚠️ Missing API Keys: {', '.join(missing)}")
    st.stop()

# Main layout
col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("🔍 Enter Research Query")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        examples = [
            "Apollo 11 mission with primary sources and recent analysis",
            "Civil War Battle of Gettysburg with soldiers' letters",
            "Women's Suffrage Movement with speeches and documents",
            "Industrial Revolution workers' conditions with primary sources"
        ]
        for idx, ex in enumerate(examples):
            if st.button(ex, key=f"ex_{idx}", use_container_width=True):
                set_example_query(ex)
                st.rerun()
    
    # Query input with form for Enter key support
    with st.form(key="query_form", clear_on_submit=False):
        query = st.text_area(
            "Your Query:",
            height=120,
            placeholder="Example: Create a report on Apollo 11 with primary sources...",
            key="query_input",
            value=st.session_state.query_text
        )
        
        # Submit button 
        submit_button = st.form_submit_button("🚀 Generate Report", type="primary", use_container_width=True)
        
        # Update session state
        if query:
            st.session_state.query_text = query
    
    # Buttons
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        if st.session_state.pdf_path and st.button("🔄 New Query", use_container_width=True):
            st.session_state.pdf_path = None
            st.session_state.query_text = ""
            st.session_state.agent_status = {
                'Supervisor': 'waiting',
                'Planner': 'waiting',
                'Researcher': 'waiting',
                'Checker': 'waiting',
                'Reporter': 'waiting'
            }
            st.rerun()
    
    with col_b:
        if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, "rb") as f:
                st.download_button("📥 Download PDF", f, f"Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
                                 mime="application/pdf", use_container_width=True)
    
    # Results with PDF viewer
    if st.session_state.pdf_path:
        st.success(f"✅ Report Generated: `{st.session_state.pdf_path}`")
        st.info(f"📊 Size: {os.path.getsize(st.session_state.pdf_path) / 1024:.2f} KB")
        
        # PDF Viewer
        with st.expander("📄 View PDF Report", expanded=True):
            with open(st.session_state.pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

with col2:
    st.subheader("📊 Agent Status")
    
    # Create placeholders for each agent 
    supervisor_placeholder = st.empty()
    planner_placeholder = st.empty()
    researcher_placeholder = st.empty()
    checker_placeholder = st.empty()
    reporter_placeholder = st.empty()
    progress_placeholder = st.empty()
    
    # Initial render - show current status
    render_agent_status("Supervisor", "🎯", "Orchestrating workflow", st.session_state.agent_status['Supervisor'], supervisor_placeholder)
    render_agent_status("Planner", "📋", "Creating research plan", st.session_state.agent_status['Planner'], planner_placeholder)
    render_agent_status("Researcher", "🔍", "Gathering information", st.session_state.agent_status['Researcher'], researcher_placeholder)
    render_agent_status("Checker", "✅", "Verifying accuracy", st.session_state.agent_status['Checker'], checker_placeholder)
    render_agent_status("Reporter", "📄", "Generating PDF", st.session_state.agent_status['Reporter'], reporter_placeholder)

# Process workflow when form is submitted
if submit_button and query:
    try:
        # Initialize agents
        planning_agent = Research_Planning_Agent()
        researcher_agent = Researcher_Agent()
        checker_agent = CheckerAgent()
        report_gen = report_workflow()
        
        # Supervisor starts
        st.session_state.agent_status['Supervisor'] = 'active'
        render_agent_status("Supervisor", "🎯", "Orchestrating workflow", "active", supervisor_placeholder)
        progress_placeholder.info("🔄 Supervisor initiating workflow...")
        
        # Planner Agent
        st.session_state.agent_status['Planner'] = 'active'
        render_agent_status("Planner", "📋", "Creating research plan", "active", planner_placeholder)
        progress_placeholder.progress(5)
        progress_placeholder.info("🔄 Planning research strategy...")
        
        plan = planning_agent.run(query)
        
        st.session_state.agent_status['Planner'] = 'complete'
        render_agent_status("Planner", "📋", "Creating research plan", "complete", planner_placeholder)
        progress_placeholder.progress(25)
        
        # Researcher Agent
        st.session_state.agent_status['Researcher'] = 'active'
        render_agent_status("Researcher", "🔍", "Gathering information", "active", researcher_placeholder)
        progress_placeholder.info("🔄 Gathering historical information...")
        
        findings = researcher_agent.run_research(plan)
        
        st.session_state.agent_status['Researcher'] = 'complete'
        render_agent_status("Researcher", "🔍", "Gathering information", "complete", researcher_placeholder)
        progress_placeholder.progress(50)
        
        # Checker Agent
        st.session_state.agent_status['Checker'] = 'active'
        render_agent_status("Checker", "✅", "Verifying accuracy", "active", checker_placeholder)
        progress_placeholder.info("🔄 Verifying facts and accuracy...")
        
        checked = checker_agent.evaluate(query, findings)
        
        st.session_state.agent_status['Checker'] = 'complete'
        render_agent_status("Checker", "✅", "Verifying accuracy", "complete", checker_placeholder)
        progress_placeholder.progress(75)
        
        # Reporter Agent
        st.session_state.agent_status['Reporter'] = 'active'
        render_agent_status("Reporter", "📄", "Generating PDF", "active", reporter_placeholder)
        progress_placeholder.info("🔄 Creating PDF report...")
        
        result = report_gen.invoke({"rewritten_output": checked.rewritten_output})
        
        st.session_state.agent_status['Reporter'] = 'complete'
        render_agent_status("Reporter", "📄", "Generating PDF", "complete", reporter_placeholder)
        progress_placeholder.progress(95)
        
        # Supervisor completes
        st.session_state.agent_status['Supervisor'] = 'complete'
        render_agent_status("Supervisor", "🎯", "Orchestrating workflow", "complete", supervisor_placeholder)
        progress_placeholder.progress(100)
        
        # Complete
        st.session_state.pdf_path = result.get("pdf_path")
        progress_placeholder.success("🎉 All agents completed successfully!")
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())