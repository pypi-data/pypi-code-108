from django.conf.urls import url
from django.urls import path

from buybackprogram.views import calculate, common, programs, special_taxes, stats

app_name = "buybackprogram"

urlpatterns = [
    path("", common.index, name="index"),
    path("faq", common.faq, name="faq"),
    path("setup", programs.setup, name="setup"),
    path("program_add", programs.program_add, name="program_add"),
    path("location_add", programs.location_add, name="location_add"),
    path("user_settings_edit", common.user_settings_edit, name="user_settings_edit"),
    url(
        r"^location(?P<location_pk>[0-9]+)/remove$",
        programs.location_remove,
        name="location_remove",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/special_taxes$",
        special_taxes.program_special_taxes,
        name="program_special_taxes",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit_item$",
        special_taxes.program_edit_item,
        name="program_edit_item",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit_marketgroup$",
        special_taxes.program_edit_marketgroup,
        name="program_edit_marketgroup",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit",
        programs.program_edit,
        name="program_edit",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/remove$",
        programs.program_remove,
        name="program_remove",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/program_item/(?P<item_pk>[0-9]+)/remove$",
        special_taxes.program_item_remove,
        name="program_item_remove",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/remove_all$",
        special_taxes.program_item_remove_all,
        name="program_item_remove_all",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/calculate$",
        calculate.program_calculate,
        name="program_calculate",
    ),
    path("my_stats", stats.my_stats, name="my_stats"),
    path(
        "tracking/<str:contract_title>/",
        stats.contract_details,
        name="contract_details",
    ),
    path("program_stats", stats.program_stats, name="program_stats"),
    path("program_stats_all", stats.program_stats_all, name="program_stats_all"),
    url(
        r"^item_autocomplete/$",
        common.item_autocomplete,
        name="item_autocomplete",
    ),
    url(
        r"^solarsystem_autocomplete/$",
        common.solarsystem_autocomplete,
        name="solarsystem_autocomplete",
    ),
    url(
        r"^marketgroup_autocomplete/$",
        common.marketgroup_autocomplete,
        name="marketgroup_autocomplete",
    ),
]
