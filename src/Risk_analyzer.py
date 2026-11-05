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
    Stores transaction history of every user
    '''
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

    def evaluate_transaction_risk(self, transaction: "Transactions.Transaction")->str:
        '''
        Evaluates risk level and return it to Transaction processor

        '''

        return 'MEDIUM'
        pass


    def get_data_from_audit_log(self, log: AuditLog):
        pass


