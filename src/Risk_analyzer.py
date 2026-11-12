from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime, timedelta

import Bank_Account_class as BA
import Bank as Bank
from typing import TYPE_CHECKING
import json
from pathlib import Path

if TYPE_CHECKING:
    import Transactions


class AuditLog:
    """
    Stores transaction history of every user/ saves to disk reads before strart
    """

    def __init__(
        self, file_name: str
    ):
        # self.read_log_from_disk(file_name='log.txt')
        self._audit_log = []
        if not isinstance(file_name, str):
            raise BA.InvalidOperationError("Wrong type")          
        p = Path(file_name)
        if p.is_file():
            self.read_log_from_disk(file_name=file_name)
        

    def add_transation_to_log(self, transaction: "Transactions.Transaction", risk_level: str, file_name: str) -> None:
        if not isinstance(risk_level, str):
            raise BA.InvalidOperationError("Wrong type")
        if not isinstance(file_name, str):
            raise BA.InvalidOperationError("Wrong type")        
        transaction_dict = transaction.get_transaction_data()
        transaction_dict["risk_level"] = risk_level
        self._audit_log.append(transaction_dict)
        self.write_log_to_disk(file_name=file_name)

    def get_client_transaction_history(self, client_id: str) -> list:
        """returns all transaction logs by client_id"""
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        user_transactions = []
        for transaction_note in self._audit_log:
            if transaction_note['Sender'] == client_id or transaction_note['Recipient'] == client_id :
                user_transactions.append(transaction_note)
        return user_transactions

    def make_client_risk_profile(self, client_id: str) -> dict:
        """
        Общее количество операций.
        Количество операций с MEDIUM и HIGH.
        """
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        client_transactions = self.get_client_transaction_history(client_id=client_id)
        medium_and_high_risk_ops: int = 0
        for trasction_note in client_transactions:
            if trasction_note['risk_level'] == 'MEDIUM' or trasction_note['risk_level'] == 'HIGH':
                medium_and_high_risk_ops += 1
        return {'Total ops number': len(client_transactions), 'Mid and high level ops number': medium_and_high_risk_ops}




    def make_suspicious_operations_log(self, client_id: str) -> list:
        """Фильтрует журнал и возвращает транзакции с риском MEDIUM и HIGH."""
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        client_transactions = self.get_client_transaction_history(client_id=client_id)
        susp_transction =[]
        for trasction_note in client_transactions:
            if trasction_note['risk_level'] == 'MEDIUM' or trasction_note['risk_level'] == 'HIGH':
                susp_transction.append(trasction_note)
        return susp_transction

    def read_log_from_disk(self, file_name: str):
        """reads file"""
        if not isinstance(file_name, str):
            raise BA.InvalidOperationError("Wrong type")          
        with open(file_name, "r", encoding='utf-8') as file:
            self._audit_log = json.load(file)

        for transaction_note in self._audit_log:
            if transaction_note['Creation time'] is not None:
                transaction_note["Creation time"] = datetime.fromisoformat(transaction_note["Creation time"])
            if transaction_note['Processing_time'] is not None:
                transaction_note["Processing_time"] = datetime.fromisoformat(transaction_note["Processing_time"])
            if transaction_note['Sheduled at'] is not None:
                transaction_note["Sheduled at"] = datetime.fromisoformat(transaction_note["Sheduled at"])


    def write_log_to_disk(self, file_name: str):
        """writes file"""
        if not isinstance(file_name, str):
            raise BA.InvalidOperationError("Wrong type")          
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(self._audit_log, file, indent=4, default=str)
        
        


