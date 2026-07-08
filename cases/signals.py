from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Case, CaseAuditLog


@receiver(post_save, sender=Case)
def notify_on_case_change(sender, instance, created, **kwargs):
    """Send email notifications on case assignment and status changes."""
    if created:
        return

    # Check what changed by looking at the latest audit log
    latest_log = instance.audit_logs.order_by('-timestamp').first()
    if not latest_log:
        return

    action = latest_log.action.lower()
    subject = f'TechDesk Reporter - {instance.title}'

    # Notify technician when assigned
    if 'assigned to' in action and instance.technician:
        send_mail(
            subject=f'You have been assigned to: {instance.title}',
            message=(
                f'Hello {instance.technician.get_full_name()},\n\n'
                f'You have been assigned to case #{instance.id}.\n\n'
                f'Title: {instance.title}\n'
                f'Description: {instance.description[:200]}\n'
                f'Priority: {instance.get_case_priority_display()}\n\n'
                f'Please log in to view the case and start working on it.\n\n'
                f'- TechDesk Reporter'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.technician.email],
            fail_silently=True,
        )

    # Notify reporter when case status changes
    if instance.created_by and instance.created_by.email:
        status_messages = {
            'in_progress': 'Your case is now being worked on.',
            'waiting_report': 'The technician has stopped working on your case.',
            'pending_review': 'A report has been submitted for your case.',
            'closed': 'Your case has been resolved.',
        }
        for key, message in status_messages.items():
            if key in action:
                send_mail(
                    subject=f'Case Update: {instance.title}',
                    message=(
                        f'Hello {instance.created_by.get_full_name()},\n\n'
                        f'{message}\n\n'
                        f'Case #{instance.id}: {instance.title}\n'
                        f'Status: {instance.get_status_display()}\n\n'
                        f'- TechDesk Reporter'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.created_by.email],
                    fail_silently=True,
                )
                break

    # Notify reporter when case is closed
    if 'closed' in action and instance.created_by and instance.created_by.email:
        send_mail(
            subject=f'Case Resolved: {instance.title}',
            message=(
                f'Hello {instance.created_by.get_full_name()},\n\n'
                f'Your case has been resolved!\n\n'
                f'Case #{instance.id}: {instance.title}\n\n'
                f'Thank you for using TechDesk Reporter.\n\n'
                f'- TechDesk Reporter'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.created_by.email],
            fail_silently=True,
        )
