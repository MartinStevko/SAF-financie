from django.contrib import admin

from .models import *


class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    list_per_page = 100
    list_filter = ('section',)

    search_fields = ['name',]
    ordering = ('-pk',)

    fieldsets = (
        ('Transakčný typ', {
            'classes': ('wide',),
            'fields': ('name', 'section', 'ammount'),
        }),
    )


class ExtraExpenseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'section', 'state', 'purpose')
    list_per_page = 100
    list_filter = ('section', 'state')

    search_fields = ['transaction_type', 'purpose']
    ordering = ('-pk',)

    fieldsets = (
        ('Zaradenie', {
            'classes': ('wide',),
            'fields': ('section', 'state'),
        }),
        ('Extra výdavok', {
            'classes': ('wide',),
            'fields': ('transaction_type', 'ammount', 'purpose'),
        }),
    )


admin.site.register(TransactionType, TransactionTypeAdmin)
admin.site.register(ExtraExpense, ExtraExpenseAdmin)
