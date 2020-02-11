from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.mail import EmailMessage
from django.template.loader import get_template

'''
SendMail(
    ['contact1', 'contact2'],
    'subject'
).method(instance)
'''


class SendMail:

    def __init__(self, recipients, subject):
        if type(recipients) == list:
            self.recipients = recipients
        elif recipients == 'SAF_FM':
            self.recipients = getattr(
                settings,
                'SAF_FM',
                ['safslovakia@gmail.com']
            )
        elif recipients == 'ULT_FM':
            self.recipients = getattr(
                settings,
                'ULT_FM',
                ['safslovakia@gmail.com']
            )
        elif recipients == 'DG_FM':
            self.recipients = getattr(
                settings,
                'DG_FM',
                ['safslovakia@gmail.com']
            )
        elif recipients == 'ACCOUNTANT':
            self.recipients = getattr(
                settings,
                'ACCOUNTANT',
                ['safslovakia@gmail.com']
            )
        else:
            raise SuspiciousOperation('Príjmateľ správy sa nezhoduje!')

        prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', None)
        if prefix:
            self.subject = prefix + subject
        else:
            self.subject = subject

    def send_reminder(self, model, obj):
        plaintext = get_template('emails/reminder.txt')

        context = {
            'model': model,
            't': obj,
        }

        self.send_rendered_email(context, plaintext)

    def change_state(self, model, obj):
        plaintext = get_template('emails/change_state.txt')

        context = {
            'model': model,
            't': obj,
        }

        self.send_rendered_email(context, plaintext)

    def send_invoice(self, context, attachement):
        template = get_template('emails/send_invoice.txt')
        content = template.render(context)

        email = EmailMessage(
            self.subject,
            content,
            getattr(settings, 'FROM_EMAIL_NAME', 'info@szf.sk'),
            self.recipients,
        )
        email.attach_file(attachement) 
        email.send(fail_silently=False)

    def send_rendered_email(self, context, template):
        content = template.render(context)

        email = EmailMessage(
            self.subject,
            content,
            getattr(settings, 'FROM_EMAIL_NAME', 'info@szf.sk'),
            self.recipients,
        )
        email.send(fail_silently=False)
