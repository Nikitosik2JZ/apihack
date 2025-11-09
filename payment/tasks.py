from celery import shared_task
from django.http import HttpResponse
from .models import Bank
from .api.tokens import get_name_bank, get_account_consent, get_tokens
from .api.exchangerate import get_exchange_rate
import requests

@shared_task
def check_bank_status():
    # Проверяем банки со статусом ОЖИДАНИЕ
    banks = Bank.objects.filter(account_consents_status='PENDING')
    
    for bank in banks:
        # Ваша функция обработки
        process_waiting_bank(bank)
        
def process_waiting_bank(bank):
    
    print(f"Обработка банка {bank.bank_name} со статусом ОЖИДАНИЕ")
    bank_l=get_name_bank(bank)
    headers = {'accept': 'application/json','x-fapi-interaction-id': 'team200'}
    url = f'https://{bank_l}bank.open.bankingapi.ru/account-consents/{bank.account_consents}'
    response = requests.get(url,headers=headers)
    newdata = response.json()
    if newdata['data']['status'] == 'AwaitingAuthorization':
        return 'PENDING'
    if newdata['data']['status'] == 'Authorized':
        bank.account_consents = newdata['data']['consentId']
        bank.account_consents_status = 'ACTIVE'
        bank.save()
        return 'ACTIVE'

@shared_task
def autorize_bank(bank_id):
    bank = Bank.objects.get(id=bank_id)
    get_tokens(bank)
    get_account_consent(bank)

