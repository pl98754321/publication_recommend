import math

from fastapi import HTTPException

from ..services import pub_dataloader


def auto_complete_from_query(query: str, page: int = 1, page_size: int = 5):
    """
    Get autocomplete results from a query
    """

    df_pub = pub_dataloader.get_data()
    if df_pub is None:
        raise HTTPException(status_code=503, detail="Data not available")
    df_contain = df_pub[df_pub["title"].str.lower().str.contains(query)]
    if df_contain.empty:
        return {"pubs": [], "current_page": page, "total_num": 0}
    df_contain.loc[:, "ind"] = df_contain["title"].str.lower().str.find(query)
    df_selected = df_contain.sort_values(["ind", "len"]).iloc[
        (page - 1) * page_size : page * page_size
    ]
    return {
        "pubs": df_selected[["title", "index"]]
        .rename(columns={"index": "id"})
        .to_dict(orient="records"),
        "current_page": page,
        "total_num": df_contain.shape[0],
        "total_page": math.ceil(df_contain.shape[0] / page_size),
    }


def get_course_details(course_id: int):
    """
    Get course details
    """
    return {"course_id": course_id, "course_name": "Course Name"}
