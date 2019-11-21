from django.db import models
from django.conf import settings

SECTIONS = settings.SECTIONS

STATES = (
    ('allocated', 'alokované'),
    ('borrowed', 'požičané'),
    ('stored', 'odložené'),
    ('payed', 'zaplatené'),
    ('archived', 'archivované'),
)


class Account(models.Model):
    name = models.CharField(
        max_length=63,
        verbose_name='meno'
    )
    iban = models.CharField(
        max_length=31,
    )
    balance = models.DecimalField(
        verbose_name='zostatok',
        max_digits=8,
        decimal_places=2,
    )

    class Meta:
        verbose_name = 'účet'
        verbose_name_plural = 'účty'

    def __str__(self):
        return '{}'.format(self.name)


class TransactionType(models.Model):
    section = models.CharField(
        max_length=15,
        choices=SECTIONS,
        verbose_name='sekcia',
    )
    name = models.CharField(
        max_length=63,
        verbose_name='meno'
    )

    class Meta:
        verbose_name = 'transakčný typ'
        verbose_name_plural = 'transakčné typy'

    def __str__(self):
        return '{}'.format(self.name)


class ExtraExpense(models.Model):
    ammount = models.DecimalField(
        verbose_name='suma',
        max_digits=8,
        decimal_places=2,
    )
    state = models.CharField(
        max_length=15,
        choices=STATES,
        verbose_name='stav',
    )

    section = models.CharField(
        max_length=15,
        choices=SECTIONS,
        verbose_name='sekcia',
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete='models.PROTECT',
        verbose_name='zaradenie',
    )
    purpose = models.TextField(
        verbose_name='účel',
    )

    class Meta:
        verbose_name = 'extra výdavok'
        verbose_name_plural = 'extra výdavky'

    def __str__(self):
        return '{} - {}'.format(self.transaction_type, self.ammount)
