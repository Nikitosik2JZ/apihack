from django import forms
from .models import Profile,Bank
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль')
    password2 = forms.CharField(label='Повтор пароля')
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(label='Номер телефона',required=True)
    
    def get_number(self):
        if self.is_valid():
            return self.cleaned_data['phone_number']
        else:
            return None
                                

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
        

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data
    
    def clean_phone_number(self):
        
        phone = self.cleaned_data['phone_number']
        if not re.match(r'^\+?[0-9]{7,15}$', phone):
            raise forms.ValidationError("Введите корректный номер телефона")
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Создаём профиль с номером телефона
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number']
            )
            
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id)\
                         .filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number','date_of_birth']
        


'''class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
   
    phone_number = forms.CharField(label='номер')

    
    class Meta:
        model = Profile
        fields = ["username","first_name","email","password1","password2" ]
    def clean_email(self):
        data = self.cleaned_data['email']
        if Profile.objects.filter(email=data).exists():
            raise forms.ValidationError('Почта используется кемто.')
        return data
    def get_number(self):
        return self.cleaned_data['phone_number']'''


'''class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name","last_name", "email", "bio", ]  # Поля, которые можно редактировать

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = Profile.objects.exclude(id=self.instance.id)\
        .filter(email=data)
        if qs.exists():
            raise forms.ValidationError(' Почта уже .')
        return data'''


# class BankInitForm(forms.Form):
    # team = forms.CharField(label="Team", max_length=255)
    # team_login = forms.CharField(label="Логин", max_length=255)
    # team_password = forms.CharField(max_length=255,label="Пароль")

class BankForm(forms.ModelForm):
    """Форма для создания и редактирования банковских данных"""
    
    team_password = forms.CharField(

        label='Пароль',
        
    )
    
    class Meta:
        model = Bank
        fields = ['bank_name', 'team', 'team_login', 'team_password']
        widgets = {
            'bank_name': forms.Select(attrs={
                'class': 'form-control'
            }),
            'team': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название команды'
            }),
            'team_login': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Логин для доступа к API'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        bank_name = cleaned_data.get('bank_name')
        team_login = cleaned_data.get('team_login')
        
        # Проверка на уникальность банка для пользователя
        if self.instance.pk is None:  # Только при создании
            user = self.instance.user if hasattr(self.instance, 'user') else None
            if user and Bank.objects.filter(user=user, bank_name=bank_name).exists():
                raise forms.ValidationError(f'У вас уже подключен банк {bank_name}')
        
        return cleaned_data
