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
