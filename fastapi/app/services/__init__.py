from .dataloader import *
from .dataloader_np import *
from .logger import get_logger

pub_dataloader = PubDataLoader(r"./data/pub.csv")
ref_dataloader = RefDataLoader(r"./data/ref.csv")
aff_dataloader = AffilDataLoader(r"./data/affiliation.csv")
sim_dataloader = NpDataLoader(r"./data/similiar_metrix.npy")
