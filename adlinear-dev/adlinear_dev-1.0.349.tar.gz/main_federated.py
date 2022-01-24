import pandas as pd

from adlinear import fed_nmtf as fd
from adlinear import utilities as utl
import root_path
from transparentpath import Path
import os
import dotenv

from adlinear import fed_nmtf

dotenv.load_dotenv()

if __name__ == "__main__":

    # Data localization
    rootpath = root_path.get_root_path()

    rd_path = Path(rootpath / os.getenv("rd_subpath"), fs="local")
    federated_path: object = Path(rd_path / os.getenv("federated_subpath"), fs="local")

    data_path: object = Path(federated_path / os.getenv("data_subpath"), fs="local")

    temp_data_path = Path(data_path / "temp_data/", fs="local")
    pictures_path = Path(data_path / "Pics", fs="local")
    out_data_path = Path(federated_path / "results/", fs="local")

    res_path = Path(federated_path / os.getenv("results_subpath"), fs="local")

    if os.getenv("fed_do_epithor", "False").lower() == "true":

        epithor_filename: str = os.getenv("fed_epithor_filename")
        df_epithor: pd.DataFrame = Path(data_path / epithor_filename, fs="local").read()
        df_epithor.drop(columns=df_epithor.columns[0:4], inplace=True)
        df_epithor.drop(labels=['Code', 'Suivi'], axis='columns', inplace=True)
        df_dense, _ = utl.drop_sparse_columns(df_epithor, minimum_fill_rate=0.8)
        df_n_lines = len(df_dense.index)
        epithor_nb_feat = len(df_dense.columns)
        epithor_ncomp = 10

        # initialisation
        # centralizer
        centralizer: fd.NMFCentralizer = fd.NMFCentralizer(nfeat=epithor_nb_feat)
        centralizer.set_ncomp(ncomp=epithor_ncomp)
        # clients
        nb_clients: int = 5
        df_slice: int = int(df_n_lines / nb_clients)
        clients = [fd.NMFClient() for _ in range(nb_clients)]
        for icl, client in enumerate(clients):
            client.set_data(df_dense.iloc[int(icl * df_slice): int((icl+1) * df_slice), :])
        # config
        fed_config: fd.FederatedNMFConfig = fd.FederatedNMFConfig(nmfcentral=centralizer,
                                                                  clients=clients)

        fed_config.set_ncomp(epithor_ncomp)
        fed_config.set_nfeat(epithor_nb_feat)
        fed_config.request_update_step(index=0)
        pass