from .dataloader import *
from .dataloader_np import *
from .logger import get_logger

pub_dataloader = PubDataLoader(r"./data_process/pub.csv")
ref_dataloader = RefDataLoader(r"./data_process/ref.csv")
aff_dataloader = AffilDataLoader(r"./data_process/affiliation.csv")
