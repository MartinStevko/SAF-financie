from django.shortcuts import render
from django.views.generic import ListView

from accountancy.models import *


class DiaryView(ListView):

    model = Transaction
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_list'] = Transaction.objects.filter(state='public').order_by('-item__date_payed')
        return context
