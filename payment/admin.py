# from django.contrib import admin
# from .models import Profile


# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ['user', 'date_of_birth', 'photo']
   
# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile,Bank

class ProfileAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке профилей
    list_display = (
        "user",
        "user_first_name",
        "user_last_name",
        "user_email",
        "date_of_birth",
        "phone_number",
        "photo",
    )

    # Добавляем поля в форму редактирования профиля
    readonly_fields = ("user_first_name", "user_last_name", "user_email")

    # Методы для получения данных пользователя
    def user_first_name(self, obj):
        return obj.user.first_name

    user_first_name.short_description = "Имя"

    def user_last_name(self, obj):
        return obj.user.last_name

    user_last_name.short_description = "Фамилия"

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = "Email"

# Регистрируем модель в админке
admin.site.register(Profile, ProfileAdmin)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','updated_at' )
    list_display = ['user', 'bank_name']

