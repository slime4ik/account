from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    def soft_delete(self):
        """Мягкое удаление пользователя"""
        self.is_active = False
        self.save()

        return self

    def is_deleted(self):
        """Проверка, удален ли пользователь"""
        return not self.is_active

    def __str__(self) -> str:
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=["is_active", "id"]),
        ]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Diary(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diaries")
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.owner.username}"
    
    class Meta:
        indexes = [
            models.Index(fields=["id"]),
        ]
        verbose_name = "Дневник"
        verbose_name_plural = "Дневники"
        ordering = ['-created_at']