from django.views.generic import ListView
from django.conf import settings

from accountancy.models import *
from finances.models import *

SECTIONS = settings.SECTIONS


class BalanceView(ListView):

    model = TransactionType

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = []
        for section in SECTIONS:
            temp = []
            types = TransactionType.objects.filter(section=section[0])
            for t in types:
                approvals = Approval.objects.filter(transaction_type=t)
                s = 0
                for a in approvals:
                    if a.transaction.state in ['payed', 'public']:
                        s += a.transaction.ammount
                temp.append((t.name, s))
            context['data'].append((section[1], temp))
        return context
