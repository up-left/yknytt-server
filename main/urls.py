from django.urls import path, re_path, include
from . import views


urlpatterns = [
    path(r'levels/', views.LevelList.as_view(), name='levels'),
    path(r'rate/', views.rate, name='rate'),
    path(r'rating/', views.RatingRetrieve.as_view(), name='rating'),

    re_path(r"^admin/mcadmin/", include("mcadmin.urls")),
]
