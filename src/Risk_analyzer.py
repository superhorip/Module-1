from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import Transactions



class AuditLog():
    '''
    Stores transaction history of every user/ saves to disk reads before strart
    '''
    def __init__(self):
        #self.read_log_from_disk(file_name='log.txt')
        self._audit_log = []
        pass
    _audit_log: list[dict]

    def add_transation_to_log(self, transaction: "Transactions.Transaction", risk_level: str)->None:
        transaction_dict = transaction.get_transaction_data()
        transaction_dict['risk_level'] = risk_level
        self._audit_log.append(transaction_dict)

    def get_client_transaction_history(self, client_id: str)-> list:
         ''' returns all transaction logs by client_id
         '''
         if not isinstance(client_id, str):
              raise BA.InvalidOperationError('Wrong type')
         user_transactions = []
         for transaction_note in self._audit_log:
             if transaction_note._sender_id == client_id:
                  user_transactions.append(transaction_note)
         return user_transactions
        
        


    
    def make_client_risk_profile(self, client_id):
        '''
        Общее количество операций.
        Количество операций с MEDIUM и HIGH.
        Количество заблокированных операций.
        Максимальный зафиксированный уровень риска.
        '''
    pass

    def make_suspicious_operations_log(self)->list:
        '''Фильтрует журнал и возвращает транзакции с риском MEDIUM и HIGH.'''
        pass

    def read_log_from_disk(self, file_name: str):
        '''reads file'''
        pass
    def write_log_to_disk(self, file_name: str):
        '''reads file'''
        pass



class RiskAnalyzer():
    VALID_RISKS_LEVELS = ('LOW', 'MEDIUM', 'HIGH')
    MAXIMUM_OPERATIONS_PER_10_MINUTES = 5
    NIGHT_TIME_STARTS = 0
    NIGHT_TIME_ENDS = 5
    LARGE_AMOUNT_AS_PERCENT_OF_BALANCE = 0.5
    NUM_OF_TRANSFER_TO_NEW_ACCOUNTS = 3

    POINTS_PER_MAX_TIME_INTL_OPS = 20
    POINTS_PER_NEW_ACCOUTS_TRANSFER = 20
    POINTS_PER_LARGE_AMOUNT_TRANSFER = 30
    POINTS_PER_NIGHT_TRANSFER = 15

    LOW_RISK_TRESHOLD = 29
    MED_RISK_TRESHOLD = 59
    HIGH_RISK_TRESHOLD = 60

    
    def __init__(self, audit_log: list):
        self._risk_level = None
        pass

    def evaluate_transaction_risk(self, transaction: "Transactions.Transaction", audit_log: list)->str:
        '''
        Evaluates risk level and return it to Transaction processor

        '''
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError('Wrong data type')
        if not isinstance(audit_log, list):
                    raise BA.InvalidOperationError('Wrong data type')
        transaction_type = transaction._transaction_type
        if transaction_type == 'transfer' or transaction_type == 'withdraw':
             pass

    def evaluate_max_per_10_min_ops(self):
         '''Pass audit log throught constructor
         '''
         pass
    def evaluate_night_time(self):
         pass
             


      
    def evaluate_large_sum_transfer(self, transaction: "Transactions.Transaction", bank_obj: "Bank.Bank")->bool:
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError('Wrong data type')
        if not isinstance(bank_obj, Bank.Bank):
            raise BA.InvalidOperationError('Wrong data type')        
        transaction_type = transaction._transaction_type
        if transaction_type == 'transfer' or transaction_type == 'withdraw':
            threshold = bank_obj._all_bank_accounts[transaction._sender_acc_id]._balance * self.LARGE_AMOUNT_AS_PERCENT_OF_BALANCE
            if transaction._amount > threshold:
                  return True
            else:
                  return False
        else:
             return False
                             
                 


