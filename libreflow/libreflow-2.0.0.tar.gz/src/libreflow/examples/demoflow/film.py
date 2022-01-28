from kabaret import flow

from libreflow import baseflow


class Shot(baseflow.film.Shot):

    rigging = flow.Child(baseflow.departments.Department)
    layout = flow.Child(baseflow.departments.Department)
    animation = flow.Child(baseflow.departments.Department)
    set_design = flow.Child(baseflow.departments.Department)
    compositing = flow.Child(baseflow.departments.Department)


class Episode(flow.Object):

    description = flow.Param("")
    sequences = flow.Child(baseflow.film.Sequences)


class Episodes(baseflow.maputils.ItemMap):

    item_prefix = "e"
    item_padding = 2

    create_episode = flow.Child(baseflow.maputils.CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return Episode


class Season(flow.Object):

    description = flow.Param("")
    episodes = flow.Child(Episodes)


class Seasons(baseflow.maputils.ItemMap):

    item_prefix = "ss"
    item_padding = 2

    create_season = flow.Child(baseflow.maputils.CreateItemAction)

    @classmethod
    def mapped_type(cls):
        return Season
