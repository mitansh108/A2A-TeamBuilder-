# Project: Agent-to-Agent Student Teammate Matching
<img width="1237" height="928" alt="Screenshot 2025-08-08 at 11 29 27 AM" src="https://github.com/user-attachments/assets/0b021b8e-9c6f-4a2a-9297-1fbf229ac1cf" />

## 1. Overview

The primary goal of this project is to develop a multi-agent system where a central Host Agent acts as a "Student Matchmaker," interacting with individual student agents that represent real students. Each student agent encapsulates unique attributes such as skills, interests, communication style, and personality traits. When a student queries, "Who would be my best teammate?", the Host Agent analyzes all available student profiles to recommend the most compatible match for effective collaboration.

## 2. Architecture

The system consists of a central Host Agent that acts as a proxy and communicates with several friend agents. Each agent represents a person and manages their Skills and preferences.

The high-level architecture is as follows:

-   **ADK Web (Client):** A web-based user interface for interacting with the Host Agent.
-   **Host Agent (ADK):** The central orchestrator, built using the Agent Development Kit (ADK). It analyzes all student agent profiles and recommends the most compatible teammates based on skills, interests, communication style, and personality traits.
-   **Student Agents:** Each student is represented by a personal agent responsible for encapsulating their unique attributes. These agents are built using different technologies to demonstrate interoperability within the system.


## 3. Agents

There will be four main agents in this system. To be accessible to the Host Agent, each Student agent will run as a separate server, exposing an API that the Host Agent can call.

### 3.1. Host Agent (Team Maker's Agent)

-   **Framework:** Agent Development Kit (ADK)
-   **Role:** his is the central Student Matchmaker Agent that orchestrates teammate discovery and compatibility analysis. It acts as a proxy between students and individual student agents, gathering profile information and analyzing skill complementarity to recommend optimal project partnerships.
-   **Status:** The basic structure is already in place. However, the internal instructions need to be reviewed and corrected.
-   **Port:** `10001`

### 3.2. Student Agents (Sub-Agents)

To be accessible to the Host Agent, each student agent will run as a separate server, exposing an API that the Host Agent can call.

#### 3.2.1. Karley's Agent

-   **Framework:** Agent Development Kit (ADK)
-   **Role:** Represents Karley, a quiet and thoughtful introvert student with HTML/CSS basics and JavaScript fundamentals. Shares her technical skills, interests, communication style, and learning preferences for teammate matching.
-   **Example:** Based on `@google_adk` sample.
-   **Port:** `10002`

#### 3.2.2. Nate's Agent

-   **Framework:** CrewAI
-   **Role:** Represents Nate, a friendly and enthusiastic student with Python programming and API development skills. Provides information about his technical abilities, interests, and communication style. 
-   **Example:** Based on `@crewai` sample.
-   **Port:** `10003`

#### 3.2.3. Kaitlyn's Agent

-   **Framework:** LangGraph
-   **Role:** Represents Kaitlynn, a confident leader with project management and frontend development expertise. Shares her technical skills, leadership abilities, and organized communication style for optimal teammate pairing.
-   **Example:** Based on `@langgraph` sample.
-   **Port:** `10004`

## 4. Teammate Matching Tools

The Host Agent will be equipped with a specialized set of tools for student teammate matching. These tools will enable the Host Agent to manage the entire matchmaking process, from gathering student profiles to analyzing compatibility and recommending optimal partnerships.

### 4.1. Core Functionality

-   **Profile Discovery:** he tools will allow the Host Agent to query the student agents (Karley, Nate, and Kaitlynn) for their complete profiles including technical skills, interests, communication styles, and learning preferences.
-   **Compatibility Analysis::** The tools will analyze skill complementarity, communication style balance, and experience levels to calculate compatibility scores.
-   **Teammate Recommendation:** Once compatibility analysis is complete, the tools will recommend the best teammate match with detailed reasoning and alternative suggestions for optimal project collaboration.




<img width="1707" height="936" alt="Screenshot 2025-08-08 at 11 38 41 AM" src="https://github.com/user-attachments/assets/887fff9e-f11a-4234-98f1-b3db85971f86" />
<img width="1707" height="936" alt="Screenshot 2025-08-08 at 11 38 51 AM" src="https://github.com/user-attachments/assets/097fe478-9294-4ef1-ad7f-b0048a9813c3" />
<img width="1707" height="936" alt="Screenshot 2025-08-08 at 11 39 00 AM" src="https://github.com/user-attachments/assets/e05bdc47-4044-4a6d-b2b2-635eeac33ce5" />
<img width="1707" height="936" alt="Screenshot 2025-08-08 at 11 39 09 AM" src="https://github.com/user-attachments/assets/4dda38b0-5eb6-473e-b506-f92b950cce3f" />



