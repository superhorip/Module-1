from abc import ABC, abstractmethod
from uuid import uuid4
import math
import time

import Bank_Account_class as BA




class Client():
    def __init__(self, name: str, surname: str, age: int, client_id: str | None = None ):
        if not isinstance(name, str) or not name.strip():
            raise BA.InvalidOperationError('Client name should be a string and not empty')
        self._name = name
        if not isinstance(surname, str) or not surname.strip():
            raise BA.InvalidOperationError('Client name should be a string and not empty')
        self._surname =surname
        if not isinstance(age, int) or isinstance(age, bool):
            raise BA.InvalidOperationError('Age should be int type')
        if age < 18:
            raise BA.InvalidOperationError('Client should at list 18 years old')
        self._age = age

        if client_id is None:
            self._client_id = uuid4().hex[:12]
        else:
            if not isinstance(client_id, str) or not client_id.strip():
                raise BA.InvalidOperationError('Client ID should be str and not empty')
            self._client_id = client_id

        self._uuids = []
        





    



class Bank():
    def __init__(self):

        pass

    def add_client():
        ''' 
        Создает клиента подтягивает данные из класса Client создает дефолтный счет
        '''
        pass

    def open_account():
        '''
        Октрывает любой другой счет
        '''
        pass

    def close_account():
        '''
        закрывает счет 
        '''
        pass

    def freeze_account():
        '''
        замораживает счет
        '''
        pass

    def unfreeze_account():
        '''
        размораживает счет
        '''
        pass

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

    def get_total_balance():
        ''' 
        Расчет баланса банка по всем считам по всем клиаентам и активам
        '''
        pass

    def get_clients_ranking():
        ''' 
        Ранжирование клиентов по сумме активов
        '''
        pass












