from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class VerificationEmail:
    html_email_template_name = 'email_templates/verification_email.html'

    def __init__(self, context):
        self.context = context

    def send(self, to):
        subject = 'Verify your COT-N account'
        html_message = render_to_string(self.html_email_template_name, self.context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            to,
            html_message=html_message,
            fail_silently=False,
        )
