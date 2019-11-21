from django.urls import path

from finances.views import BalanceView

app_name = 'finances'

urlpatterns = [
    path('accountant_diary/', DiaryView.as_view(), name='diary'),
]
