from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank
import Risk_analyzer as RiskAnalyzer

class Transaction:
    CURRENCIES = ("RUB", "USD", "EUR", "KZT", "CNY")
    VALID_TRANSACTION_STATUSES = (
        "pending",
        "processing",
        "completed",
        "failed",
        "cancelled",
    )
    TRANSATION_TYPES = ("transfer", "withdraw", "deposit")
    MAX_RETRIES = 3
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
        scheduled_at: datetime | None = None,
    ) -> None:
        """
        3 types of transaction: transfer, withdraw, deposit
        """
        self._id = str(uuid4())
        self.validate_transaction_data(transaction_type=transaction_type, currency=currency, amount=amount, sender_id=sender_id, recipient_id=recipient_id)

        self.validate_bank_data(transaction_type=transaction_type, bank_object=bank_object, sender_id=sender_id, recipient_id=recipient_id, sender_acc_id=sender_acc_id, recipient_acc_id=recipient_acc_id)

        if scheduled_at is not None:
            if not isinstance(scheduled_at, datetime):
                raise BA.InvalidOperationError("Wrong datetime object")
        self._sender_id = sender_id
        self._recipient_id = recipient_id
        self._currency = currency
        self._amount = amount
        self._transaction_type = transaction_type
        self._recipient_acc_id = recipient_acc_id
        self._sender_acc_id = sender_acc_id
        self._status = "pending"
        self._failure_reason = None
        self._transfer_fee = 0 # always in transaction currency
        self._creation_time = datetime.now()
        self._processing_time = None
        self._scheduled_at = scheduled_at
        self._retry_count = 0

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

    def get_transaction_data(self) -> dict:
        transaction_data = {
            "Sender": self._sender_id,
            "Recipient": self._recipient_id,
            "Currency": self._currency,
            "Sender_acc_id": self._sender_acc_id,
            "Recipient_acc_id": self._recipient_acc_id,
            "Amount": self._amount,
            "Transaction_type": self._transaction_type,
            "Creation time": self._creation_time,
            "Processing_time": self._processing_time,
            "Transaction status": self._status,
            "Failure reason": self._failure_reason,
            "Transation ID": self._id,
            "Transfer fee": self._transfer_fee,
            "Sheduled at": self._scheduled_at,
            "Retry count": self._retry_count
        }
        return transaction_data

    def change_transaction_status(self, status: str) -> None:
        BA.validate_string(string=status, field_name="Transaction status")
        if status not in self.VALID_TRANSACTION_STATUSES:
            raise BA.InvalidOperationError("Wrong status")
        if self._status == "pending" and status == "processing":
            self._status = status
        elif self._status == "pending" and status == "cancelled":
            self._status = status
        elif self._status == "processing" and status == "completed":
            self._status = status
        elif self._status == "processing" and status == "failed":
            self._status = status
        elif self._status == "failed" and status == "pending":
            self._status = status
        else:
            raise BA.InvalidOperationError("Could not change status")


class TransactionQueue:
    VALID_PRIORITIES = ("1", "2", "3")
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

    def add_transaction(self, transaction_obj: Transaction, prioprity: str, sheduled_at: datetime | None = None) -> None:

        
        BA.validate_string(string=prioprity, field_name="Transaction priority")
        if not isinstance(transaction_obj, Transaction):
            raise BA.InvalidOperationError("Wrong transaction onject")
        if prioprity not in self.VALID_PRIORITIES:
            raise BA.InvalidOperationError("No such priority types")
        if sheduled_at is not None:
            if not isinstance(sheduled_at, datetime):
                raise BA.InvalidOperationError("Not a datetime object")
            transaction_obj._scheduled_at = sheduled_at
        if any(list(item.values())[0]._id == transaction_obj._id for item in self._transaction_queue):
                raise BA.InvalidOperationError("Transaction already in queue")

        self._transaction_queue.append({prioprity: transaction_obj})

    def get_next_transaction(self)->Transaction:
        """
        1 priority, 2 time (if more then one with same priority, skip if
        ,chanhe status)
        remove transaction from queue
        """
        self._approved_candidate: dict = None
        self._approved_candidate_prioirty: int = None

        num_to_remove = None
        for num, candidate in enumerate(self._transaction_queue):
            if list(candidate.values())[0]._status != "pending":
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

        pass  #    VALID_TRANSACTION_STATUSES = ( "pending",  "processing",  "completed", "failed", "cancelled",  )

    def cancel_transaction(self, transation_id: str):
        transation_found = False
        BA.validate_string(string=transation_id, field_name="Transaction ID")
        for num, transaction_dict in enumerate(self._transaction_queue):
            if list(transaction_dict.values())[0]._id == transation_id and list(transaction_dict.values())[0]._status == "pending":
                list(transaction_dict.values())[0].change_transaction_status(status="cancelled")
                transation_found = True
                break
        if not transation_found:
            raise BA.InvalidOperationError("Transaction not found or has not pending status")