class RiskAnalyzer:
    VALID_RISKS_LEVELS = ("LOW", "MEDIUM", "HIGH")
    MAXIMUM_OPERATIONS_PER_10_MINUTES = 5
    LARGE_AMOUNT_AS_PERCENT_OF_BALANCE = 0.5

    POINTS_PER_MAX_TIME_INTL_OPS = 20
    POINTS_PER_NEW_ACCOUTS_TRANSFER = 20
    POINTS_PER_LARGE_AMOUNT_TRANSFER = 30
    POINTS_PER_NIGHT_TRANSFER = 15

    LOW_RISK_TRESHOLD = 29
    MED_RISK_TRESHOLD = 59


    def __init__(self, audit_log: AuditLog, bank_obj: "Bank.Bank", cur_converter: "Transactions.CurrencyConverter" ):
        if not isinstance(audit_log, AuditLog):
            raise BA.InvalidOperationError("Wrong datatype")
        if not isinstance(bank_obj, Bank.Bank):
            raise BA.InvalidOperationError("Wrong data type")
        self._audit_log = audit_log
        self._bank_obj = bank_obj
        self._risk_level = "LOW"
        self._cur_converter = cur_converter

    def evaluate_transaction_risk(self, transaction: "Transactions.Transaction") -> str:
        """
        #Evaluates risk level and return it to Transaction processor

        """
        points = 0
        if not self._bank_obj.check_allowed_time_interval():
            points = points + self.POINTS_PER_NIGHT_TRANSFER
        transaction_type = transaction._transaction_type
        if transaction_type == "transfer" or transaction_type == "withdraw":
            if self.evaluate_large_sum_transfer(transaction=transaction):
                points = points + self.POINTS_PER_LARGE_AMOUNT_TRANSFER
            if self.evaluate_max_per_10_min_ops(client_id=transaction._sender_id) >= self.MAXIMUM_OPERATIONS_PER_10_MINUTES:
                points = points + self.POINTS_PER_MAX_TIME_INTL_OPS
        if transaction_type == "transfer":
            if self.evaluate_new_account_transfer(transaction=transaction):
                points = points + self.POINTS_PER_NEW_ACCOUTS_TRANSFER
        if points <= self.LOW_RISK_TRESHOLD:
            return 'LOW'
        if self.LOW_RISK_TRESHOLD < points <= self.MED_RISK_TRESHOLD:
            return 'MEDIUM'
        if points > self.MED_RISK_TRESHOLD:
            return 'HIGH'
            





        

    def evaluate_max_per_10_min_ops(self, client_id: str)->int:
        """Pass audit log throught constructor"""
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        client_log = self._audit_log.get_client_transaction_history(client_id)
        current_time = datetime.now()
        time_10_min_ago = current_time - timedelta(minutes=10)
        num_of_transaction = 0
        
        for transaction_note in client_log:
            if transaction_note["Processing_time"] is not None:
                if transaction_note["Processing_time"] > time_10_min_ago and transaction_note["Processing_time"] < current_time and transaction_note['Transaction_type'] != 'deposit' and transaction_note['Sender'] == client_id:
                    num_of_transaction += 1
        return num_of_transaction



    def evaluate_large_sum_transfer(self, transaction: "Transactions.Transaction") -> bool:
        transaction_type = transaction._transaction_type
        if transaction_type == "transfer" or transaction_type == "withdraw":
                if self._bank_obj._all_bank_accounts[transaction._sender_acc_id]._currency != transaction._currency:
                    withdrow_amount = self._cur_converter.convert(amount=transaction._amount, from_currency=transaction._currency, to_currency=self._bank_obj._all_bank_accounts[transaction._sender_acc_id]._currency)
                    threshold = self._bank_obj._all_bank_accounts[transaction._sender_acc_id]._balance * self.LARGE_AMOUNT_AS_PERCENT_OF_BALANCE
                    if withdrow_amount > threshold:
                        return True
                    else:
                        return False
                else:
                    threshold = self._bank_obj._all_bank_accounts[transaction._sender_acc_id]._balance * self.LARGE_AMOUNT_AS_PERCENT_OF_BALANCE
                    if transaction._amount > threshold:
                        return True
                    else:
                        return False
        else:
            return False 

        


    def evaluate_new_account_transfer(self, transaction: "Transactions.Transaction")->bool:
        '''check wether current transfer to new acc or not'''
        history_acc_transfers = []
        if transaction._transaction_type == 'transfer':
            client_id = transaction._sender_id
            client_log = self._audit_log.get_client_transaction_history(client_id=client_id)        
            for transaction_note in client_log:
                if transaction_note['Transaction_type'] == 'transfer' and transaction_note['Transaction status'] == 'completed' and  transaction_note['Sender'] == client_id:
                    history_acc_transfers.append(transaction_note['Recipient_acc_id'])
        else:
            return False

        if history_acc_transfers:
            if transaction._recipient_acc_id in history_acc_transfers:
                return False
            else:
                return True
        else:
            return True




