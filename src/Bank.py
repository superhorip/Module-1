from abc import ABC, abstractmethod
from uuid import uuid4
import math
import time

import Bank_Account_class as BA




class Client():
    def __init__(self, name: str, surname: str, age: int, client_id: str | None = None ):
        BA.validate_string(string=name, field_name='Name')
        self._name = name
        BA.validate_string(string=surname, field_name='Surname')
        self._surname =surname
        if not isinstance(age, int) or isinstance(age, bool):
            raise BA.InvalidOperationError('Age should be int type')
        if age < 18:
            raise BA.InvalidOperationError('Client should at list 18 years old')
        self._age = age

        if client_id is None:
            self._client_id = uuid4().hex[:12]
        else:
            BA.validate_string(string=client_id, field_name='Client id')
            self._client_id = client_id

        self._uuids = []

        
        

class Bank():
    def __init__(self ):

        self._all_clients: dict[str, Client] = {} # Dict for storing clients [client_id, Client object]
        self._all_bank_accounts: dict[str, BA.BankAccount] = {} # Dict for storing all accounts [account_uuid, BankAcc object]

        

    def add_client(self, name: str, surname: str, age: int)-> str:
        ''' 
        Создает клиента подтягивает данные из класса Client
        возвращет id созданного клиента
        '''
        new_client = Client(name=name, surname=surname, age=age)
        self._all_clients[new_client._client_id] = new_client
        return new_client._client_id




    def open_account(self, client_id: str, account_type: type[BA.BankAccount], currency: str = 'RUB', **kwargs )-> str:
        '''
        Октрывает счет
        '''
        BA.validate_string(string=client_id, field_name=('Сlient_ID'))
        if not isinstance (account_type, type) or not issubclass(account_type, BA.BankAccount):
            raise BA.InvalidOperationError('Wrong account type or not BankAccount subclass') 

        BA.validate_string(string=currency, field_name='Currency')

        if client_id not in self._all_clients.keys():
            raise BA.InvalidOperationError('No clients with such client ID exist')
        
        new_account = account_type(name= self._all_clients[client_id]._name,
                                        surname=self._all_clients[client_id]._surname,
                                        currency=currency,
                                        **kwargs)
        self._all_bank_accounts[new_account._uuid] = new_account
        self._all_clients[client_id]._uuids.append(new_account._uuid)

        return new_account._uuid

    def close_account(self,client_id: str, uuid_of_acc_to_close: str):
        '''
        закрывает счет 
        '''
        BA.validate_string(string=uuid_of_acc_to_close, field_name='UUID of account')
        BA.validate_string(string=client_id, field_name='Client id')

        if client_id not in self._all_clients.keys():
            raise BA.InvalidOperationError('No Client with such ID')
        if uuid_of_acc_to_close not in self._all_clients[client_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')

        self._all_bank_accounts[uuid_of_acc_to_close]._account_status = 'closed'


    def freeze_account(self, client_id: str, uuid_of_acc_to_freeze: str):
        '''
        замораживает счет
        '''
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=uuid_of_acc_to_freeze, field_name='UUID of account')

        if client_id not in self._all_clients.keys():
            raise BA.InvalidOperationError('No client with such ID')
        if uuid_of_acc_to_freeze not in self._all_clients[client_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')

        self._all_bank_accounts[uuid_of_acc_to_freeze]._account_status = 'frozen'

        

    def unfreeze_account(self, client_id: str, uuid_of_acc_to_unfreeze: str):
        '''
        размораживает счет
        '''
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=uuid_of_acc_to_unfreeze, field_name='UUID of account')

        if client_id not in self._all_clients.keys():
            raise BA.InvalidOperationError('No client with such ID')
        if uuid_of_acc_to_unfreeze not in self._all_clients[client_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')

        self._all_bank_accounts[uuid_of_acc_to_unfreeze]._account_status = 'active'

    def authenticate_client():
        ''' аутентификация, проверка. Не понимаю когда она выполняется? Нужен ли флаг что аутентификация выполнена когда происходят операции со счетом?
        Наверное да. Нужна ли аутентификация для add_client()
             🔒 3 неверные попытки входа = блокировка
-            ⚠️ пометка подозрительных действий
-            🌙 запрет операций с 00:00 до 05:00
        '''

        pass

    def search_accounts():
        '''Поиск аккаунтов по имени или отчеству
        '''
        pass

    def get_total_balance(self, *client_ids: str, all_bank_clients: bool =True):
        ''' 
        Расчет баланса банка по списку клиентов, если стоит флаг all_bank_clents то расчет идет по всем клинетам 
        и их счетам
        '''
        bank_total_balance = 0
        if not isinstance(all_bank_clients, bool):
            raise BA.InvalidOperationError('All bank clients var should be bool type')
        if all_bank_clients:
            for client_id, client_ojb in self._all_clients.items():
                for uuid in client_ojb._uuids:
                    account_info = self._all_bank_accounts[uuid].get_account_info()
                    if account_info['type'] == 'InvestmentBankAccount':
                        for _, amount in self._all_bank_accounts[uuid].portfolio.items():
                            bank_total_balance = bank_total_balance + amount
                    
                    bank_total_balance = bank_total_balance + self._all_bank_accounts[uuid]._balance
        return bank_total_balance
        



 
        


    def get_clients_ranking():
        ''' 
        Ранжирование клиентов по сумме активов
        '''
        pass












