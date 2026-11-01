from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank


class Transaction:
    CURRENCIES = ("RUB", "USD", "EUR", "KZT", "CNY")
    VALID_TRANSACTION_STATUSES = ( "pending",  "processing",  "completed", "failed", "cancelled",  )
    TRANSATION_TYPES = ("transfer", "withdraw", "deposit")
    """
    """

    def __init__(
        self,
        transaction_type: str,
        bank_object: Bank.Bank,
        currency: str,
        amount: float,
        sender_id: str | None = None,
        recipient_id: str | None = None,
        sender_acc_id: str | None = None,
        recipient_acc_id: str | None = None,
        scheduled_at: datetime | None = None
     ) -> None:
        """
        3 types of transaction: transfer, withdraw, deposit
        """
        self._id = str(uuid4())
        self.validate_transaction_data(transaction_type=transaction_type, currency=currency, amount=amount, sender_id=sender_id,
                                      recipient_id=recipient_id)

        self.validate_bank_data(transaction_type=transaction_type, bank_object=bank_object, sender_id=sender_id,
                                recipient_id=recipient_id, sender_acc_id=sender_acc_id,recipient_acc_id=recipient_acc_id)

        if scheduled_at is not None:
                if not isinstance(scheduled_at, datetime):
                    raise BA.InvalidOperationError('Wrong datetime object')
        self._sender_id = sender_id
        self._recipient_id = recipient_id
        self._currency = currency
        self._amount = amount
        self._transaction_type = transaction_type
        self._recipient_acc_id = recipient_acc_id
        self._sender_acc_id = sender_acc_id
        self._status = 'pending'
        self._failure_reason = None
        self._transfer_fee = 0
        self._creation_time = datetime.now()
        self._processing_time = None
        self._scheduled_at = scheduled_at
       

    def validate_transaction_data(
        self,
        transaction_type: str,
        currency: str,
        amount: float,
        sender_id: str | None = None,
        recipient_id: str | None = None,
    ) -> None:
        """
        validates type of transation, sum and a currency and mandatory fields depending of transation type
        sender and recipient for transfer, only sender for withdraw, only  recipent for deposit
        """

        BA.validate_string(string=transaction_type, field_name="Transaction type")
        if transaction_type not in self.TRANSATION_TYPES:
            raise BA.InvalidOperationError("No such transation type")
        BA.validate_string(string=currency, field_name="Currency")
        if currency not in self.CURRENCIES:
            raise BA.InvalidOperationError("Wrong currency type")
        BA.validate_amount(amount=amount)
        if transaction_type == "transfer":
            BA.validate_string(string=sender_id, field_name="Sender ID")
            BA.validate_string(string=recipient_id, field_name="Recipient ID")
        if transaction_type == "withdraw":
            BA.validate_string(string=sender_id, field_name="Sender ID")
        if transaction_type == "deposit":
            BA.validate_string(string=recipient_id, field_name="Recipient ID")


    def validate_bank_data(
        self,
        transaction_type: str,
        bank_object: Bank.Bank,
        sender_id: str | None = None,
        recipient_id: str | None = None,
        sender_acc_id: str | None = None,
        recipient_acc_id: str | None = None,
    ) -> None:
        """VAlidates clients and theirs accounts"""

        if not isinstance(bank_object, Bank.Bank):
            raise BA.InvalidOperationError("Not an Bank object")
        if transaction_type == "transfer":
            BA.validate_string(string=sender_acc_id, field_name="Sender account ID")
            BA.validate_string(string=recipient_acc_id, field_name="Recipient account ID")
            Bank.validate_account_to_client_id(client_id=sender_id, accountt_uuid=sender_acc_id, bank_object=bank_object)
            Bank.validate_account_to_client_id(client_id=recipient_id, accountt_uuid=recipient_acc_id, bank_object=bank_object)
        if transaction_type == "withdraw":
            BA.validate_string(string=sender_acc_id, field_name="Sender account ID")
            Bank.validate_account_to_client_id(client_id=sender_id, accountt_uuid=sender_acc_id, bank_object=bank_object)
            
        if transaction_type == "deposit":
            BA.validate_string(string=recipient_acc_id, field_name="Recipient account ID")
            Bank.validate_account_to_client_id(client_id=recipient_id, accountt_uuid=recipient_acc_id, bank_object=bank_object)
            
    def get_transaction_data(self)-> dict:
        transaction_data = {
            "Sender": self._sender_id,
            "Recipient": self._recipient_id,
            "Currency": self._currency,
            "Sender_acc_id": self._sender_acc_id,
            "Recipient_acc_id": self._recipient_acc_id,
            "Amount": self._amount,
            "Transaction_type": self._transaction_type,
            "Creation time" : self._creation_time,
            "Processing_time" : self._processing_time,
            "Transaction status" : self._status,
            "Failure reason" : self._failure_reason,
            'Transation ID' : self._id,
            "Transfer fee" : self._transfer_fee,
            'Sheduled at' : self._scheduled_at

        }
        return transaction_data

    def change_transaction_status(self, status: str)-> None:
        BA.validate_string(string=status, field_name='Transaction status')
        if status not in self.VALID_TRANSACTION_STATUSES:
            raise BA.InvalidOperationError('Wrong status')
        if self._status == 'pending' and status == 'processing':
            self._status = status
        elif self._status == 'pending' and status == 'cancelled':
            self._status = status
        elif self._status == 'processing' and status == 'completed':
            self._status = status
        elif self._status == 'processing' and status == 'failed':
            self._status = status
        elif self._status == 'failed' and status == 'pending':
            self._status = status
        else:
            raise BA.InvalidOperationError('Could not change status')





