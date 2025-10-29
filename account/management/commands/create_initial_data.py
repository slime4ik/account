from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import Diary

User = get_user_model()

class Command(BaseCommand):
    help = 'Создает начальные данные для приложения'

    def handle(self, *args, **options):
        # Создаем суперпользователя
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Создан суперпользователь admin:admin123'))

        # Создаем тестовые дневники
        diary1, created = Diary.objects.get_or_create(
            title='Мой первый дневник',
            owner=admin_user,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Создан дневник "Мой первый дневник"'))

        diary2, created = Diary.objects.get_or_create(
            title='Рабочие заметки', 
            owner=admin_user,
            defaults={}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Создан дневник "Рабочие заметки"'))

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно созданы!'))