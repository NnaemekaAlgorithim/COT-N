from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.loans.models import Loan
from apps.notifications.models import Notification
from apps.notifications.services import notify_admins_and_founder, notify_user


class Command(BaseCommand):
    help = 'Sends loan repayment-due-soon and overdue push notifications. Schedule this hourly via cron.'

    def handle(self, *args, **options):
        now = timezone.now()
        due_soon_cutoff = now + timezone.timedelta(days=1)

        due_soon_count = 0
        due_soon_qs = Loan.objects.filter(
            status=Loan.RECEIVED, due_date__gt=now, due_date__lte=due_soon_cutoff, due_reminder_sent_at__isnull=True,
        )
        for loan in due_soon_qs:
            notify_user(
                recipient=loan.borrower,
                title='Loan repayment due soon',
                body=f'Your loan of {loan.amount} in {loan.organization.name} is due on {loan.due_date:%Y-%m-%d %H:%M}.',
                notification_type=Notification.LOAN_REPAYMENT_DUE,
                organization=loan.organization,
                data={'loan_id': loan.id},
            )
            loan.due_reminder_sent_at = now
            loan.save(update_fields=['due_reminder_sent_at'])
            due_soon_count += 1

        overdue_count = 0
        overdue_qs = Loan.objects.filter(status=Loan.RECEIVED, due_date__lt=now, overdue_notified_at__isnull=True)
        for loan in overdue_qs:
            notify_user(
                recipient=loan.borrower,
                title='Loan overdue',
                body=f'Your loan of {loan.amount} in {loan.organization.name} is now overdue.',
                notification_type=Notification.LOAN_OVERDUE,
                organization=loan.organization,
                data={'loan_id': loan.id},
            )
            notify_admins_and_founder(
                organization=loan.organization,
                title='A member loan is overdue',
                body=f'{loan.borrower.email}\'s loan in {loan.organization.name} is overdue.',
                notification_type=Notification.LOAN_OVERDUE,
                data={'loan_id': loan.id},
            )
            loan.overdue_notified_at = now
            loan.save(update_fields=['overdue_notified_at'])
            overdue_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Sent {due_soon_count} due-soon and {overdue_count} overdue loan notifications.'
        ))
