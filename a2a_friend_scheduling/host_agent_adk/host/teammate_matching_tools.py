"""
Teammate Matching Tools for Student Agent Compatibility Analysis
"""

from typing import Dict, List, Tuple, Any
from google.adk.tools.tool_context import ToolContext


class TeammateMatchingEngine:
    """Engine for analyzing student compatibility and finding optimal teammates."""
    
    def __init__(self, remote_agent_connections: Dict[str, Any]):
        self.remote_agent_connections = remote_agent_connections
    
    def analyze_compatibility(self, requester_profile: str, candidate_profile: str) -> Tuple[float, str]:
        """Analyzes compatibility between two student profiles and returns a score with reasoning."""
        
        # Convert profiles to lowercase for analysis
        req_profile = requester_profile.lower()
        cand_profile = candidate_profile.lower()
        
        compatibility_score = 0.0
        reasoning_points = []
        
        # Define skill categories and keywords
        frontend_skills = ['html', 'css', 'javascript', 'react', 'ui', 'ux', 'frontend', 'design', 'responsive']
        backend_skills = ['python', 'api', 'backend', 'database', 'sql', 'server', 'crewai']
        leadership_skills = ['leadership', 'project management', 'team', 'organize', 'mentor', 'lead']
        communication_styles = {
            'introvert': ['introvert', 'quiet', 'reserved', 'shy', 'thoughtful', 'prefer written'],
            'extrovert': ['extrovert', 'enthusiastic', 'outgoing', 'friendly', 'loves explaining', 'confident']
        }
        experience_levels = {
            'beginner': ['basic', 'learning', 'beginner', 'still learning', 'not confident', 'improving'],
            'advanced': ['expert', 'experienced', 'advanced', 'confident', 'strong', 'excellent']
        }
        
        # Analyze skill complementarity
        req_frontend = any(skill in req_profile for skill in frontend_skills)
        req_backend = any(skill in req_profile for skill in backend_skills)
        req_leadership = any(skill in req_profile for skill in leadership_skills)
        
        cand_frontend = any(skill in cand_profile for skill in frontend_skills)
        cand_backend = any(skill in cand_profile for skill in backend_skills)
        cand_leadership = any(skill in cand_profile for skill in leadership_skills)
        
        # Skill complementarity scoring
        if req_frontend and cand_backend:
            compatibility_score += 30
            reasoning_points.append("Frontend + Backend skill complementarity")
        elif req_backend and cand_frontend:
            compatibility_score += 30
            reasoning_points.append("Backend + Frontend skill complementarity")
        
        if req_leadership and not cand_leadership:
            compatibility_score += 20
            reasoning_points.append("Leadership + Technical collaboration")
        elif not req_leadership and cand_leadership:
            compatibility_score += 20
            reasoning_points.append("Technical + Leadership collaboration")
        
        # Communication style balance
        req_introvert = any(word in req_profile for word in communication_styles['introvert'])
        req_extrovert = any(word in req_profile for word in communication_styles['extrovert'])
        cand_introvert = any(word in cand_profile for word in communication_styles['introvert'])
        cand_extrovert = any(word in cand_profile for word in communication_styles['extrovert'])
        
        if (req_introvert and cand_extrovert) or (req_extrovert and cand_introvert):
            compatibility_score += 25
            reasoning_points.append("Balanced introvert-extrovert communication styles")
        
        # Experience level balance
        req_beginner = any(word in req_profile for word in experience_levels['beginner'])
        req_advanced = any(word in req_profile for word in experience_levels['advanced'])
        cand_beginner = any(word in cand_profile for word in experience_levels['beginner'])
        cand_advanced = any(word in cand_profile for word in experience_levels['advanced'])
        
        if (req_beginner and cand_advanced) or (req_advanced and cand_beginner):
            compatibility_score += 15
            reasoning_points.append("Mentor-learner experience balance")
        
        # Interest overlap (small bonus for shared interests)
        common_interests = []
        interest_keywords = ['ai', 'machine learning', 'web development', 'programming', 'design', 'projects']
        for interest in interest_keywords:
            if interest in req_profile and interest in cand_profile:
                common_interests.append(interest)
        
        if common_interests:
            compatibility_score += 10
            reasoning_points.append(f"Shared interests: {', '.join(common_interests)}")
        
        # Create reasoning string
        if reasoning_points:
            reasoning = "Strong compatibility due to: " + "; ".join(reasoning_points)
        else:
            reasoning = "Basic compatibility - could work well together with some shared foundation"
            compatibility_score += 5  # Base compatibility score
        
        return compatibility_score, reasoning

    async def get_student_profile(self, agent_name: str, send_message_func, tool_context: ToolContext) -> str:
        """Gets a student's complete profile using the send_message function."""
        try:
            response = await send_message_func(
                agent_name,
                "Tell me about all your skills, interests, and communication style",
                tool_context
            )
            if response:
                profile_text = ""
                for part in response:
                    if isinstance(part, dict) and "text" in part:
                        profile_text += part["text"] + " "
                return profile_text.strip()
        except Exception as e:
            print(f"Error getting profile from {agent_name}: {e}")
        return ""

    async def find_best_teammate(self, requester_name: str, send_message_func, tool_context: ToolContext) -> str:
        """Finds the best teammate for a specific student based on dynamic profile analysis."""
        print(f"Finding best teammate for {requester_name}...")
        
        # Step 1: Get the requester's profile
        requester_profile = ""
        if requester_name in self.remote_agent_connections:
            requester_profile = await self.get_student_profile(requester_name, send_message_func, tool_context)
        else:
            return f"Sorry, I couldn't find a student named '{requester_name}'. Available students: {', '.join(self.remote_agent_connections.keys())}"
        
        if not requester_profile:
            return f"Unable to get profile information for {requester_name}"
        
        # Step 2: Get profiles of all other students
        other_students = {}
        for agent_name in self.remote_agent_connections.keys():
            if agent_name != requester_name:  # Don't include the requester
                profile = await self.get_student_profile(agent_name, send_message_func, tool_context)
                if profile:
                    other_students[agent_name] = profile
                else:
                    other_students[agent_name] = "Profile unavailable"
        
        if not other_students:
            return "No other students available for matching."
        
        # Step 3: Analyze compatibility with each potential teammate
        best_match = None
        highest_score = 0
        best_reasoning = ""
        all_matches = []
        
        for candidate_name, candidate_profile in other_students.items():
            score, reasoning = self.analyze_compatibility(requester_profile, candidate_profile)
            all_matches.append((candidate_name, score, reasoning))
            
            if score > highest_score:
                highest_score = score
                best_match = candidate_name
                best_reasoning = reasoning
        
        # Step 4: Format the response
        if best_match:
            result = f"## 🎯 Best Teammate Recommendation for {requester_name}\n\n"
            result += f"**Recommended Partner:** {best_match}\n"
            result += f"**Compatibility Score:** {highest_score:.1f}/100\n"
            result += f"**Why this match works:** {best_reasoning}\n\n"
            
            result += f"**Your Profile Summary:**\n{requester_profile[:300]}...\n\n"
            result += f"**{best_match}'s Profile Summary:**\n{other_students[best_match][:300]}...\n\n"
            
            # Show other potential matches
            if len(all_matches) > 1:
                result += "**Other Potential Matches:**\n"
                sorted_matches = sorted(all_matches, key=lambda x: x[1], reverse=True)
                for name, score, reasoning in sorted_matches[1:3]:  # Show top 2 alternatives
                    result += f"- **{name}** (Score: {score:.1f}) - {reasoning[:100]}...\n"
            
            return result
        else:
            return "Unable to find a suitable teammate match."


# Global instance will be initialized by the agent
teammate_engine: TeammateMatchingEngine = None


def initialize_teammate_engine(remote_agent_connections: Dict[str, Any]):
    """Initialize the global teammate matching engine."""
    global teammate_engine
    teammate_engine = TeammateMatchingEngine(remote_agent_connections)


async def find_best_teammate_tool(requester_name: str, send_message_func, tool_context: ToolContext) -> str:
    """Tool function for finding the best teammate - to be used by the agent."""
    if teammate_engine is None:
        return "Teammate matching engine not initialized."
    
    return await teammate_engine.find_best_teammate(requester_name, send_message_func, tool_context)