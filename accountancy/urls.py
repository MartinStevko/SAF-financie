from django.urls import path

from .views import DiaryView

app_name = 'accountancy'

urlpatterns = [
    path('accountant_diary/', DiaryView.as_view(), name='diary'),
]
