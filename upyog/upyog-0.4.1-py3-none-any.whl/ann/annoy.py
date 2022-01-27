from imp import reload
from upyog.imports import *
from annoy import AnnoyIndex
from rich import print

__all__ = ["AnnoySimilarityMetrics", "AnnoyIndexer", "AnnoyDataFrameIndexer"]


class AnnoySimilarityMetrics(Enum):
    Angular = "angular"
    Euclidean = "euclidean"
    Manhattan = "manhattan"
    Hamming = "hamming"
    Dot = "dot"


class AnnoyIndexer:
    """
    Wrapper for Spotify's Annoy
    See https://github.com/spotify/annoy for more details

    Selected Args:
        * `path`: If given, builds the index on disk to this path, and adds
                          the suffix ".ann" to it
    """

    def __init__(
        self,
        dimension: int,
        n_trees: int = 10,
        search_k: int = -1,
        metric: AnnoySimilarityMetrics = AnnoySimilarityMetrics.Euclidean,
        path: PathLike = None,
    ):
        if not isinstance(metric, AnnoySimilarityMetrics):
            raise TypeError(
                f"Metric must be of type {AnnoySimilarityMetrics}, got {type(metric)} instead"
            )

        self.n_trees = n_trees
        self.search_k = search_k
        self.metric = metric.value
        self.dimension = dimension
        self.path = path
        self.indexer = AnnoyIndex(self.dimension, self.metric)

    def build_from_indexed_dataframe(self, df: pd.DataFrame, colname: str):
        "Builds an index from a DataFrame with vectors stored in `colname`"
        start = time.time()

        for (index, vector) in df[[colname]].itertuples(index=True):
            self.indexer.add_item(index, vector)
        self.indexer.build(self.n_trees, n_jobs=-1)

        end = time.time()
        print(f"Took {round(end-start, 2)} seconds to build index")

    def save(self):
        assert self.path
        self.indexer.save(str(self.path))
        print(f"Saved index to {self.path}")

    def load_from_disk(self, mmap: bool = True):
        self.indexer.load(str(self.path), prefault=False if mmap else True)
        print(
            f"Loaded index from disk with {self.indexer.get_n_items()} items ",
            f"and {self.indexer.get_n_trees()} trees",
        )

    def search(self, index: int, num_items: int = 100):
        return self.indexer.get_nns_by_item(index, num_items)

    # def __repr__(self):
    #     return f"AnnoyIndex with {self.indexer.get_n_items()} items and {self.indexer.get_n_trees()} trees"


class AnnoyDataFrameIndexer(AnnoyIndexer):
    def __init__(
        self,
        df: pd.DataFrame,
        vector_column: str,
        index_column: str,
        path: PathLike,
        search_k: int = -1,
        n_trees: int = 10,
        metric: AnnoySimilarityMetrics = AnnoySimilarityMetrics.Euclidean,
    ):
        """Spotify's Annoy Indexer that can be used with a DataFrame

        Parameters
        ----------

        df : pd.DataFrame
        vector_column : str
            name of the column containing arrays to build the index from
        index_column : str
            name of the column that you will be running queries from. Typically
            a filename column. You will be able to search for nearest neighbors
            using `indexer[name]`
        path : PathLike, optional
            Path to save the index to, by default None
        search_k : int, optional
            , by default -1
        n_trees : int, optional
            num. trees for the indexer, by default 10
        metric : AnnoySimilarityMetrics, optional
            Metric to build the index on, by default AnnoySimilarityMetrics.Euclidean"""

        vector = df[vector_column].iloc[0]
        assert isinstance(vector, np.ndarray)

        self.path = path
        self.index = df[index_column]
        self.df = df.reset_index(drop=True)

        super().__init__(len(vector), n_trees, search_k, metric, path)

        if Path(self.path).exists():
            self.load_from_disk()
        else:
            self.build_from_indexed_dataframe(self.df, vector_column)
            self.save()

        # Now, df has a column 'index' which has the annoy `indexer`'s indexes
        self.df = self.df.reset_index(drop=False)
        self.df = self.df.set_index(index_column)

    def search(self, index: str, num_items: int = 100):
        index = self.df.loc[index, "index"]
        idxs: List[int] = super().search(index, num_items)

        return self.df.iloc[idxs]

    def __getitem__(self, index):
        return self.search(index)
