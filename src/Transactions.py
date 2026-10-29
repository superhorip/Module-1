from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank



class Transaction():
    CURRENCIES = ('RUB', 'USD', 'EUR', 'KZT', 'CNY')
    '''
    Stores information bout single operation
    - 🆔 ID, тип, сумма, валюта, комиссия
    - 👤 отправитель, получатель
    - 📊 статус, причина отказа
    - ⏰ timestamps
    - 💸 комиссия за внешние переводы между разными людьми
    First inisiate Transaction by type the get it data via get_transaction_data()
    '''
    def __init__(self):

        self._sender_id: str
        self._recipient_id: str
        self._currency: str
        self._sender_acc_id: str
        self._recipient_acc_id: str
        self._amount: float
        self._bank_fee: float
        self._status: str
        self._transaction_type: str
        self._id = uuid4()


    def get_transaction_data(self):
          transation_data = {'Sender': self.sender_id,
                  'Recipient': self.recipient_id,
                  'Currency' : self.currency,
                  'Sender_acc_id': self.sender_acc_id,
                  'Recipient_acc_id' : self.recipient_acc_id,
                  'Amount' : self.amount,
                  'Bank_fee' : self.bank_fee,
                  'Transaction_type': self._transaction_type}


    def send_money_to_other_user(self, sender_id: str, recipient_id: str, currency: str, 
                sender_acc_id: str, recipient_acc_id: str, amount: float, bank_fee: float = None | None)-> None:
        BA.validate_string(string=sender_id, field_name='Sender ID')
        BA.validate_string(string=recipient_id, field_name='Recipient ID')
        BA.validate_string(string=currency, field_name='Currency')
        BA.validate_string(string=sender_acc_id, field_name='Sender account ID')
        BA.validate_string(string=recipient_acc_id, field_name='Recipeint account ID')
        BA.validate_amount(amount=amount)
        BA.validate_amount(amount=bank_fee)
        if sender_id not in self._all_clients.keys():
                    raise BA.InvalidOperationError('No clients with such client ID exist')
        if recipient_id not in self._all_clients.keys():
                    raise BA.InvalidOperationError('No clients with such client ID exist')
        if sender_acc_id not in self._all_clients[sender_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')
        if recipient_acc_id not in self._all_clients[recipient_acc_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')
        if currency not in self.CURRENCIES:
                raise BA.InvalidOperationError('Wrong currency')
        
        self._sender_id = sender_id
        self._recipient_id = recipient_id
        self._currency = currency
        self._sender_acc_id = sender_acc_id
        self._recipient_acc_id = recipient_acc_id
        self._amount = amount
        self._bank_fee = bank_fee
        self._transaction_type = 'from_user_to_user'
        # self._status: str  пока не понял оно нужно или нет
        
    def deposit(self, sender_id: str, recipient_id: str, currency: str, 
                sender_acc_id: str, recipient_acc_id: str, amount: float, bank_fee: float = None | None)
    
    
                     



    
    
    
    
    
    
    pass


class TransactionQueue():
    '''
    Queue control 
    adds transaction 
    gets next tranzaction
    cancels transaction
    priority
    - ➕ добавление
    - ⭐ приоритет
    - ⏳ отложенные операции
    - ❌ отмена
    '''

class TransactionProcessor():
    '''
    - 💰 комиссии
    - 💱 конвертация
    - 🔄 повторные попытки
    - 📝 фиксация ошибок
    - transfer() with fee

    Последовательность:
1. Получить транзакцию и найти необходимые объекты счетов.
2. Проверить, что операция допустима: счета существуют, не закрыты и не заморожены, клиент не заблокирован, время разрешено.
3. Рассчитать комиссию, если операция является внешним переводом.
4. Если валюты счетов различаются — рассчитать конвертацию.
5. Проверить доступный остаток с учётом комиссии. Для PremiumAccount разрешить овердрафт в пределах установленного лимита.
6. Изменить балансы и установить completed. При отказе записать failed и причину.
    '''

