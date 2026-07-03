from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from cases.models import Case # This ensures the Case model is available

class Command(BaseCommand):
    help = 'Setup user groups and permissions'

    def handle(self, *args, **kwargs):
        # Define the roles
        groups = ['Admin', 'Technician', 'Analyst', 'User']
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(f'Group {group_name} already exists.')
        
        self.stdout.write(self.style.SUCCESS('Successfully initialized all user groups.'))