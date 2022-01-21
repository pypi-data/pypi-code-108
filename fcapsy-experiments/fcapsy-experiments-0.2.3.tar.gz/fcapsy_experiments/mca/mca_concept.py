import prince
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import textwrap


class MCAConcept:
    def __init__(
        self,
        concept: "concepts.lattices.Concept",
        n_components=2,
        random_state=42,
        n_iter=100,
        color_by=None,
    ) -> None:
        self._concept = concept
        self.concept_df = self._concept_df()
        self.n_components = n_components
        self._color_by = color_by

        self.mca = prince.MCA(
            n_components=n_components, random_state=random_state, n_iter=n_iter
        )
        self.mca.fit(self.concept_df)

        self.concept_df_transformed = pd.DataFrame(
            self.mca.transform(self.concept_df), index=self._concept.extent
        )

    def _concept_df(self):
        label_domain = self._concept.lattice._context._intents
        vectors = list(
            map(
                lambda x: label_domain.__getitem__(x).bools(),
                self._concept._extent.iter_set(),
            )
        )

        df = pd.DataFrame(
            vectors,
            dtype=int,
            index=self._concept.extent,
            columns=self._concept.lattice._context.properties,
        )

        return df.loc[:, (df != 0).any(axis=0)]

    def to_plotly(self) -> "go.Figure":
        """Generates plotly figure.

        Returns:
            go.Figure: figure
        """

        # need some love
        data = self.concept_df_transformed.copy()

        hover_data = {
                "x": False,
                "y": False,
            }

        if self._color_by is not None:
            color_name = self._color_by[0]
            data[color_name] = self._color_by[1]
            hover_data[color_name] = ":.2f"
        else:
            color_name = None
            
        if self.n_components == 3:
            data = data.rename(columns={0: "x", 1: "y", 2: "z"})

            hover_data["z"] = False
            
            fig = px.scatter_3d(
                data,
                x="x",
                y="y",
                z="z",
                hover_name=list(
                    map(
                        lambda txt: "<br>".join(textwrap.wrap(txt, width=50)),
                        self.concept_df_transformed.index,
                    )
                ),
                hover_data=hover_data,
                color=color_name,
                color_continuous_scale="Bluered",
            )
        else:
            data = data.rename(columns={0: "x", 1: "y"})

            fig = px.scatter(
                data,
                x=0,
                y=1,
                hover_name=list(
                    map(
                        lambda txt: "<br>".join(textwrap.wrap(txt, width=50)),
                        self.concept_df_transformed.index,
                    )
                ),
                hover_data=hover_data,
                color=color_name,
                color_continuous_scale="Bluered",
            )

        return fig