class TransactionQueue:
    VALID_PRIORITIES = ('1', '2', '3')
    """
    Queue control
    adds transaction
    gets next tranzaction
    cancels transaction
    priority
    - ➕ добавление
    - ⭐ приоритет
    - ⏳ отложенные операции
    - ❌ отмена
    """
    def __init__(self):
        self._transaction_queue = []

        pass

    def add_transaction(self,transaction_obj: Transaction, prioprity: str, sheduled_at: datetime | None = None)-> None:

        BA.validate_string(string=prioprity, field_name='Transaction priority')
        if  not isinstance(transaction_obj, Transaction):
            raise BA.InvalidOperationError('Wrong transaction onject')
        if prioprity not in self.VALID_PRIORITIES:
            raise BA.InvalidOperationError('No such priority types')
        if sheduled_at is not None:
            if not isinstance(sheduled_at, datetime):
                raise BA.InvalidOperationError('Not a datetime object')
            transaction_obj._scheduled_at = sheduled_at
        self._transaction_queue.append({prioprity:transaction_obj})


        

    def get_next_transaction(self):
        '''
        1 priority, 2 time (if more then one with same priority, skip if 
        ,chanhe status)
        remove transaction from queue
        '''
        self._approved_candidate: dict = None
        self._approved_candidate_prioirty: int = None
        
        num_to_remove = None
        for num, candidate in enumerate(self._transaction_queue):
            if list(candidate.values())[0]._status != 'pending':
                continue
            if list(candidate.values())[0]._scheduled_at is not None:
                            if list(candidate.values())[0]._scheduled_at <= datetime.now():
                                if self._approved_candidate_prioirty is None or self._approved_candidate_prioirty > int(list(candidate.keys())[0]):
                                    self._approved_candidate = self._transaction_queue[num]
                                    self._approved_candidate_prioirty = int(list(self._transaction_queue[num].keys())[0])
                                    num_to_remove = num
            if list(candidate.values())[0]._scheduled_at is None:
                            if self._approved_candidate_prioirty is None or self._approved_candidate_prioirty > int(list(candidate.keys())[0]):
                                self._approved_candidate = self._transaction_queue[num]
                                self._approved_candidate_prioirty = int(list(self._transaction_queue[num].keys())[0])
                                num_to_remove = num
        
            


        if num_to_remove is None:
            return None

        self._transaction_queue.pop(num_to_remove)
        return list(self._approved_candidate.values())[0]



        
        
        
        pass #    VALID_TRANSACTION_STATUSES = ( "pending",  "processing",  "completed", "failed", "cancelled",  )



    def cancel_transaction(self, transation_id,):
        pass
    









class TransactionProcessor:
    """
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
    """