class TransactionProcessor:
    COMMISSION_FEE = 0.01
    VALID_RISKS_LEVELS = ('LOW', 'MEDIUM', 'HIGH')
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

    def get_transaction(self, transaction_queue: TransactionQueue)->Transaction:
        #TRANSATION_TYPES = ("transfer", "withdraw", "deposit")
        '''
        gets transaction from queue
        '''
        if not isinstance(transaction_queue, TransactionQueue):
            raise BA.InvalidOperationError('Not a queue object')

        transaction = transaction_queue.get_next_transaction()
        if transaction is None:
            return None
        if not isinstance(transaction, Transaction):
            raise BA.InvalidOperationError('Not Transaction type object')
        return transaction




    def make_transaction(self, transaction_queue: TransactionQueue, bank_obj: Bank.Bank, currency_convertr: "CurrencyConverter", risk_analyser: RiskAnalyzer.RiskAnalyzer):
        ''' main method that calls for other methods'''
        
        if not isinstance(transaction_queue, TransactionQueue):
            raise BA.InvalidOperationError('Wrong object')
        if not isinstance(bank_obj, Bank.Bank):
            raise BA.InvalidOperationError('Wrong object')
        if not isinstance(currency_convertr, CurrencyConverter):
            raise BA.InvalidOperationError('Not Converter type')         
        transaction = self.get_transaction(transaction_queue=transaction_queue)
        if transaction is None:
            raise BA.InvalidOperationError('No suitable transactions in queue')
        if not isinstance(risk_analyser, RiskAnalyzer.RiskAnalyzer):
            BA.InvalidOperationError('Wrong object type')
        transaction._processing_time = datetime.now()
        transaction.change_transaction_status(status='processing')
        transaction_risk = risk_analyser.evaluate_transaction_risk(transaction=transaction)
        if transaction_risk not in self.VALID_RISKS_LEVELS:
            raise BA.InvalidOperationError('Not such risk level')
        if transaction_risk == 'HIGH':
            BA.InvalidOperationError('High risk_transaction. Processing stopped')
            transaction.change_transaction_status(status='failed')


        try:
            if transaction._transaction_type == 'transfer':
                need_currency_conversion = self.validate_currency_convertion(transaction=transaction, bank=bank_obj)
                dont_need_extra_fee = False
                if bank_obj._all_bank_accounts[transaction._sender_acc_id].get_account_info()['type'] == 'PremiumBankAccount':
                    dont_need_extra_fee = True
                    self.execute_transfer(transaction=transaction, bank_obj=bank_obj, need_corrency_conversion=need_currency_conversion, dont_need_extra_fee=dont_need_extra_fee,
                                        currency_convertr=currency_convertr, bank_fee=0)                
                if not dont_need_extra_fee:
                    bank_fee = self.calculate_bank_fee(transaction=transaction,bank=bank_obj, currency_convertr=currency_convertr)
                    transaction._transfer_fee = self.COMMISSION_FEE * transaction._amount
                    self.execute_transfer(transaction=transaction, bank_obj=bank_obj, need_corrency_conversion=need_currency_conversion, dont_need_extra_fee=dont_need_extra_fee,
                                        currency_convertr=currency_convertr, bank_fee=bank_fee)
            if transaction._transaction_type == 'withdraw':
                need_currency_conversion = self.validate_currency_convertion(transaction=transaction, bank=bank_obj)
                dont_need_extra_fee = True
                self.execute_transfer(transaction=transaction, bank_obj=bank_obj, need_corrency_conversion=need_currency_conversion, dont_need_extra_fee=dont_need_extra_fee,
                                        currency_convertr=currency_convertr, bank_fee=0)          
            if transaction._transaction_type == 'deposit':
                need_currency_conversion = self.validate_currency_convertion(transaction=transaction, bank=bank_obj)
                dont_need_extra_fee = True
                self.execute_transfer(transaction=transaction, bank_obj=bank_obj, need_corrency_conversion=need_currency_conversion, dont_need_extra_fee=dont_need_extra_fee,
                                        currency_convertr=currency_convertr, bank_fee=0)
        except (BA.InvalidOperationError, BA.AccountClosedError, BA.AccountFrozenError, BA.InsufficientFundsError) as e:
            print (f'Operation failed: {e}')
            transaction._failure_reason = f'Operation failed: {e}'
            if transaction._status != 'failed':
                transaction.change_transaction_status(status='failed')





    def validate_currency_convertion(self, transaction: Transaction, bank: Bank.Bank):
        """check if both accounts have same currency and need for convertation
        returns FAlse if same, True if differs
        This function is only for between users transfers
        """
        if transaction._transaction_type == 'transfer':
            transaction_currency = transaction._currency
            sender_acc_obj = bank._all_bank_accounts[transaction._sender_acc_id]
            sender_acc_cur = sender_acc_obj._currency
            recipient_acc_obj = bank._all_bank_accounts[transaction._recipient_acc_id]
            recipient_acc_cur = recipient_acc_obj._currency
            if transaction_currency not in (recipient_acc_cur, sender_acc_cur):
                raise BA.InvalidOperationError('Invalid transaction currency')
            if sender_acc_cur != recipient_acc_cur :
                return True
            else:
                return False
        if transaction._transaction_type == 'withdraw':
            transaction_currency = transaction._currency
            sender_acc_obj = bank._all_bank_accounts[transaction._sender_acc_id]
            sender_acc_cur = sender_acc_obj._currency
            if sender_acc_cur != transaction_currency:
                return True
            else:
                return False
        if transaction._transaction_type == 'deposit':
            transaction_currency = transaction._currency
            recipient_acc_obj = bank._all_bank_accounts[transaction._recipient_acc_id]
            recipient_acc_cur = recipient_acc_obj._currency
            if transaction._currency != recipient_acc_cur :
                return True
            else:
                return False   



    def calculate_bank_fee(self ,transaction: Transaction, currency_convertr: "CurrencyConverter", bank: Bank.Bank):
        '''
        calculate fee only between users transaction and not if withdrowal or deposit operations
        '''

        if not isinstance(transaction, Transaction):
            raise BA.InvalidOperationError('Not transaction type')
        if not isinstance(currency_convertr, CurrencyConverter):
            raise BA.InvalidOperationError('Not Converter type')
        if not isinstance(bank, Bank.Bank):
            raise BA.InvalidOperationError('Not bank object')
        trans_fee = transaction._amount * self.COMMISSION_FEE
        if bank._all_bank_accounts[transaction._sender_acc_id]._currency != transaction._currency:
            bank_fee = currency_convertr.convert(amount = trans_fee, from_currency=transaction._currency , to_currency=bank._all_bank_accounts[transaction._sender_acc_id]._currency)
            return bank_fee
        else:
            return trans_fee



    def execute_transfer(self, transaction: Transaction, bank_obj: Bank.Bank, need_corrency_conversion: bool, dont_need_extra_fee: bool, currency_convertr: "CurrencyConverter", bank_fee: float):
        ''' makes transfer withdrowal and deposit oprations'''
        if not isinstance(bank_obj, Bank.Bank):
            raise BA.InvalidOperationError('Not bank object')
        if not isinstance(transaction, Transaction):
            raise BA.InvalidOperationError('Not transaction type')
        if not isinstance(need_corrency_conversion, bool):
            raise BA.InvalidOperationError('Not bool type')
        if not isinstance(dont_need_extra_fee, bool):
            raise BA.InvalidOperationError('Not bool type')
        if transaction._transaction_type == 'transfer':
            BA.validate_amount(amount=bank_fee, allow_zero=True)
            sender_profile_is_blocked = bank_obj._all_clients[transaction._sender_id]._isblocked
            recipient_profile_is_blocked = bank_obj._all_clients[transaction._recipient_id]._isblocked
            sender_account_active = False
            recipient_account_active = False
            if bank_obj._all_bank_accounts[transaction._sender_acc_id]._account_status == 'active':
                sender_account_active = True
            if bank_obj._all_bank_accounts[transaction._recipient_acc_id]._account_status == 'active':
                recipient_account_active = True
            if need_corrency_conversion:
                amount_to_withdraw = currency_convertr.convert(amount=transaction._amount, from_currency=transaction._currency , to_currency=bank_obj._all_bank_accounts[transaction._sender_acc_id]._currency)
            else:
                amount_to_withdraw = transaction._amount
            if need_corrency_conversion:
                amount_to_deposit = currency_convertr.convert(amount=transaction._amount, from_currency=transaction._currency , to_currency=bank_obj._all_bank_accounts[transaction._recipient_acc_id]._currency)
            else:
                amount_to_deposit = transaction._amount
            if not sender_profile_is_blocked and not recipient_profile_is_blocked and sender_account_active and recipient_account_active:
                if dont_need_extra_fee:
                    try:
                        bank_obj.withdraw(client_id=transaction._sender_id, amount=amount_to_withdraw, acccount_uuid=transaction._sender_acc_id)
                        bank_obj.deposit(client_id=transaction._recipient_id, amount=amount_to_deposit, acccount_uuid=transaction._recipient_acc_id)
                        transaction.change_transaction_status(status='completed')
                    except (BA.InvalidOperationError, BA.AccountClosedError, BA.AccountFrozenError, BA.InsufficientFundsError) as e:
                        print (f'Operation failed: {e}')
                        transaction._failure_reason = f'Operation failed: {e}'
                        transaction.change_transaction_status(status='failed')                        
                else:
                    try:
                        bank_obj.withdraw(client_id=transaction._sender_id,amount=amount_to_withdraw+bank_fee, acccount_uuid=transaction._sender_acc_id)
                        bank_obj.deposit(client_id=transaction._recipient_id, amount=amount_to_deposit, acccount_uuid=transaction._recipient_acc_id)
                        transaction.change_transaction_status(status='completed')
                    except (BA.InvalidOperationError, BA.AccountClosedError, BA.AccountFrozenError, BA.InsufficientFundsError) as e:
                        print (f'Operation failed: {e}')
                        transaction._failure_reason = f'Operation failed: {e}'                        
                        transaction.change_transaction_status(status='failed')
                
            else:
                transaction.change_transaction_status(status='failed')
                transaction._failure_reason = 'Account blocked, frozen or client is blocked'
                
        if transaction._transaction_type == 'withdraw':
            BA.validate_amount(amount=bank_fee, allow_zero=True)
            sender_profile_is_blocked = bank_obj._all_clients[transaction._sender_id]._isblocked
            sender_account_active = False
            if bank_obj._all_bank_accounts[transaction._sender_acc_id]._account_status == 'active':
                sender_account_active = True
            if need_corrency_conversion:
                amount_to_withdraw = currency_convertr.convert(amount=transaction._amount, from_currency=transaction._currency , to_currency=bank_obj._all_bank_accounts[transaction._sender_acc_id]._currency)
            else:
                amount_to_withdraw = transaction._amount
            if not sender_profile_is_blocked and sender_account_active:
                try:
                    bank_obj.withdraw(client_id=transaction._sender_id, amount=amount_to_withdraw, acccount_uuid=transaction._sender_acc_id)
                    transaction.change_transaction_status(status='completed')
                except (BA.InvalidOperationError, BA.AccountClosedError, BA.AccountFrozenError, BA.InsufficientFundsError) as e:
                        print (f'Operation failed: {e}')
                        transaction._failure_reason = f'Operation failed: {e}'                        
                        transaction.change_transaction_status(status='failed')
            else:
                transaction.change_transaction_status(status='failed')
                transaction._failure_reason = 'Account blocked, frozen or client is blocked'                
                            
                
        if transaction._transaction_type == 'deposit':
            BA.validate_amount(amount=bank_fee, allow_zero=True)
            recipient_profile_is_blocked = bank_obj._all_clients[transaction._recipient_id]._isblocked
            recipient_account_active = False
            if bank_obj._all_bank_accounts[transaction._recipient_acc_id]._account_status == 'active':
                recipient_account_active = True
            if need_corrency_conversion:
                amount_to_deposit = currency_convertr.convert(amount=transaction._amount, from_currency=transaction._currency , to_currency=bank_obj._all_bank_accounts[transaction._recipient_acc_id]._currency)
            else:
                amount_to_deposit = transaction._amount
            if not recipient_profile_is_blocked and recipient_account_active:
                try:
                    bank_obj.deposit(client_id=transaction._recipient_id, amount=amount_to_deposit, acccount_uuid=transaction._recipient_acc_id)
                    transaction.change_transaction_status(status='completed')
                except (BA.InvalidOperationError, BA.AccountClosedError, BA.AccountFrozenError) as e:
                        print (f'Operation failed: {e}')
                        transaction.change_transaction_status(status='failed')   
                        transaction._failure_reason = f'Operation failed: {e}'                                         
            else:
                transaction.change_transaction_status(status='failed')
                transaction._failure_reason = 'Account blocked, frozen or client is blocked'                     



            

        
        ##!!!!!!!!!
        
        pass

