import pandas as pd
from abc import ABC, abstractmethod

class DataSource(ABC):
    def __init__(self):
        self.data = None
        super().__init__()

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        pass

    # TODO: Depricate and let data_handler write files
    @abstractmethod
    def write(self, filepath: str):
        pass

    @abstractmethod
    def get_time(self):
        pass
