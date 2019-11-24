from django.contrib import admin
from django_reverse_admin import ReverseModelAdmin

from finances.models import Account, TransactionType
from .models import *


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'section', 'ammount', 'atype', 'description')
    list_per_page = 100
    list_filter = ['section', 'atype', 'state']

    search_fields = ['ammount', 'description']
    ordering = ('-date_created',)

    date_hierarchy = 'date_created'

    fieldsets = (
        ('Transakcia', {
            'classes': ('wide',),
            'fields': (('ammount', 'atype'),),
        }),
        ('Zaradenie', {
            'classes': ('wide',),
            'fields': ('section', 'description'),
        }),
        ('Faktúra', {
            'classes': ('wide',),
            'fields': ('invoice',),
        }),
    )

    actions = [
        'send_reminder',
        'request_approval',
    ]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super(TransactionAdmin, self).save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if 'state__exact' not in request.GET:
            q = request.GET.copy()
            q['state__exact'] = 'created'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(TransactionAdmin, self).changelist_view(request, extra_context=extra_context)

    def request_approval(self, request, queryset):
        for q in queryset:
            if Approval.objects.filter(transaction=q):
                q.approval.send_reminder()
            else:
                a = Approval.objects.create(
                    transaction=q,
                )
                q.approval = a
                q.save()
                a.send_reminder()

    def send_reminder(self, request, queryset):
        self.request_approval(request, queryset)

    send_reminder.short_description = 'Pošli upomienku'
    request_approval.short_description = 'Požiadať o schválenie'


class ApprovalAdmin(ReverseModelAdmin):
    list_display = (
        'get_id',
        'get_section',
        'transaction_type',
        'get_ammount',
        'get_atype',
    )
    list_per_page = 100
    list_filter = [
        'transaction__section',
        'transaction__atype',
        'transaction__state',
    ]

    search_fields = ['transaction__ammount', 'transaction__description']
    ordering = ('-transaction__date_created',)

    autocomplete_fields = ['transaction_type']

    fieldsets = (
        ('Zaradenie', {
            'classes': ('wide',),
            'fields': ('transaction_type',),
        }),
    )

    inline_type = 'stacked'
    inline_reverse = [('transaction', {'fields': [
        ('created_by', 'section'),
        ('ammount', 'atype'),
        'description',
        'invoice',
    ]}),]

    actions = [
        'send_reminder',
        'approve',
        'disapprove',
    ]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(ApprovalAdmin, self).save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if 'transaction__state__exact' not in request.GET:
            q = request.GET.copy()
            q['transaction__state__exact'] = 'created'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(ApprovalAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_id(self, obj):
        return str(obj.transaction)

    get_id.admin_order_field = 'transaction'
    get_id.short_description = 'ID'

    def get_section(self, obj):
        if obj.transaction:
            return obj.transaction.section
        else:
            return str(None)

    get_section.short_description = 'Sekcia'

    def get_ammount(self, obj):
        if obj.transaction:
            return obj.transaction.ammount
        else:
            return str(None)

    get_ammount.admin_order_field = 'transaction__ammount'
    get_ammount.short_description = 'Suma'

    def get_atype(self, obj):
        if obj.transaction:
            if obj.transaction.atype == 'income':
                return 'príjem'
            else:
                return 'výdaj'
        else:
            return str(None)

    get_atype.short_description = 'Typ'

    def send_reminder(self, request, queryset):
        for q in queryset:
            q.item.send_reminder()

    send_reminder.short_description = 'Pošli upomienku žiadosti'

    def approve(self, request, queryset):
        for q in queryset:
            t = q.transaction
            t.approve()

    approve.short_description = 'Schváliť a požiadať o prevod'

    def disapprove(self, request, queryset):
        for q in queryset:
            t = q.transaction
            t.disapprove('finančným manažérom sekcie')

    disapprove.short_description = 'Zamietnuť transakciu'


class ItemAdmin(ReverseModelAdmin):
    list_display = (
        'get_id',
        'get_section',
        'get_transaction_type',
        'get_ammount',
        'get_atype',
    )
    list_per_page = 100
    list_filter = [
        'account',
        'transaction__section',
        'transaction__atype',
        'transaction__state',
        'approval__transaction_type',
    ]

    search_fields = [
        'transaction__ammount',
        'transaction__description',
    ]
    ordering = ('-date_payed',)

    date_hierarchy = 'date_payed'

    fieldsets = (
        ('Platba', {
            'classes': ('wide',),
            'fields': ('account', 'date_payed'),
        }),
    )

    inline_type = 'stacked'
    inline_reverse = [('approval', {'fields': [
        ('created_by', 'transaction_type',),
    ]}), ('transaction', {'fields': [
        ('created_by', 'section'),
        ('ammount', 'atype'),
        'description',
        'invoice',
    ]}),]

    actions = [
        'make_public',
        'make_privat',
        'pay',
        'disapprove',
    ]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(ItemAdmin, self).save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if 'transaction__state__exact' not in request.GET:
            q = request.GET.copy()
            q['transaction__state__exact'] = 'approved'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(ItemAdmin, self).changelist_view(request, extra_context=extra_context)

    def get_id(self, obj):
        return str(obj.approval.transaction)

    get_id.admin_order_field = 'transaction'
    get_id.short_description = 'ID'

    def get_section(self, obj):
        return obj.approval.transaction.section

    get_section.short_description = 'Sekcia'

    def get_transaction_type(self, obj):
        return obj.approval.transaction_type

    get_transaction_type.short_description = 'Druh'

    def get_ammount(self, obj):
        return obj.approval.transaction.ammount

    get_ammount.admin_order_field = 'transaction__ammount'
    get_ammount.short_description = 'Suma'

    def get_atype(self, obj):
        if obj.approval.transaction.atype == 'income':
            return 'príjem'
        else:
            return 'výdaj'

    get_atype.short_description = 'Typ'

    def make_privat(self, request, queryset):
        for q in queryset:
            q.transaction.state = 'payed'
            q.transaction.save()

    make_privat.short_description = 'Urob súkromným'

    def make_public(self, request, queryset):
        for q in queryset:
            q.transaction.state = 'public'
            q.transaction.save()

    make_public.short_description = 'Urob verejným'

    def disapprove(self, request, queryset):
        for q in queryset:
            t = q.transaction
            t.disapprove('finančným manažérom SAF')

    disapprove.short_description = 'Zamietnuť transakciu'

    def pay(self, request, queryset):
        for q in queryset:
            t = q.transaction
            t.pay()

    pay.short_description = 'Zaplatiť transakciu'


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Approval, ApprovalAdmin)
admin.site.register(Item, ItemAdmin)
