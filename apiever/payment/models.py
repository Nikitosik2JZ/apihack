
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20,verbose_name='Номер телефона')
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True,null=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'



# class Profile(AbstractUser):
#     bio = models.TextField(blank=True)
#     avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True)

#     def __str__(self):
#         return self.username

class Bank(models.Model):
    class BankNames(models.TextChoices):
        ALFA = "ALFA", "ALFA"
        VTB = "VTB", "VTB"
        SBER = "SBER", "SBER"
    class ThreeStatus(models.TextChoices):
        """Статусы подтверждения доступа к счетам"""
        NONE = "NONE", "Нет"
        PENDING = "PENDING", "Ожидает подтверждения"
        ACTIVE = "ACTIVE", "Работает"
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,   related_name="banks",  verbose_name="Пользователь")   
    bank_name = models.CharField(max_length=20, choices=BankNames.choices,    verbose_name="Банк")
    team = models.CharField(max_length=255, verbose_name="Team")
    team_login = models.CharField(max_length=255, verbose_name="Логин")
    team_password = models.CharField(max_length=255, verbose_name="Пароль")
      
    bank_token = models.CharField(    max_length=255,    blank=True,    null=True,    verbose_name="Токен банка",)
    bank_token_status = models.BooleanField(default=False , verbose_name="Статус токена" )

    account_consents = models.CharField(    max_length=255,    blank=True,    null=True,    verbose_name="Разрешения по счёту",)
    account_consents_status = models.CharField( max_length=10,choices=ThreeStatus.choices,default=ThreeStatus.NONE,verbose_name="Статус разрешения на доступ" )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        unique_together = ("user", "bank_name")
        verbose_name = "Банк пользователя"
        verbose_name_plural = "Банки пользователя"

    def __str__(self):
        return f"{self.user} - {self.bank_name}"
