# implements the dalaloader with lock and cache
from abc import ABC, abstractmethod

import pandas as pd


class DataLoader(ABC):
    def __init__(self, path: str):
        self.update_data(path)

    def update_data(self, path1: str):
        """
        Update data
        """
        self.is_avaliable = False
        self.cache = {}
        self.csv = self.preprocess_df(pd.read_csv(path1))
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
        super().__init__(path)

    def preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[~df["abstracts"].isna()]
        df = df[~df["title"].isna()]
        df["len"] = df["title"].str.len()
        df = df.reset_index()
        return df
