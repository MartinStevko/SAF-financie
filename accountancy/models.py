from django.db import models
from django.conf import settings

from finances.models import Account, TransactionType
from app.emails import SendMail

SECTIONS = settings.SECTIONS

TYPES = (
    ('income', 'príjem'),
    ('outcome', 'výdaj'),
)

STATES = (
    ('created', 'vytvorené'),
    ('approved', 'schválené'),
    ('disapproved', 'neschválené'),
    ('payed', 'zaplatené a neverejné'),
    ('public', 'zaplatené a verejné'),
)


class Transaction(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Vytovril',
    )
    date_created = models.DateTimeField(
        auto_now=True,
    )
    state = models.CharField(
        max_length=15,
        choices=STATES,
        verbose_name='stav',
        default='created',
    )
    ammount = models.DecimalField(
        verbose_name='suma',
        max_digits=8,
        decimal_places=2,
    )
    atype = models.CharField(
        max_length=7,
        choices=TYPES,
        verbose_name='typ',
    )
    section = models.CharField(
        max_length=15,
        choices=SECTIONS,
        verbose_name='sekcia',
    )
    description = models.TextField(
        verbose_name='popis',
    )
    invoice = models.FileField(
        verbose_name='faktúra',
        upload_to='invoices/%Y/%m/',
    )

    class Meta:
        verbose_name = 'transakcia'
        verbose_name_plural = 'transakcie'

    def __str__(self):
        return 'Transakcia {} - {}'.format(self.pk, self.date_created.date())

    def approve(self):
        self.state = 'approved'
        self.save()

        i = Item.objects.create(
            transaction=self,
            approval=self.approval
        )
        i.send_reminder()

        SendMail(
            [self.created_by.email],
            'Informácia o schválení transakcie '+str(self.pk)
        ).change_state(
            'schválená finančným manažérom sekcie',
            self
        )

    def pay(self):
        self.state = 'public'
        self.save()

        SendMail(
            [self.created_by.email],
            'Informácia o zaplatení transakcie '+str(self.pk)
        ).change_state(
            'zaplatená',
            self
        )

    def disapprove(self, by_who):
        self.state = 'disapproved'
        self.save()

        SendMail(
            [self.created_by.email],
            'Informácia o zamietnutí transakcie '+str(self.pk)
        ).change_state(
            'zamietnutá '+by_who,
            self
        )


class Approval(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Schválil',
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True,
        related_name='approval'
    )
    transaction_type = models.ForeignKey(
        TransactionType,
        on_delete=models.PROTECT,
        verbose_name='druh',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'schválenie'
        verbose_name_plural = 'schválenia'

    def __str__(self):
        return 'Schválenie transakcie {}'.format(self.transaction.pk)

    def send_reminder(self):
        if self.transaction.section == 'ultimate':
            recipient = 'ULT_FM'
        elif self.transaction.section == 'discgolf':
            recipient = 'DG_FM'
        else:
            recipient = 'SAF_FM'

        SendMail(
            recipient,
            'Žiadosť o schválenie prevodu '+str(self.transaction.pk)
        ).send_reminder(
            'schválenie',
            self.transaction
        )


class Item(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Zaplatil'
    )
    approval = models.OneToOneField(
        Approval,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='item'
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='item'
    )
    date_payed = models.DateField(
        verbose_name='dátum zúčtovania',
        blank=True,
        null=True,
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        verbose_name='účet',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'položka'
        verbose_name_plural = 'položky'

    def __str__(self):
        return '{} - {}'.format(
            str(self.date_payed),
            self.approval.transaction.ammount
        )

    def send_reminder(self):
        SendMail(
            'SAF_FM',
            'Žiadosť o vykonanie prevodu '+str(self.transaction.pk)
        ).send_reminder(
            'vykonanie',
            self.transaction
        )
