from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm,UserEditForm,ProfileEditForm,BankForm
from .models import Profile,Bank
from .api.exchangerate import get_exchange_rate
import requests
from .api.tokens import get_tokens, get_account_consent
from datetime import timedelta
from django.utils import timezone
from django.db import IntegrityError,transaction
from .tasks import autorize_bank

@login_required
def dashboard(request):
    price_now = 1#get_exchange_rate
    banks = Bank.objects.filter(user=request.user)


    return render(request,'payment/dashboard.html',{'section': 'dashboard','price_now':price_now,'banks':banks})

# views.py
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()  # Форма сама создаёт профиль
            #login(request, new_user)
            return render(request, 'payment/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'payment/register.html', {'form': user_form})



@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile,
                                    data=request.POST,
                                    files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, 'Profile updated '\
                                      'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
                                    instance=request.user.profile)
    return render(request,
                  'payment/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

# @login_required
# def edit_profile(request):
#     user_profile = request.user  # Текущий пользователь (экземпляр Profile)
#     if request.method == "POST":
#         form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully') 
#         else:
#             messages.error(request,'Ошибка при обновлении профиля')
#     else:
#         form = EditProfileForm(instance=user_profile)
#     return render(request, "payment/edit.html", {"form": form})

# def register_view(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)  # Автоматический вход после регистрации
#             return redirect("dashboard")  # Замените на нужный URL
#     else:
#         form = RegisterForm()
#     return render(request, "payment/register.html", {"form": form})

@login_required
def profile(request):
    user_profile = request.user.profile  # Получаем профиль текущего пользователя
    return render(request, "payment/profile.html", {"user_profile": user_profile,'section': 'profile'})



@login_required
def bank_list(request):
    """Отображает список всех банков текущего пользователя"""
    banks = Bank.objects.filter(user=request.user).order_by('-created_at')
    shold_update = False    
    for bank in banks:        
        if  bank.updated_at < (timezone.now() - timedelta(days=1)):
            shold_update = True           
            break    
        if shold_update:        
            pass
    
    return render(request, 'banks/bank_list.html', {'banks': banks, 'section':'bank'})

# Функциональное представление для добавления банка
@login_required
@transaction.atomic
def bank_create(request):
    """Создает новый банк для текущего пользователя"""

    used_banks_count = Bank.objects.filter(user=request.user).count()
    total_banks = len(Bank.BankNames.choices)
    
    if used_banks_count >= total_banks:
        messages.warning(request, 'Вы уже подключили все доступные банки!')
        return redirect('bank_list')
    if request.method == 'POST':
        form = BankForm(request.POST)
        try:
            bank = form.save(commit=False)
            bank.user = request.user
            bank.save()
            messages.success(request, f'Банк {bank.get_bank_name_display()} успешно добавлен!')
            autorize_bank.delay_on_commit(bank.pk)
            return redirect('bank_list')
        except IntegrityError:
            messages.error(request, 'Этот банк уже добавлен в вашем аккаунте!')
    else:
        form = BankForm()
    return render(request, 'banks/bank_form.html', {'form': form, 'action': 'Добавить'})

# Функциональное представление для редактирования банка
@login_required
def bank_update(request, pk):
    """Редактирует существующий банк"""
    bank = get_object_or_404(Bank, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            messages.success(request, f'Банк {bank.get_bank_name_display()} успешно обновлен!')
            autorize_bank.delay(bank.pk)
            return redirect('bank_list')
    else:
        form = BankForm(instance=bank)
    return render(request, 'banks/bank_form.html', {'form': form, 'action': 'Редактировать', 'bank': bank})

# Функциональное представление для удаления банка
@login_required
def bank_delete(request, pk):
    """Удаляет банк"""
    bank = get_object_or_404(Bank, pk=pk, user=request.user)
    if request.method == 'POST':
        bank_name = bank.get_bank_name_display()
        bank.delete()
        messages.success(request, f'Банк {bank_name} успешно удален!')
        return redirect('bank_list')
    return render(request, 'banks/bank_confirm_delete.html', {'bank': bank})