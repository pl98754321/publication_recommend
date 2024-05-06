import numpy as np


class NpDataLoader:
    def __init__(self, path: str):
        self.update_data(path)

    def update_data(self, path1: str):
        """
        Update data
        """
        self.is_avaliable = False
        with open(path1, "rb") as f:
            self.np = np.load(f)
        self.is_avaliable = True

    def get_data(self):
        if self.is_avaliable:
            return self.np
        return None
