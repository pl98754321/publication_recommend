import math

import pandas as pd

from fastapi import HTTPException

from ..schemas import (
    AutocompleteResp,
    EdgeResp,
    NodeGraphResp,
    PubDetailResp,
    PubResp,
    affilResp,
)
from ..services import aff_dataloader, pub_dataloader, ref_dataloader

################ BASIC FUNC ################


def get_affil_by_id(list_affi_id: list[int]) -> list[affilResp]:
    """
    Get affiliation by id
    """
    aff_df = aff_dataloader.get_data()
    if aff_df is None:
        raise HTTPException(status_code=503, detail="Data not available")
    aff_df = aff_df[["id", "affilname", "lat", "lon"]]
    df_current_affi = pd.DataFrame({"id": list_affi_id})
    df_current_affi = df_current_affi.merge(aff_df, on="id", how="left")
    dict_ = df_current_affi.to_dict(orient="records")
    result = [
        affilResp(affiliation=aff["affilname"], lat=aff["lat"], lng=aff["lon"])
        for aff in dict_
    ]
    return result


def get_pub_resp_by_id(pub_id: int, need_affil: bool) -> PubResp:
    """
    Get publication response by id
    """
    df_pub = pub_dataloader.get_data()
    if df_pub is None:
        raise HTTPException(status_code=503, detail="Pub Data not available")
    if pub_id not in df_pub["id"].values:
        print("PUB ID NOT FOUND", pub_id)
        raise HTTPException(status_code=404, detail="Pub ID not found")
    pub = df_pub[df_pub["id"] == pub_id].iloc[0]
    if need_affil:
        affi = get_affil_by_id(pub["affiliation_id"])
    else:
        affi = []
    return PubResp(id=pub["id"], title=pub["title"], affilations=affi)


def get_pub_resp_by_list_id(list_pub_id: list[int], need_affil: bool) -> list[PubResp]:
    """
    Get publication response by list id
    """
    return [get_pub_resp_by_id(pub_id, need_affil) for pub_id in list_pub_id]


################ AUTO COMPLETE ################


def auto_complete_from_query(
    query: str, page: int = 1, page_size: int = 5
) -> AutocompleteResp:
    """
    Get autocomplete results from a query
    """

    df_pub = pub_dataloader.get_data()
    if df_pub is None:
        raise HTTPException(status_code=503, detail="Pub Data not available")
    df_contain = df_pub[df_pub["title"].str.lower().str.contains(query)]
    if df_contain.empty:
        return AutocompleteResp(pubs=[], current_page=page, total_num=0, total_page=0)
    df_contain.loc[:, "ind"] = df_contain["title"].str.lower().str.find(query)
    df_selected = df_contain.sort_values(["ind", "len"]).iloc[
        (page - 1) * page_size : page * page_size
    ]
    return AutocompleteResp(
        pubs=get_pub_resp_by_list_id(df_selected["id"].tolist(), need_affil=False),
        current_page=page,
        total_num=df_contain.shape[0],
        total_page=math.ceil(df_contain.shape[0] / page_size),
    )


################ PUB DETAIL ################


def get_edge_resp(pub_id: int, lower_bound: int) -> list[EdgeResp]:
    """
    Get edge response
    """
    ref_df = ref_dataloader.get_data()
    if ref_df is None:
        raise HTTPException(status_code=503, detail="Ref Data not available")
    ref_df = ref_df[(ref_df["source"] == pub_id) & (ref_df["weight"] > lower_bound)]
    [source, target, weight] = ref_df[["source", "target", "weight"]].values.T
    return [
        EdgeResp(source=s, target=t, weight=w)
        for s, t, w in zip(source, target, weight)
    ]


def get_node_graph(pub_id: int, lower_bound: int) -> NodeGraphResp:
    """
    Get node graph
    """
    edges = get_edge_resp(pub_id, lower_bound)
    pub_taget_ids = [edge.target for edge in edges]
    nodes = get_pub_resp_by_list_id(pub_taget_ids, need_affil=True)
    return NodeGraphResp(edge=edges, node=nodes)


def get_pub_rec(pub_id: int, page_size: int = 10, page: int = 1) -> list[PubResp]:
    """
    Get publication recommendation
    """
    df_pub = pub_dataloader.get_data()
    if df_pub is None:
        raise HTTPException(status_code=503, detail="Pub Data not available")
    # Get similarity scores
    similar_pub_indices = df_pub[df_pub["id"] == pub_id].iloc[0]["rec"]
    return get_pub_resp_by_list_id(similar_pub_indices, need_affil=False)


def get_link_and_abstract(pub_id: int) -> tuple[str, str]:
    """
    Get link and abstract
    """
    pub_df = pub_dataloader.get_data()
    if pub_df is None:
        raise HTTPException(status_code=503, detail="Pub Data not available")
    series = pub_df[pub_df["id"] == pub_id]
    link = series["link"].iloc[0]
    abstract = series["abstracts"].iloc[0]
    if pd.isna(link):
        link = ""
    if pd.isna(abstract):
        abstract = ""
    return link, abstract


def get_pub_details(pub_id: int, lower_bound: int) -> PubDetailResp:
    """
    Get course details
    """
    pub_resp = get_pub_resp_by_id(pub_id, need_affil=True)
    pub_rec = get_pub_rec(pub_id)
    link, abstract = get_link_and_abstract(pub_id)
    node_graph = get_node_graph(pub_id, lower_bound)

    pub_detail = PubDetailResp(
        title=pub_resp.title,
        id=pub_resp.id,
        affilations=pub_resp.affilations,
        abstract=abstract,
        link=link,
        pub_rec=pub_rec,
        node_graph=node_graph,
    )
    return pub_detail
