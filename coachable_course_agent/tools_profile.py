from langchain.tools import Tool
from coachable_course_agent.linkedin_tools import extract_profile_info, build_profile_from_bio
# Import other dependencies as needed from linkedin_tools

def get_skill_tool(vectorstore):
    from coachable_course_agent.linkedin_tools import get_skill_tool as _get_skill_tool
    return _get_skill_tool(vectorstore)

def get_save_profile_tool(user_id):
    from coachable_course_agent.linkedin_tools import get_save_profile_tool as _get_save_profile_tool
    return _get_save_profile_tool(user_id)

def get_infer_skills_tool(vectorstore):
    from coachable_course_agent.linkedin_tools import get_infer_skills_tool as _get_infer_skills_tool
    return _get_infer_skills_tool(vectorstore)

profile_extract_tool = Tool.from_function(
    name="ExtractProfileFromText",
    func=extract_profile_info,
    description=(
        "Given a free-form LinkedIn profile text, extracts a short career headline, "
        "a list of up to 10 professional skills, and an inferred learning or career goal. "
        "Input should be raw profile text. "
        "After extracting skills, always match them to ESCO concepts and save only the matched preferredLabel and conceptUri into the user profile."
    )
)
