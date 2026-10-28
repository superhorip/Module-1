from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA




class Client():
    def __init__(self, name: str, surname: str, age: int, phone_number: str, client_id: str | None = None ):
        BA.validate_string(string=name, field_name='Name')
        self._name = name
        BA.validate_string(string=surname, field_name='Surname')
        self._surname =surname
        BA.validate_string(phone_number, field_name='Phone number')
        self._phone_number = phone_number
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
        self._isblocked = False
        self._isauthentificated = False
        self._is_verification_passed = False
        self._num_of_login_attempts = 0
        
        
    
    def is_client_blocked(self)-> bool:
        return self._isblocked

    def is_client_authentificated(self)->bool:
        return self._isauthentificated

    def block_unblock_client(self, block_client: bool):
        '''
        action to block_client -> Block if True, unblock if False
        '''
        if not isinstance(block_client, bool):
            raise BA.InvalidOperationError('Flag chould bee Bool type')
        if block_client:
            self._isblocked = True
            self._isauthentificated = False
        else:
            self._isblocked = False

    def change_login_attempts(self, add_or_reset: bool):
        '''
        if add_or_reset, adds + 1 attempt if True, resets to zero if False
        '''
        if not isinstance(add_or_reset, bool):
            raise BA.InvalidOperationError('Flag chould bee Bool type')
        
        if add_or_reset:
            if self._num_of_login_attempts == 2:
                self.block_unblock_client(True)
                self._num_of_login_attempts = self._num_of_login_attempts + 1
                raise BA.InvalidOperationError('Maximum login attemps reached client is blocked')
            else:
                self._num_of_login_attempts += 1
        if not add_or_reset:
            self._num_of_login_attempts = 0

    def change_auth_status(self, authenthificate_or_not: bool):
        '''
        Authentification means kinda auth throug password for bank app
        True means change change to auth, and False means change to not
        '''
        if not isinstance(authenthificate_or_not, bool):
            raise BA.InvalidOperationError('Flag chould bee Bool type')
        if authenthificate_or_not:
            self._isauthentificated = True
        else:
            self._isauthentificated = False        




        
        

