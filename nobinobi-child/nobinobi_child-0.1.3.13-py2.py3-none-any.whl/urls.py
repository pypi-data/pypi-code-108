# -*- coding: utf-8 -*-

#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import django.contrib.auth.views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from nobinobi_child import views

app_name = 'nobinobi_child'

router = DefaultRouter()
router.register(r'child', views.ChildViewSet, basename="api-child")
router.register(r'absence', views.AbsenceViewSet, basename="api-absence")
urlpatterns = [
                  path('api/', include(router.urls)),
                  path('accounts/login/', views.AuthLoginView.as_view(), name='login_view'),
                  path('accounts/logout/',
                       auth_views.LogoutView.as_view(template_name='nobinobi_child/pages/login/logout.html'),
                       name='logout_view'),
                  path("", views.HomeView.as_view(), name="home"),
                  # child
                  path("admin/child/printhealcard/<uuid:pk>/", view=views.ChildAdminPrintHealCardView.as_view(),
                       name="print_heal_card"),
                  path("child/", include([
                      path("child/", include([
                          path("",
                               view=views.ChildListView.as_view(),
                               name='Child_list'
                               ),
                          path("~create/",
                               view=views.ChildCreateView.as_view(),
                               name='Child_create'
                               ),
                          path("~picture/select/",
                               view=views.ChildPictureSelectView.as_view(),
                               name='child_picture_select'
                               ),
                          path("<uuid:pk>/", include([
                              path("",
                                   view=views.ChildDetailView.as_view(),
                                   name='Child_detail'),
                              path("~delete/",
                                   view=views.ChildDeleteView.as_view(),
                                   name='Child_delete'),
                              path("~update/",
                                   view=views.ChildUpdateView.as_view(),
                                   name='Child_update'),
                              path("~picture/",
                                   view=views.ChildPictureView.as_view(),
                                   name='child_picture'),
                              path("~picture/modal/",
                                   view=views.ChildPictureUpdateView.as_view(),
                                   name='child_picture_modal'),
                          ])
                               ),
                      ])),
                      path("iotd/", include([
                          path("",
                               view=views.InformationOfTheDayListView.as_view(),
                               name='InformationOfTheDay_list'
                               ),
                          path("<int:pk>/", include([
                              path("",
                                   view=views.InformationOfTheDayDetailView.as_view(),
                                   name='InformationOfTheDay_detail'),
                          ])),
                      ])),
                      path("absence/", include([
                          path("",
                               view=views.AbsenceListView.as_view(),
                               name='Absence_list'
                               ),
                          path("~create/",
                               view=views.AbsenceCreateView.as_view(),
                               name='Absence_create'
                               ),
                          path("<int:pk>/", include([
                              path("",
                                   view=views.AbsenceDetailView.as_view(),
                                   name='Absence_detail'),
                              path("~delete/",
                                   view=views.AbsenceDeleteView.as_view(),
                                   name='Absence_delete'),
                              path("~update/",
                                   view=views.AbsenceUpdateView.as_view(),
                                   name='Absence_update'),
                          ])),
                      ])),
                  ])),
                  path("staff/", include([
                      path("",
                           view=views.StaffListView.as_view(),
                           name='Staff_list'
                           ),
                  ])),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
