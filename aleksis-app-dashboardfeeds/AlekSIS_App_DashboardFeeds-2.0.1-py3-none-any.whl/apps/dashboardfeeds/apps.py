from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.dashboardfeeds"
    verbose_name = "AlekSIS — Dashboard Feeds (Feeds from external resources as dashboard widgets)"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-DashboardFeeds/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2020], "Dominik George", "dominik.george@teckids.org"),
        ([2020], "Julian Leucker", "leuckeju@katharineum.de"),
    )
