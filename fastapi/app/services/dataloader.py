# implements the dalaloader with lock and cache
import json
from abc import ABC, abstractmethod

import pandas as pd


class DataLoader(ABC):
    def __init__(self, path: str, list_need_col: list[str] | None = None):
        self.list_need_col = list_need_col or []
        self.update_data(path)

    def check_column(self, df: pd.DataFrame) -> None:
        if len(self.list_need_col) > 0:
            for col in self.list_need_col:
                if col not in df.columns:
                    raise ValueError(f"Missing column {col}")

    def update_data(self, path1: str):
        """
        Update data
        """
        self.is_avaliable = False
        self.cache = {}
        csv = pd.read_csv(path1)
        self.check_column(csv)
        self.csv = self.preprocess_df(csv)
        self.is_avaliable = True

    def get_data(self) -> None | pd.DataFrame:
        if self.is_avaliable:
            return self.csv
        return None

    @abstractmethod
    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class PubDataLoader(DataLoader):
    def __init__(self, path: str):
        super().__init__(path, ["id", "title", "abstracts", "affiliation_id", "link"])

    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        def jsonify(x):
            return json.loads(x)

        # df = df[~df["abstracts"].isna()]
        # df = df[~df["title"].isna()]
        df["len"] = df["title"].str.len()
        df["affiliation_id"] = df["affiliation_id"].apply(jsonify)
        return df


class AffilDataLoader(DataLoader):
    def __init__(self, path: str):
        super().__init__(
            path, ["id", "affilname", "affilcity", "affilcountry", "lat", "lon"]
        )

    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


class RefDataLoader(DataLoader):
    def __init__(self, path: str):
        super().__init__(path, ["source", "target", "weight"])

    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
