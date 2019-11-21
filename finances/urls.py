from django.urls import path

from finances.views import BalanceView

app_name = 'finances'

urlpatterns = [
    path('balance/', BalanceView.as_view(), name='balance'),
]
