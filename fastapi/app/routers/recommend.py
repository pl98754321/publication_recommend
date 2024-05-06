from fastapi import APIRouter, Depends

from ..config import VERSION
from ..schemas import AutocompleteResp, HelloResp, PubDetailResp
from ..utils import auto_complete_from_query, get_pub_details

router = APIRouter(prefix="", tags=["course"])


@router.get("/hello_world", response_model=HelloResp)
def hello_world():
    return {"message": "Hello World", "version": VERSION}


# Recommendation endpoint
@router.get("/auto_complete", response_model=AutocompleteResp)
def get_auto_complete(query: str, page: int = 1, page_size: int = 20):
    return auto_complete_from_query(query, page, page_size)


# Recommendation endpoint
@router.get("/publication/{pub_id}", response_model=PubDetailResp)
def api_get_pub_details(pub_id: int, lower_bound: int = 0):
    return get_pub_details(pub_id, lower_bound)
