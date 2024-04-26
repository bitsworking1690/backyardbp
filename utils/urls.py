from django.urls import path
from utils.views import (
    SystemResetView,
    UserDataResetView
)

urlpatterns = [
    path('system/reset/', SystemResetView.as_view(), name='system-reset'),
    path('user/data/reset/', UserDataResetView.as_view(), name='user-data-reset'),
]
