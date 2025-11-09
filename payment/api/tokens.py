from ..models import Bank
import requests

def get_name_bank(bank):
    if bank.bank_name == 'VTB':
       bank_l = 'v'
    elif bank.bank_name == 'ALFA':
        bank_l = 'a'
    elif bank.bank_name == 'SBER':
        bank_l = 's'
    return bank_l
def get_tokens(bank):
    
    
    #

   
    data = {'client_id': bank.team, 'client_secret': bank.team_password}
    bank_l=get_name_bank(bank)
    url = f'https://{bank_l}bank.open.bankingapi.ru/auth/bank-token'

    response = requests.post(url,params=data)
    if response.status_code == 200:
         
        bank.bank_token = response.json()["access_token"]
        bank.bank_token_status = True
        bank.save()
        return 'TOKEN TRUE'
    else:
        bank.bank_token_status = False
        bank.bank_token = ''
        bank.save()


            
               


def get_account_consent(bank):
    
    data = {
    "client_id": "team058-1",
    "permissions": [
            "ReadAccountsDetail",
            "ReadBalances",
            "ReadTransactionsDetail"
        ],
    "reason": "",
    "requesting_bank": "team_800",
    "requesting_bank_name": "TEAM 800"
    }
    bank_l=get_name_bank(bank)
    headers = {'x-requesting-bank': 'team800'}
    url = f'https://{bank_l}bank.open.bankingapi.ru/account-consents/request'
    if bank_l != 's':

        response = requests.post(url,json=data,headers=headers)
        if response.status_code == 200:
            bank.account_consents = response.json()["consent_id"]
            bank.account_consents_status = 'ACTIVE'
            bank.save()
            return 'CONSENT ACTIVE'
    else:

        response = requests.post(url,json=data,headers=headers)
        newdata=response.json()
        if response.status_code == 200 and newdata["status"] == 'pending':
            bank.account_consents_status = 'PENDING'
            bank.account_consents = newdata["request_id"]
            bank.save()
            return 'CONSENT PENDING'

def get_account_consent_status(bank):
    bank_l=get_name_bank(bank)
    headers = {'accept': 'application/json','x-fapi-interaction-id': 'team2001'}
    url = f'https://{bank_l}bank.open.bankingapi.ru/account-consents/{bank.account_consents}'
    response = requests.get(url,headers=headers)
    newdata = response.json()
    if newdata['data']['status'] == 'AwaitingAuthorization':
        return 'PENDING'
    if newdata['data']['status'] == 'Authorized':
        return 'ACTIVE'

