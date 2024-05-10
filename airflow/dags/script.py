import ast
import re
from pathlib import Path

import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Create TF-IDF representation


def clean_text(text):

    # Remove text between parentheses
    text = re.sub(r"\([^)]*\)", " ", text)

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Remove numbers
    text = re.sub(r"\d+", "", text)

    # Convert text to lowercase
    text = text.lower()

    # Tokenize text
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Join tokens back into a single string
    cleaned_text = " ".join(tokens)

    return cleaned_text


def proprocess_pub_raw(df_pub_raw: pd.DataFrame):

    df_pub_raw_explode = df_pub_raw.explode(["affilname", "affilcity", "affilcountry"])
    affiliate_df = (
        df_pub_raw_explode[["affilname", "affilcity", "affilcountry"]]
        .drop_duplicates()
        .reset_index(drop=True)
        .reset_index(names="id")
    )
    df_pub_raw_explode = df_pub_raw_explode.merge(
        affiliate_df, how="left", on=["affilname", "affilcity", "affilcountry"]
    )
    df_pub_merge_aff = (
        df_pub_raw_explode.groupby("title")["id"].apply(list).to_frame().reset_index()
    )
    df_pub_raw = df_pub_raw.merge(df_pub_merge_aff, on="title")[
        ["title", "abstracts", "id", "link"]
    ].rename(columns={"id": "affiliation_id"})
    df_pub_raw = df_pub_raw.reset_index(names="id")

    return df_pub_raw, affiliate_df


def preprocess_df_ref(df_ref: pd.DataFrame, df_pub: pd.DataFrame):
    df_ref["title_ref"] = df_ref["title_ref"].str.lower()
    df_count = df_ref.groupby("title_ref").count()
    df_ref_new = df_ref[df_ref["title_ref"].isin(df_count[df_count["title"] > 1].index)]
    df_merge = df_ref_new.merge(
        df_ref_new[["title_ref", "title"]],
        on=["title_ref"],
        how="left",
        suffixes=("", "_2"),
    )
    df_merge = df_merge[df_merge["title"] != df_merge["title_2"]]
    group_fre = (
        df_merge.groupby(["title", "title_2"])
        .count()
        .sort_values("title_ref", ascending=False)
        .reset_index()
    )
    group_fre.columns = ["title", "title_2", "count", "count_2"]
    group_fre = group_fre.drop(columns=["count_2"])
    df_dropdup = df_merge.drop_duplicates(subset=["title", "title_2"])
    df_dropdup = df_dropdup.merge(group_fre, on=["title", "title_2"], how="left")

    df_ref_merge_id = df_dropdup.merge(df_pub[["title", "id"]], on="title", how="left")
    df_ref_merge_id = df_ref_merge_id[df_ref_merge_id.id.notna()]
    df_ref_merge_id = df_ref_merge_id.merge(
        df_pub[["title", "id"]],
        left_on="title_2",
        right_on="title",
        how="inner",
        suffixes=("", "_3"),
    )
    df_ref_merge_id = df_ref_merge_id[["id", "id_3", "count", "year"]]
    df_ref_merge_id = df_ref_merge_id.astype(
        {"id": "int", "id_3": "int", "count": "int"}
    )
    df_ref_merge_id.columns = ["source", "target", "weight", "year"]
    return df_ref_merge_id


def create_similarity_matrix(list_abstracts: list[str]):
    # Create TF-IDF representation
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(list_abstracts)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity_matrix


def turn_id_to_idx(pub_id: int):
    return pub_id


def turn_idx_to_id(pub_idx: int):
    return pub_idx


def recommend_publications(
    pub_id: int, similarity_matrix, page_size: int = 10, page: int = 1
):
    # Get similarity scores

    similarity_scores = similarity_matrix[pub_id]

    # Get indices of publications similar to the target publication
    similar_pub_indices = similarity_scores.argsort()[::-1]
    similar_pub_indices = similar_pub_indices[similar_pub_indices != pub_id]
    similar_pub_indices = similar_pub_indices[(page - 1) * page_size : page * page_size]
    similar_pub_indices = [turn_idx_to_id(idx) for idx in similar_pub_indices]
    return similar_pub_indices


def add_rec_to_pub(df_pub: pd.DataFrame):
    df_pub["abstracts_preprocess"] = df_pub["abstracts"].apply(clean_text)
    similiar_matrix = create_similarity_matrix(df_pub["abstracts_preprocess"].to_list())
    df_pub = df_pub.drop(columns="id").reset_index(drop=True).reset_index(names="id")
    df_pub["rec"] = df_pub["id"].apply(
        lambda x: recommend_publications(x, similiar_matrix)
    )
    df_pub = df_pub.drop(columns="abstracts_preprocess")
    return df_pub


