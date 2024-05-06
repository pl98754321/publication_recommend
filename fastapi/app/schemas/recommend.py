from pydantic import BaseModel


class HelloResp(BaseModel):
    message: str
    version: str


class affilResp(BaseModel):
    lat: float | None
    lng: float | None
    affiliation: str


class PubResp(BaseModel):
    title: str
    id: int
    affilations: list[affilResp]


class AutocompleteResp(BaseModel):
    pubs: list[PubResp]
    current_page: int
    total_num: int
    total_page: int


class EdgeResp(BaseModel):
    source: int
    target: int
    weight: float


class NodeGraphResp(BaseModel):
    edge: list[EdgeResp]
    node: list[PubResp]


class PubDetailResp(PubResp):
    abstract: str
    link: str
    pub_rec: list[PubResp]
    node_graph: NodeGraphResp
