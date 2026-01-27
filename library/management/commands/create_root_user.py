from django.core.management.base import BaseCommand
from library.models import User


class Command(BaseCommand):
    help = 'Creates the root user (zero) if it does not exist.'

    def handle(self, *args, **options):
        if not User.objects.filter(username='zero').exists():
            User.objects.create_superuser(
                username='zero',
                email='',
                password='975312468qq',
                full_name='Root (Zero)',
                user_type='ROOT',
            )
            self.stdout.write(self.style.SUCCESS("Root user 'zero' created successfully."))
        else:
            self.stdout.write("Root user 'zero' already exists.")
