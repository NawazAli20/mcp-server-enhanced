from pathlib import Path
import json
from typing import Any

from mcp.server.fastmcp import FastMCP 

mcp = FastMCP(
    name="Teaching Assistant",
    instructions="""You will provide course information using two tools.
    convert course into CS111, if user enter cs 111.  
    """
)

DATA_FILE = Path(__file__).resolve().parent/"data"/"courses.json"

## Helper function 
def _load_courses()->list[dict[str,Any]]:
    """Return list of courses"""
    try:
        with DATA_FILE.open(encoding="utf-8") as file: 
            courses = json.load(file)
            return courses
    except Exception as e:
        return [{"error":f"File handling error. {e}"}]

##helper function 
def _normalized_course_id(course:str)->str:
    """Return course in a normalized form. CS111 : "".join(["CS","111"])"""
    normalized_course_id = "".join(course.upper().split())
    return normalized_course_id

@mcp.tool()
def get_course_list()->list[dict[str,Any]]:
    """return list of available courses"""
    return[
        {
            "Course code":course["course_id"],
            "Title":course["title"]
        }
        for course in _load_courses()
    ] 

@mcp.tool()
def get_course_details(course_id:str)->dict[str,Any]:
    """Return detailed course information of a given course"""
    normalized_course_id = _normalized_course_id(course_id)

    for course in _load_courses():
        if _normalized_course_id(course["course_id"]) == normalized_course_id:
            return course

    available_courses = [course["course_id"] for course in _load_courses()]
    return {
        "Error":f"{course_id} is not available",
        "Available courses":available_courses
    }

# -----------------------
# RESOURCES
# -----------------------
@mcp.resource("course://catalog")
def course_catalog()->str:
    """"Return information about the course catalog"""

    return json.dumps(
        _load_courses(),
        indent=2
    )

@mcp.resource("course://{course_id}")
def course_resource(course_id:str)->str:
    """Return a specific course information"""
    return json.dumps(
        get_course_details(course_id),
        indent=2
    )




# -----------------------
# PROMPTS
# -----------------------
@mcp.prompt()
def all_course_summary()->str:
    """Prompt for summarizing all courses in the catalog"""
    return f"""Using the course assistant tools and resources summarize all catalog courses
    
    Include: 
    - Course description 
    - Course prerequisites
    - Course Learning Objectives 
    - Expected Student Outcomes 
    """

@mcp.prompt()
def course_summary(course_id:str)->str:
    """Prompt for summarizing all courses in the catalog"""
    return f"""Using the course assistant tools and resources summarize {course_id} courses
    
    Include: 
    - Course description 
    - Course prerequisites
    - Course Learning Objectives 
    - Expected Student Outcomes 
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")