from pydantic import BaseModel


class CourseResp(BaseModel):
    course_name: str
    course_id: int


class AutocompleteResp(BaseModel):
    courses: list[CourseResp]
    current_page: int
    total_num: int


class HelloResp(BaseModel):
    message: str
    version: str


class RecommendResp(BaseModel):
    course_name: str
    course_x: float
    course_y: float
    score: float


class CourseDetailResp(BaseModel):
    course_id: int
    course_name: str
    course_abstract: str
    courses_recommend: list[RecommendResp]