def load_data():
    import pandas as pd

    # lat_lon_ciry = pd.DataFrame(columns=["affilcity","lat","lon"])
    lat_lon_ciry = pd.read_csv("./data_raw/worldcities.csv")
    df_ref = pd.read_csv("./data_raw/ref_raw.csv")
    df_pub = pd.read_csv("./data_raw/pub_raw.csv")

    lat_lon_ciry = lat_lon_ciry[["city_ascii", "lat", "lng"]].rename(
        columns={"city_ascii": "affilcity", "lat": "lat", "lng": "lon"}
    )
    lat_lon_ciry["lat"] = lat_lon_ciry["lat"].astype(float)
    lat_lon_ciry["lon"] = lat_lon_ciry["lon"].astype(float)

    if "sourcetitle" in df_ref.columns:
        df_ref = df_ref.drop(columns="sourcetitle")
    if "sourcetitle" in df_pub.columns:
        df_pub = df_pub.drop(columns="sourcetitle")

    df_pub = df_pub[(df_pub["abstracts"].notna()) & (df_pub["title"].notna())]
    df_pub["len"] = df_pub["title"].str.len()
    for col in ["affilname", "affilcity", "affilcountry"]:
        df_pub[col] = df_pub[col].apply(ast.literal_eval)
    return df_ref, df_pub, lat_lon_ciry


def load_new_pub(paper_info_path: str, ref_info_path: str):
    dftp = pd.read_csv(paper_info_path)
    dfref = pd.read_csv(ref_info_path)

    # preprocess dftp
    dfref = dfref.merge(dftp[["id", "title"]])
    dfref = dfref[["title", "ref_publicationyear", "ref_title"]].rename(
        columns={"ref_publicationyear": "year", "ref_title": "title_ref"}
    )
    dfref = dfref[dfref["title_ref"].notna()]

    # preprocess dftp
    dftp.drop(columns=["Unnamed: 0"], inplace=True)
    dftp = dftp[["title", "abstract", "affiliation", "link"]].rename(
        columns={"abstract": "abstracts"}
    )
    dftp["affiliation"] = dftp["affiliation"].apply(ast.literal_eval)
    dftp["affilname"] = dftp["affiliation"].apply(lambda x: [i[0] for i in x])
    dftp["affilcity"] = dftp["affiliation"].apply(lambda x: [i[1] for i in x])
    dftp["affilcountry"] = dftp["affiliation"].apply(lambda x: [i[2] for i in x])
    dftp = dftp.drop(columns=["affiliation"])

    return dftp, dfref


def merge_save_new_pub(
    df_pub: pd.DataFrame,
    df_ref: pd.DataFrame,
    df_pub_new: pd.DataFrame,
    df_ref_new: pd.DataFrame,
):
    df_pub = pd.concat([df_pub, df_pub_new])
    df_ref = pd.concat([df_ref, df_ref_new])
    df_pub = df_pub.drop_duplicates(subset=["title"])
    df_ref = df_ref.drop_duplicates(subset=["title", "title_ref"])

    df_pub = df_pub[df_pub["title"].notna() & df_pub["abstracts"].notna()]
    df_pub.to_csv("./data_raw/pub_raw.csv", index=False)
    df_ref.to_csv("./data_raw/ref_raw.csv", index=False)
    return df_pub, df_ref


def main(paper_info_path: str, ref_info_path: str):
    print("Start")
    df_ref, df_pub, lat_lon_ciry = load_data()
    df_pub_new, df_ref_new = load_new_pub(paper_info_path, ref_info_path)
    df_pub, df_ref = merge_save_new_pub(df_pub, df_ref, df_pub_new, df_ref_new)
    print("Data loaded")
    df_pub, affiliate_df = proprocess_pub_raw(df_pub)
    affiliate_df = affiliate_df.merge(lat_lon_ciry, on="affilcity", how="left")
    print("Data preprocessed")
    df_pub_preprocess = add_rec_to_pub(df_pub)
    print("Recommendation added")
    df_ref_merge_id = preprocess_df_ref(df_ref, df_pub)
    print("Save data")
    affiliate_df.to_csv("./data_process/affiliation.csv", index=False)
    df_pub_preprocess.to_csv("./data_process/pub_preprocessed.csv", index=False)
    df_ref_merge_id.to_csv("./data_process/ref_preprocessed.csv", index=False)
