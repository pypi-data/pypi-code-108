# -*- coding: utf-8 -*-

#      Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.conf.urls import url
from django.urls import path, include, register_converter
from nobinobi_core.functions import FourDigitConverter, TwoDigitConverter
from rest_framework.routers import DefaultRouter

from nobinobi_daily_follow_up import views
from nobinobi_daily_follow_up.utils import IsoDateConverter
from nobinobi_daily_follow_up.views import ClassroomJsonView

app_name = 'nobinobi_daily_follow_up'

register_converter(FourDigitConverter, 'yyyy')
register_converter(TwoDigitConverter, 'mmdd')
register_converter(IsoDateConverter, 'isodate')

router = DefaultRouter()
router.register(r'presence', views.PresenceViewSet, basename="api-presence")
router.register(r'earlytroubleshooting', views.EarlyTroubleshootingViewSet, basename="api-earlytroubleshooting")

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/presence/presence_by_weeks/<isodate:from_date>/<isodate:end_date>/', views.PresenceViewSet.as_view({
        'get': 'presence_by_weeks',
    }), name='api-presence-presence-by-weeks'),
    path('api/presence/presence_by_classroom/<isodate:date>/<int:classroom_id>/', views.PresenceClassroomDateViewSet.as_view({'get': 'list'}), name='api-presence-presence-by-classroom'),
    path('api/presence/presence_by_classroom_kindergarten/<isodate:date>/<int:classroom_id>/', views.PresenceKindergartenClassroomDateViewSet.as_view({'get': 'list'}), name='api-presence-by-classroom-kindergarten'),
    path('api/presence/presence_by_weeks_and_child/<uuid:child_pk>/<isodate:from_date>/<isodate:end_date>/',
         views.PresenceViewSet.as_view({
             'get': 'presence_by_weeks_and_child',
         }), name='api-presence-presence-by-weeks-and-child'),

    path('api/dfu/all_count/', views.dfu_live_all_notification_count, name='dfu_live_all_notification_count'),
    path('api/dfu/all_list/', views.dfu_live_all_notification_list, name='dfu_live_all_notification_list'),
    path('fields/classroom_allowed.json', ClassroomJsonView.as_view(), name="classroom_allowed_json"),

    path("daily-follow-up/", include([
        path("presence/", include([
            path("",
                 view=views.PresenceChoiceView.as_view(),
                 name='Presence_choice'
                 ),
            path("list/", include([
                path("",
                     view=views.PresenceListView.as_view(),
                     name='Presence_list'
                     ),
                path("<int:pk>/",
                     view=views.PresenceDetailListView.as_view(),
                     name='Presence_detail_list'
                     )
            ])),
            path("week-list/", include([
                path("",
                     view=views.PresenceWeekListChoiceView.as_view(),
                     name='presence_week_choice'
                     ),
                path("creche/<int:classroom_id>/",
                     view=views.PresenceWeekListView.as_view(),
                     name='presence_week_list'
                     ),
                path("creche/<int:classroom_id>/<isodate:date>/",
                     view=views.PresenceWeekListView.as_view(),
                     name='presence_week_list'
                     ),
                path("kindergarten/<int:classroom_id>/",
                     view=views.PresenceWeekKinderGartenListView.as_view(),
                     name='presence_week_kindergarten_list'
                     ),
                path("kindergarten/<int:classroom_id>/<isodate:date>/",
                     view=views.PresenceWeekKinderGartenListView.as_view(),
                     name='presence_week_kindergarten_list'
                     )
            ])),
            path("admin-week-list/", include([
                path("",
                     view=views.AdminPresenceWeekListView.as_view(),
                     name='admin_presence_week'
                     ),
            ])),

            path("<int:pk>/", include([
                path("~create/",
                     view=views.PresenceCreateView.as_view(),
                     name='Presence_create'
                     ),
                path("~create/<uuid:child_pk>/",
                     view=views.PresenceCreateView.as_view(),
                     name='Presence_create'
                     ),
                path("~departure/<int:presence_pk>/",
                     view=views.PresenceDepartureView.as_view(),
                     name='Presence_departure'
                     ),
                path("~intermediate-departure/<int:presence_pk>/",
                     view=views.PresenceIntermediateDepartureView.as_view(),
                     name='Presence_intermediate_departure'
                     ),
                #     path("",
                #          view=views.PresenceDetailView.as_view(),
                #          name='Presence_detail'),
                #     path("~delete/",
                #          view=views.PresenceDeleteView.as_view(),
                #          name='Presence_delete'),
                #     path("~update/",
                #          view=views.PresenceUpdateView.as_view(),
                #          name='Presence_update'),
            ])),
        ])),
        path("stroll/", include([
            path("",
                 view=views.StrollChoiceView.as_view(),
                 name='stroll_choice'
                 ),
            path("<int:classroom_id>/pdf",
                 view=views.StrollViewPDF.as_view(),
                 name='stroll_pdf'
                 ),
        ])),
        path("group_activity/", include([
            path("",
                 view=views.GroupActivityChoiceView.as_view(),
                 name='group_activity_choice_view'
                 ),
            path("<int:classroom_id>/",
                 view=views.GroupActivityUpdateView.as_view(),
                 name='group_activity_view'
                 ),
        ])),
        path("group_daily_follow_up/", include([
            path("",
                 view=views.GroupDailyFollowUpChoiceView.as_view(),
                 name='group_daily_follow_up_choice_view'
                 ),
            path("<int:classroom_id>/",
                 view=views.GroupDailyFollowUpUpdateView.as_view(),
                 name='group_daily_follow_up_view'
                 ),
        ])),
        path("reception/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            # path("~create/",
            #      view=views.ReceptionCreateView.as_view(),
            #      name='Reception_create'
            #      ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                # path("~delete/",
                #      view=views.PresenceDeleteView.as_view(),
                #      name='Presence_delete'),
                path("~update/",
                     view=views.ReceptionUpdateView.as_view(),
                     name='Reception_update'),
            ])),
        ])),
        path("meals/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            path("~create/",
                 view=views.MealDailyFollowUpCreateView.as_view(),
                 name='MealDailyFollowUp_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                # path("~delete/",
                #      view=views.PresenceDeleteView.as_view(),
                #      name='Presence_delete'),
                path("~update/",
                     view=views.MealDailyFollowUpUpdateView.as_view(),
                     name='MealDailyFollowUp_update'),
            ])),
        ])),
        path("nap/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            path("~create/<int:daily_follow_up>/",
                 view=views.NapCreateView.as_view(),
                 name='Nap_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.NapDeleteView.as_view(),
                     name='Nap_delete'),
                path("~update/",
                     view=views.NapUpdateView.as_view(),
                     name='Nap_update'),
            ])),
        ])),
        path("diaperchange/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            path("~create/<int:daily_follow_up>/",
                 view=views.DiaperChangeCreateView.as_view(),
                 name='DiaperChange_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.DiaperChangeDeleteView.as_view(),
                     name='DiaperChange_delete'),
                path("~update/",
                     view=views.DiaperChangeUpdateView.as_view(),
                     name='DiaperChange_update'),
            ])),
        ])),
        path("lotion/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            path("~create/<int:daily_follow_up>/",
                 view=views.LotionDailyFollowUpCreateView.as_view(),
                 name='LotionDailyFollowUp_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.LotionDailyFollowUpDeleteView.as_view(),
                     name='LotionDailyFollowUp_delete'),
                path("~update/",
                     view=views.LotionDailyFollowUpUpdateView.as_view(),
                     name='LotionDailyFollowUp_update'),
            ])),
        ])),
        path("activity/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            path("~create/<int:daily_follow_up>/",
                 view=views.ActivityCreateView.as_view(),
                 name='Activity_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.ActivityDeleteView.as_view(),
                     name='Activity_delete'),
                path("~update/",
                     view=views.ActivityUpdateView.as_view(),
                     name='Activity_update'),
            ])),
        ])),
        path("dailyfollowuptomedication/", include([
            path("~create/<int:daily_follow_up>/<int:classroom_id>/",
                 view=views.DailyFollowUpToMedicationCreateView.as_view(),
                 name='DailyFollowUpToMedication_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.DailyFollowUpToMedicationDeleteView.as_view(),
                     name='DailyFollowUpToMedication_delete'),
                path("~update/",
                     view=views.DailyFollowUpToMedicationUpdateView.as_view(),
                     name='DailyFollowUpToMedication_update'),
            ])),
        ])),
        path("medication/", include([
            path("<int:daily_follow_up>/<int:classroom_id>/<uuid:child>/", include([
                path("~create/",
                     view=views.MedicationCreateView.as_view(),
                     name='Medication_create'
                     ),
                path("<int:pk>/", include([
                    # path("",
                    #      view=views.PresenceDetailView.as_view(),
                    #      name='Presence_detail'),
                    path("~delete/",
                         view=views.MedicationDeleteView.as_view(),
                         name='Medication_delete'),
                    path("~update/",
                         view=views.MedicationUpdateView.as_view(),
                         name='Medication_update'),
                ])),
            ])),
            path("multiday/~create/",
                 view=views.MultiDayMedication.as_view(),
                 name='Multiday_Medication'
                 ),
        ])),
        path("give-medication/", include([
            path("~create/<int:medication>/",
                 view=views.GiveMedicationCreateView.as_view(),
                 name='GiveMedication_create'
                 ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                path("~delete/",
                     view=views.GiveMedicationDeleteView.as_view(),
                     name='GiveMedication_delete'),
                path("~update/",
                     view=views.GiveMedicationUpdateView.as_view(),
                     name='GiveMedication_update'),
                path("~delay/",
                     view=views.GiveMedicationDelayView.as_view(),
                     name='GiveMedication_delay'),
            ])),
        ])),
        path("dailyfollowup/", include([
            # path("",
            #      view=views.PresenceChoiceView.as_view(),
            #      name='Presence_choice'
            #      ),
            # path("list/", include([
            #     path("",
            #          view=views.PresenceListView.as_view(),
            #          name='Presence_list'
            #          ),
            #     path("<int:pk>/",
            #          view=views.PresenceDetailListView.as_view(),
            #          name='Presence_detail_list'
            #          )
            # ]))
            # path("~create/<int:daily_follow_up>/",
            #      view=views.MedicationCreateView.as_view(),
            #      name='Medication_create'
            #      ),
            path("<int:pk>/", include([
                # path("",
                #      view=views.PresenceDetailView.as_view(),
                #      name='Presence_detail'),
                # path("~delete/",
                #      view=views.MedicationDeleteView.as_view(),
                #      name='Medication_delete'),
                path("~update/",
                     view=views.DailyFollowUpUpdateView.as_view(),
                     name='DailyFollowUp_update'),
            ])),
        ])),
        path("earlytroubleshooting/", include([
            path("", view=views.EarlyTroubleshootingListView.as_view(), name='EarlyTroubleshooting_list'),
            path("~create/",
                 view=views.EarlyTroubleshootingCreateView.as_view(),
                 name='EarlyTroubleshooting_create'
                 ),
            path("<int:pk>/", include([
                path("",
                     view=views.EarlyTroubleshootingDetailView.as_view(),
                     name='EarlyTroubleshooting_detail'),
                path("~delete/",
                     view=views.EarlyTroubleshootingDeleteView.as_view(),
                     name='EarlyTroubleshooting_delete'),
                path("~update/",
                     view=views.EarlyTroubleshootingUpdateView.as_view(),
                     name='EarlyTroubleshooting_update'),
            ])),
        ])),
        path("child/", view=views.DailyFollowUpChoiceSummaryWeek.as_view(),
             name='DailyFollowUp_summary_week_choice'),
        path("child/<uuid:pk>/date/<isodate:date>/", view=views.DailyFollowUpSummaryWeek.as_view(),
             name='DailyFollowUp_summary_week'),
    ])),
    url(
        regex="^TypeActivity/~create/$",
        view=views.TypeActivityCreateView.as_view(),
        name='TypeActivity_create',
    ),
    url(
        regex="^TypeActivity/(?P<pk>\d+)/~delete/$",
        view=views.TypeActivityDeleteView.as_view(),
        name='TypeActivity_delete',
    ),
    url(
        regex="^TypeActivity/(?P<pk>\d+)/$",
        view=views.TypeActivityDetailView.as_view(),
        name='TypeActivity_detail',
    ),
    url(
        regex="^TypeActivity/(?P<pk>\d+)/~update/$",
        view=views.TypeActivityUpdateView.as_view(),
        name='TypeActivity_update',
    ),
    url(
        regex="^TypeActivity/$",
        view=views.TypeActivityListView.as_view(),
        name='TypeActivity_list',
    ),
    url(
        regex="^ActivityGroup/~create/$",
        view=views.ActivityGroupCreateView.as_view(),
        name='ActivityGroup_create',
    ),
    url(
        regex="^ActivityGroup/(?P<pk>\d+)/~delete/$",
        view=views.ActivityGroupDeleteView.as_view(),
        name='ActivityGroup_delete',
    ),
    url(
        regex="^ActivityGroup/(?P<pk>\d+)/$",
        view=views.ActivityGroupDetailView.as_view(),
        name='ActivityGroup_detail',
    ),
    url(
        regex="^ActivityGroup/(?P<pk>\d+)/~update/$",
        view=views.ActivityGroupUpdateView.as_view(),
        name='ActivityGroup_update',
    ),
    url(
        regex="^ActivityGroup/$",
        view=views.ActivityGroupListView.as_view(),
        name='ActivityGroup_list',
    ),
    url(
        regex="^DailyFollowUp/~create/$",
        view=views.DailyFollowUpCreateView.as_view(),
        name='DailyFollowUp_create',
    ),
    url(
        regex="^DailyFollowUp/(?P<pk>\d+)/~delete/$",
        view=views.DailyFollowUpDeleteView.as_view(),
        name='DailyFollowUp_delete',
    ),
    url(
        regex="^DailyFollowUp/(?P<pk>\d+)/$",
        view=views.DailyFollowUpDetailView.as_view(),
        name='DailyFollowUp_detail',
    ),
    url(
        regex="^DailyFollowUp/(?P<pk>\d+)/~update/$",
        view=views.DailyFollowUpUpdateView.as_view(),
        name='DailyFollowUp_update',
    ),
    url(
        regex="^DailyFollowUp/$",
        view=views.DailyFollowUpListView.as_view(),
        name='DailyFollowUp_list',
    ),
    url(
        regex="^Lotion/~create/$",
        view=views.LotionCreateView.as_view(),
        name='Lotion_create',
    ),
    url(
        regex="^Lotion/(?P<pk>\d+)/~delete/$",
        view=views.LotionDeleteView.as_view(),
        name='Lotion_delete',
    ),
    url(
        regex="^Lotion/(?P<pk>\d+)/$",
        view=views.LotionDetailView.as_view(),
        name='Lotion_detail',
    ),
    url(
        regex="^Lotion/(?P<pk>\d+)/~update/$",
        view=views.LotionUpdateView.as_view(),
        name='Lotion_update',
    ),
    url(
        regex="^Lotion/$",
        view=views.LotionListView.as_view(),
        name='Lotion_list',
    ),
    url(
        regex="^TypeMedication/~create/$",
        view=views.TypeMedicationCreateView.as_view(),
        name='TypeMedication_create',
    ),
    url(
        regex="^TypeMedication/(?P<pk>\d+)/~delete/$",
        view=views.TypeMedicationDeleteView.as_view(),
        name='TypeMedication_delete',
    ),
    url(
        regex="^TypeMedication/(?P<pk>\d+)/$",
        view=views.TypeMedicationDetailView.as_view(),
        name='TypeMedication_detail',
    ),
    url(
        regex="^TypeMedication/(?P<pk>\d+)/~update/$",
        view=views.TypeMedicationUpdateView.as_view(),
        name='TypeMedication_update',
    ),
    url(
        regex="^TypeMedication/$",
        view=views.TypeMedicationListView.as_view(),
        name='TypeMedication_list',
    ),
    url(
        regex="^GiveMedication/~create/$",
        view=views.GiveMedicationCreateView.as_view(),
        name='GiveMedication_create',
    ),
    url(
        regex="^GiveMedication/(?P<pk>\d+)/~delete/$",
        view=views.GiveMedicationDeleteView.as_view(),
        name='GiveMedication_delete',
    ),
    url(
        regex="^GiveMedication/(?P<pk>\d+)/$",
        view=views.GiveMedicationDetailView.as_view(),
        name='GiveMedication_detail',
    ),
    url(
        regex="^GiveMedication/(?P<pk>\d+)/~update/$",
        view=views.GiveMedicationUpdateView.as_view(),
        name='GiveMedication_update',
    ),
    url(
        regex="^GiveMedication/$",
        view=views.GiveMedicationListView.as_view(),
        name='GiveMedication_list',
    ),
    url(
        regex="^Meal/~create/$",
        view=views.MealCreateView.as_view(),
        name='Meal_create',
    ),
    url(
        regex="^Meal/(?P<pk>\d+)/~delete/$",
        view=views.MealDeleteView.as_view(),
        name='Meal_delete',
    ),
    url(
        regex="^Meal/(?P<pk>\d+)/$",
        view=views.MealDetailView.as_view(),
        name='Meal_detail',
    ),
    url(
        regex="^Meal/(?P<pk>\d+)/~update/$",
        view=views.MealUpdateView.as_view(),
        name='Meal_update',
    ),
    url(
        regex="^Meal/$",
        view=views.MealListView.as_view(),
        name='Meal_list',
    ),
]
