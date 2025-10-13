# History_Report_Generator

## Multi-Agent Historical Research System
### Overview
This project implements a multi-agent system designed to generate structured historical research reports from a user-provided query. Each agent in the system has a specific role, allowing the workflow to be modular, flexible, and scalable.

### Architecture
The system consists of the following agents:
#### Research Planning Generator
 - Extracts the main topic, time period, location, and relevant groups from the user's research query.
 - Produces a structured research plan.

#### Supervisor
 - Supervises the flow of information between agents.
 - Validates outputs, ensures quality, and decides the next agent to call.

#### Search Agent
 - Performs targeted searches based on the structured plan.
 - Collects relevant historical information, and sources.

#### Report Generator Agent
 - Takes the outputs from previous agents and compiles them into a final historical report (PDF format).
 - Ensures clarity, structure, and readability.


### Setup

#### API Keys

To use this project, you’ll need **three separate API keys** from different services.  
All of these services provide **free tiers** suitable for development.

#### Groq API Key

1. Visit [GroqCloud Console](https://console.groq.com/).  
2. **Sign up** for a new account or **log in**.  
3. Go to API Keys.  
4. Click Create API Key.  
5. Save the generated key as **GROQ_API_KEY**


#### SerpApi API Key (for Google Search)

1. Go to [SerpApi website](https://serpapi.com/).  
2. Sign up for a free account.  
3. After logging in, open your Dashboard.  
4. In the left-hand menu, click API Keys.  
5. Save the generated key as **SERP_API_KEY**.


#### DPLA API Key (for Primary Source Archives)

1. Get an API key by sending a HTTP POST request,Run the following command in your cmd
   ```bash
   # Replace EXAMPLE@gmail.com with your gmail
   curl -v --ssl-no-revoke -XPOST https://api.dp.la/v2/api_key/EXAMPLE@gmail.com 
2. The API key will be sent to your email instantly.  
3. Save the generated key as **DPLA_API_KEY**.
