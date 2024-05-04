# implements the dalaloader with lock and cache
import pandas as pd


class DataLoader:
    def __init__(self):
        self.is_avaliable = True
        self.cache = {}
        self.csv = None

    def update_data(self, path1: str):
        """
        Update data
        """
        self.is_avaliable = False
        self.cache = {}
        self.csv = pd.read_csv(path1)
        self.is_avaliable = True

    def get_data(self) -> None | pd.DataFrame:
        if self.is_avaliable:
            return self.csv
        return None
