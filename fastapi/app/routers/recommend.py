from fastapi import APIRouter, Depends

from ..config import VERSION
from ..schemas import AutocompleteResp, CourseDetailResp, HelloResp
from ..utils import auto_complete_from_query, get_course_details

router = APIRouter(prefix="", tags=["course"])


@router.get("/hello_world", response_model=HelloResp)
def hello_world():
    return {"message": "Hello World", "version": VERSION}


# Recommendation endpoint
@router.get("/auto_complete", response_model=AutocompleteResp)
def get_auto_complete(query: str, page: int = 1, page_size: int = 20):
    return auto_complete_from_query(query, page, page_size)


# Recommendation endpoint
@router.get("/course/{course_id}", response_model=CourseDetailResp)
def recommend_courses_for_user(course_id: int):
    return get_course_details(course_id)
