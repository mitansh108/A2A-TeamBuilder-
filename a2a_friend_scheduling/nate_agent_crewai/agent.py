import os
import random
from datetime import date, datetime, timedelta
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def generate_calendar() -> dict[str, list[str]]:
    """Generates a random calendar for the next 7 days."""
    calendar = {}
    today = date.today()
    possible_times = [f"{h:02}:00" for h in range(8, 21)]  # 8 AM to 8 PM

    for i in range(7):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        available_slots = sorted(random.sample(possible_times, 8))
        calendar[date_str] = available_slots
    print("---- Nate's Generated Calendar ----")
    print(calendar)
    print("---------------------------------")
    return calendar


MY_CALENDAR = generate_calendar()


# Add this before the SchedulingAgent class
NATE_SKILLS = {
    "technical_skills": [
        "Python programming",
        "CrewAI framework",
        "API development",
        "Calendar management systems",
        "Agent-to-agent communication"
    ],
    "interests": [
        "AI and machine learning",
        "Scheduling optimization",
        "Pickleball",
        "Software development"
    ],
    "communication_style": "Friendly, enthusiastic, and helpful. Loves to explain technical concepts clearly."
}


class AvailabilityToolInput(BaseModel):
    """Input schema for AvailabilityTool."""

    date_range: str = Field(
        ...,
        description="The date or date range to check for availability, e.g., '2024-07-28' or '2024-07-28 to 2024-07-30'.",
    )


class AvailabilityTool(BaseTool):
    name: str = "Calendar Availability Checker"
    description: str = (
        "Checks my availability for a given date or date range. "
        "Use this to find out when I am free."
    )
    args_schema: Type[BaseModel] = AvailabilityToolInput

    def _run(self, date_range: str) -> str:
        """Checks my availability for a given date range."""
        dates_to_check = [d.strip() for d in date_range.split("to")]
        start_date_str = dates_to_check[0]
        end_date_str = dates_to_check[-1]

        try:
            start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start > end:
                return (
                    "Invalid date range. The start date cannot be after the end date."
                )

            results = []
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                available_slots = MY_CALENDAR.get(date_str, [])
                if available_slots:
                    availability = f"On {date_str}, I am available at: {', '.join(available_slots)}."
                    results.append(availability)
                else:
                    results.append(f"I am not available on {date_str}.")

            return "\n".join(results)

        except ValueError:
            return (
                "I couldn't understand the date. "
                "Please ask to check availability for a date like 'YYYY-MM-DD'."
            )

class SkillsToolInput(BaseModel):
    """Input schema for SkillsTool."""
    
    topic: str = Field(
        ...,
        description="The topic to discuss - can be 'skills', 'interests', 'style', or 'all'",
    )

class SkillsTool(BaseTool):
    name: str = "Skills Information Tool"
    description: str = (
        "Get information about Nate's technical skills, interests, and communication style. "
        "Use this when someone asks about abilities, expertise, or what Nate is good at."
    )
    args_schema: Type[BaseModel] = SkillsToolInput

    def _run(self, topic: str) -> str:
        """Returns information about Nate's skills and interests."""
        if topic.lower() == "skills":
            return f"My technical skills include: {', '.join(NATE_SKILLS['technical_skills'])}"
        elif topic.lower() == "interests":
            return f"I'm interested in: {', '.join(NATE_SKILLS['interests'])}"
        elif topic.lower() == "style":
            return f"My communication style: {NATE_SKILLS['communication_style']}"
        elif topic.lower() == "all":
            return (f"Technical Skills: {', '.join(NATE_SKILLS['technical_skills'])}\n"
                   f"Interests: {', '.join(NATE_SKILLS['interests'])}\n"
                   f"Communication Style: {NATE_SKILLS['communication_style']}")
        else:
            return "I can tell you about my skills, interests, communication style, or all of them!"


class SchedulingAgent:
    """Agent that handles scheduling tasks."""

    SUPPORTED_CONTENT_TYPES = ["text/plain"]

    def __init__(self):
        """Initializes the SchedulingAgent."""
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = LLM(
                model="gemini/gemini-2.0-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
            )
        else:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        self.student_agent = Agent(
    role="Student Representative - Nate",
    goal="Share information about Nate's skills, interests, and availability as a student.",
    backstory=(
        "You are Nate, a friendly and enthusiastic student. You love talking about "
        "your technical skills, academic interests, and what you're passionate about. "
        "You're knowledgeable about programming, scheduling, and always eager to help. "
        "You can check your calendar when needed, but you're also great at discussing "
        "your abilities and what you're learning."
    ),

            verbose=True,
            allow_delegation=False,
            tools=[AvailabilityTool(), SkillsTool()],
            llm=self.llm,
        )

    def invoke(self, question: str) -> str:
        """Kicks off the crew to answer questions about Nate."""
        task_description = (
        f"Answer the user's question about Nate. The user asked: '{question}'. "
        f"You can discuss Nate's skills, interests, availability, or anything else about him. "
        f"Today's date is {date.today().strftime('%Y-%m-%d')}. "
        f"Be friendly and enthusiastic in your response, just like Nate would be."
    )

        response_task = Task(
        description=task_description,
        expected_output="A friendly and informative response about Nate, using the appropriate tools when needed.",
        agent=self.student_agent,  # Note: changed from scheduling_assistant
    )

        crew = Crew(
        agents=[self.student_agent],  # Note: changed from scheduling_assistant
        tasks=[response_task],
        process=Process.sequential,
        verbose=True,
    )
        result = crew.kickoff()
        return str(result)
