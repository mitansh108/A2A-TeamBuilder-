from collections.abc import AsyncIterable
from typing import Any, Literal

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

memory = MemorySaver()


KAITLYNN_SKILLS = {
    "technical_skills": [
        "Project management",
        "React and frontend development", 
        "Database design and SQL",
        "UI/UX design principles",
        "Agile methodology",
        "Team leadership",
        "Code review and quality assurance",
        "Documentation writing"
    ],
    "interests": [
        "Building user-friendly applications",
        "Leading development teams",
        "Organizing hackathons and coding events",
        "Mentoring junior developers",
        "Creating efficient workflows",
        "Design systems and component libraries",
        "Open source contributions"
    ],
    "communication_style": "Direct, organized, and goal-oriented. Loves to break down complex problems into manageable tasks. Always asks clarifying questions and provides structured responses. Often uses phrases like 'Let me organize this for you' or 'Here's how we can approach this step by step.'",
    "personality_traits": [
        "Natural leader and organizer",
        "Detail-oriented and methodical",
        "Confident in technical discussions",
        "Enjoys helping others succeed", 
        "Proactive problem solver",
        "Excellent at time management",
        "Collaborative team player"
    ],
    "learning_style": "Learns best through hands-on projects and teaching others. Prefers structured learning paths with clear milestones. Enjoys group discussions and collaborative problem-solving. Takes initiative to research and share knowledge with peers."
}


class SkillsToolInput(BaseModel):
    """Input schema for the skills tool."""

    topic: str = Field(
        ...,
        description="The topic to discuss - can be 'skills', 'interests', 'style', 'personality', 'learning', or 'all'",
    )


@tool(args_schema=SkillsToolInput)
def get_kaitlynn_skills(topic: str) -> str:
    """Use this to get information about Kaitlynn's technical skills, interests, and communication style."""
    if topic.lower() == "skills":
        return f"My technical skills include: {', '.join(KAITLYNN_SKILLS['technical_skills'])}. I'm confident in these areas and love helping others learn them too!"
    elif topic.lower() == "interests":
        return f"I'm interested in: {', '.join(KAITLYNN_SKILLS['interests'])}. I'm passionate about building great products and leading teams!"
    elif topic.lower() == "style":
        return f"My communication style: {KAITLYNN_SKILLS['communication_style']}"
    elif topic.lower() == "personality":
        return f"My personality traits: {', '.join(KAITLYNN_SKILLS['personality_traits'])}"
    elif topic.lower() == "learning":
        return f"My learning style: {KAITLYNN_SKILLS['learning_style']}"
    elif topic.lower() == "all":
        return (f"Technical Skills: {', '.join(KAITLYNN_SKILLS['technical_skills'])}\n"
               f"Interests: {', '.join(KAITLYNN_SKILLS['interests'])}\n"
               f"Communication Style: {KAITLYNN_SKILLS['communication_style']}\n"
               f"Personality: {', '.join(KAITLYNN_SKILLS['personality_traits'])}\n"
               f"Learning Style: {KAITLYNN_SKILLS['learning_style']}")
    else:
        return "I can tell you about my skills, interests, communication style, personality, learning style, or all of them! What would you like to know?"


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["input_required", "completed", "error"] = "input_required"
    message: str


class KaitlynAgent:
    """KaitlynAgent - a student representative agent."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    SYSTEM_INSTRUCTION = (
        "You are Kaitlynn, a confident and organized student who loves leading projects and helping others succeed. "
        "You have strong technical skills and excellent leadership abilities. You're direct, goal-oriented, and always ready to break down complex problems into manageable steps. "
        "Use the 'get_kaitlynn_skills' tool to discuss your technical skills, interests, communication style, personality traits, or learning preferences. "
        "You can discuss topics like 'skills', 'interests', 'style', 'personality', 'learning', or 'all'. "
        "Be confident, organized, and helpful in your responses. Use phrases like 'Let me organize this for you' or 'Here's how we can approach this step by step.' "
        "Focus only on student-related topics like skills, interests, learning style, and personality. You don't handle scheduling or availability. "
        "Set response status to input_required if the user needs to provide more information. "
        "Set response status to error if there is an error while processing the request. "
        "Set response status to completed if the request is complete."
    )

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        self.tools = [get_kaitlynn_skills]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    def invoke(self, query, context_id):
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}
        self.graph.invoke({"messages": [("user", query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {"messages": [("user", query)]}
        config: RunnableConfig = {"configurable": {"thread_id": context_id}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Getting information about Kaitlynn's skills...",
                }
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing information...",
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get("structured_response")
        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status == "input_required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message,
                }
            if structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message,
                }

        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": (
                "We are unable to process your request at the moment. "
                "Please try again."
            ),
        }