def retry_transaction(self,  transaction: Transaction, transaction_queue: TransactionQueue, priority: str = "2") -> None:

    if not isinstance(transaction, Transaction):
        raise BA.InvalidOperationError("Not a Transaction object")

    if not isinstance(transaction_queue, TransactionQueue):
        raise BA.InvalidOperationError("Not a TransactionQueue object")

    if transaction._status != "failed":
        raise BA.InvalidOperationError("Only failed transactions can be retried")

    if transaction._retry_count >= transaction.MAX_RETRIES:
        raise BA.InvalidOperationError("Maximum retries exceeded")

    transaction.change_transaction_status("pending")
    transaction_queue.add_transaction(transaction_obj=transaction,  prioprity=priority, sheduled_at=datetime.now() )
    transaction._retry_count += 1
    transaction._failure_reason = None



class CurrencyConverter():
    currency_rates: dict[str, float] = {
        "USD": 90.0,
        "EUR": 100.0,
        "KZT": 0.20,
        "CNY": 12.0,
        "RUB": 1.0,
    }

    def convert(self, amount, from_currency, to_currency)-> float:
        '''
        converts from currency to currency throught RUB 
        
        '''
        BA.validate_amount(amount=amount)
        BA.validate_string(string=from_currency, field_name=('Currency'))
        BA.validate_string(string=to_currency, field_name=('Currency'))
        if from_currency not in self.currency_rates.keys():
            raise BA.InvalidOperationError('No such currency in exchange rates')
        if to_currency not in self.currency_rates.keys():
                    raise BA.InvalidOperationError('No such currency in exchange rates')
        return ((amount*self.currency_rates[from_currency])/self.currency_rates[to_currency])
