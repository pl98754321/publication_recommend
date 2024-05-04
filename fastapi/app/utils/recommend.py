def auto_complete_from_query(query: str, page: int = 1, page_size: int = 5):
    """
    Get autocomplete results from a query
    """
    return {"query": query, "results": ["result1", "result2"]}


def get_course_details(course_id: int):
    """
    Get course details
    """
    return {"course_id": course_id, "course_name": "Course Name"}
