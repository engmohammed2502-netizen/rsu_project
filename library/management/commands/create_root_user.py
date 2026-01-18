from django.core.management.base import BaseCommand
from library.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username='zero').exists():
            User.objects.create_superuser(
                username='zero',
                password='975312468qq',
                user_type='root'
            )
            self.stdout.write("Root user 'zero' created successfully.")