class Bank():
    def __init__(self ):

        self._all_clients: dict[str, Client] = {} # Dict for storing clients [client_id, Client object]
        self._all_bank_accounts: dict[str, BA.BankAccount] = {} # Dict for storing all accounts [account_uuid, BankAcc object]
        self._suspecious_actions: list[dict] = []

        

    def add_client(self, name: str, surname: str, age: int, phone_number: str)-> str:
        ''' 
        Создает клиента подтягивает данные из класса Client
        возвращет id созданного клиента
        '''
        new_client = Client(name=name, surname=surname, age=age, phone_number=phone_number)
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
        
        self.check_security(client_id=client_id, action='Open')
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
        self.check_security(client_id=client_id, action='Close account')

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

        self.check_security(client_id=client_id, action='Freeze account')
        if self._all_bank_accounts[uuid_of_acc_to_freeze]._account_status == 'closed':
            raise BA.InvalidOperationError('Closed account coudnot be freezed')
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
        self.check_security(client_id=client_id, action='Unfreeze account')

        if self._all_bank_accounts[uuid_of_acc_to_unfreeze]._account_status == 'closed':
            raise BA.InvalidOperationError('Could not unfreeze closed account')
        self._all_bank_accounts[uuid_of_acc_to_unfreeze]._account_status = 'active'

        

    def authenticate_client(self, client_id: str, verification_passed: bool):
        ''' 

        '''
        BA.validate_string(string=client_id, field_name='Client id')
        if not isinstance(verification_passed, bool):
            raise BA.InvalidOperationError('Flag should be boool type')
        if client_id not in self._all_clients:
            raise BA.InvalidOperationError('No client with such ID')

        self.check_security(client_id=client_id, action='Authentification procedure')
        
        if not verification_passed:
            self._all_clients[client_id].change_login_attempts(True)
            self._all_clients[client_id].change_auth_status(False)
        if verification_passed:
            self._all_clients[client_id].change_login_attempts(add_or_reset=False)
            self._all_clients[client_id].change_auth_status(True)


    def check_allowed_time_interval(self)-> bool:
        '''
        Checks time when operations are not allowed
        re
        '''
        current_hour = datetime.now().hour
        if  0 <= current_hour < 5:
            # raise BA.InvalidOperationError('Operations are not allowed for this time')
            return False
        else:
            return True

    def check_security(self, client_id: str, action: str):
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=action, field_name='Action name')
        if client_id not in self._all_clients:
            raise BA.InvalidOperationError('No client with such ID')
        if self._all_clients[client_id]._isblocked:
            self._suspecious_actions.append({'Client ID': client_id, 'Action': action, 'Reason':'Client is blocked', 'time': datetime.now() })
            raise BA.InvalidOperationError('Client is blocked. No operations are allowed')
        if not self.check_allowed_time_interval():
            self._suspecious_actions.append({'Client ID': client_id, 'Action': action, 'Reason':'Night operations are not allowed', 'time': datetime.now() })
            raise BA.InvalidOperationError('Night operations are not allowed')

 

    def search_accounts(self, name: str, surname: str)-> dict:
        '''Поиск аккаунтов по имени и фамилии
        '''
        BA.validate_string(string=name, field_name='Name')
        BA.validate_string(string=surname, field_name='Surname')
        founded_clients: dict[str, list[str]] = {}
        for client_id, client_obj in self._all_clients.items():
            if client_obj._name == name:
                if client_obj._surname == surname:
                    founded_clients[client_id] = client_obj._uuids.copy()

        return founded_clients
                

    def get_total_balance(self, *client_ids: str, all_bank_clients: bool =True)-> float:
        ''' 
        Расчет баланса банка по списку клиентов, если стоит флаг all_bank_clents то расчет идет по всем клинетам 
        и их счетам
        '''
        bank_total_balance = {'RUB' : 0, 'USD' : 0, 'EUR' : 0, 'KZT' : 0, 'CNY': 0}
        if not isinstance(all_bank_clients, bool):
            raise BA.InvalidOperationError('All bank clients var should be bool type')
        if all_bank_clients:
            for client_id, client_obj in self._all_clients.items():
                for uuid in client_obj._uuids:
                    acc_currency = self._all_bank_accounts[uuid]._currency
                    if isinstance(self._all_bank_accounts[uuid], BA.InvestmentAccount):
                        for _, amount in self._all_bank_accounts[uuid].portfolio.items():
                            bank_total_balance[acc_currency] = bank_total_balance[acc_currency] + amount
                    bank_total_balance[acc_currency] = bank_total_balance[acc_currency] + self._all_bank_accounts[uuid]._balance
            return bank_total_balance

        if not all_bank_clients:
            if any(client_id not in self._all_clients for client_id in client_ids):
                raise BA.InvalidOperationError('No such client in clients list')
            for client_id in set(client_ids): #avoiding duplicates
                for uuid in self._all_clients[client_id]._uuids:
                    acc_currency = self._all_bank_accounts[uuid]._currency
                    if isinstance(self._all_bank_accounts[uuid], BA.InvestmentAccount):
                        for _, amount in self._all_bank_accounts[uuid].portfolio.items():
                            bank_total_balance[acc_currency] = bank_total_balance[acc_currency] + amount
                    bank_total_balance[acc_currency] = bank_total_balance[acc_currency] + self._all_bank_accounts[uuid]._balance
            return bank_total_balance
    
 

    def get_clients_ranking(self, *client_ids: str, all_bank_clients: bool =True):
        ''' 
        Ранжирование клиентов по сумме активов
        '''
        if not isinstance(all_bank_clients, bool):
            raise BA.InvalidOperationError('All bank clients var should be bool type')
        if any(client_id not in self._all_clients for client_id in client_ids):
            raise BA.InvalidOperationError('No such client in clients list')

        clients_sum_balance: dict[str, float] = {}  # for storing clients balance and uuids
        if all_bank_clients:
            for client_id, _ in self._all_clients.items():
                client_currencies_dict = self.get_total_balance(client_id, all_bank_clients=False)
                client_total_sum = sum(client_currencies_dict.values())
                clients_sum_balance[client_id] = client_total_sum

        if not all_bank_clients:
            for client_id in client_ids:
                client_currencies_dict = self.get_total_balance(client_id, all_bank_clients=False)
                client_total_sum = sum(client_currencies_dict.values())
                clients_sum_balance[client_id] = client_total_sum

        return sorted(clients_sum_balance.items(), key=lambda item: item[1], reverse=True)

    def deposit(self, client_id: str, amount: float, acccount_uuid: str):
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=acccount_uuid, field_name='Account UUID')
        BA.validate_amount(amount=amount)
        if client_id not in self._all_clients:
            raise BA.InvalidOperationError('No client with such ID')
        if acccount_uuid not in self._all_clients[client_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')
        self.check_security(client_id=client_id, action='Deposition of money to account')
        self._all_bank_accounts[acccount_uuid].deposit(amount=amount)

    def withdraw(self, client_id: str, amount: float, acccount_uuid: str):
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=acccount_uuid, field_name='Account UUID')
        BA.validate_amount(amount=amount)
        if client_id not in self._all_clients:
            raise BA.InvalidOperationError('No client with such ID')
        if acccount_uuid not in self._all_clients[client_id]._uuids:
            raise BA.InvalidOperationError('Client does not have such account ID')
        self.check_security(client_id=client_id, action='Withdrowal of money from account')
        self._all_bank_accounts[acccount_uuid].withdraw(amount=amount)



     












