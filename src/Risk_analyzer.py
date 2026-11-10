from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime, timedelta

import Bank_Account_class as BA
import Bank as Bank
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import Transactions


class AuditLog:
    """
    Stores transaction history of every user/ saves to disk reads before strart
    """

    def __init__(
        self,
    ):
        # self.read_log_from_disk(file_name='log.txt')
        self._audit_log = []
        pass

    def add_transation_to_log(self, transaction: "Transactions.Transaction", risk_level: str) -> None:
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError("Wrong data type")
        if not isinstance(risk_level, str):
            raise BA.InvalidOperationError("Wrong type")
        transaction_dict = transaction.get_transaction_data()
        transaction_dict["risk_level"] = risk_level
        self._audit_log.append(transaction_dict)

    def get_client_transaction_history(self, client_id: str) -> list:
        """returns all transaction logs by client_id"""
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        user_transactions = []
        for transaction_note in self._audit_log:
            if transaction_note._sender_id == client_id:
                user_transactions.append(transaction_note)
        return user_transactions

    def make_client_risk_profile(self, client_id):
        """
        Общее количество операций.
        Количество операций с MEDIUM и HIGH.
        Количество заблокированных операций.
        Максимальный зафиксированный уровень риска.
        """

    pass

    def make_suspicious_operations_log(self) -> list:
        """Фильтрует журнал и возвращает транзакции с риском MEDIUM и HIGH."""
        pass

    def read_log_from_disk(self, file_name: str):
        """reads file"""
        pass

    def write_log_to_disk(self, file_name: str):
        """reads file"""
        pass


class RiskAnalyzer:
    VALID_RISKS_LEVELS = ("LOW", "MEDIUM", "HIGH")
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

    def __init__(self, audit_log: AuditLog, bank_obj: Bank.Bank):
        if not isinstance(audit_log, AuditLog):
            raise BA.InvalidOperationError("Wrong datatype")
        if not isinstance(bank_obj, Bank.Bank):
            raise BA.InvalidOperationError("Wrong data type")
        self._audit_log = audit_log
        self._bank_obj = bank_obj
        self._risk_level = "LOW"

    def evaluate_transaction_risk(self, transaction: "Transactions.Transaction") -> str:
        """
        #Evaluates risk level and return it to Transaction processor

        """
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError("Wrong data type")
        transaction_type = transaction._transaction_type
        if transaction_type == "transfer" or transaction_type == "withdraw":
            return "TEMP"

    def evaluate_max_per_10_min_ops(self, client_id: str):
        """Pass audit log throught constructor"""
        if not isinstance(client_id, str):
            raise BA.InvalidOperationError("Wrong type")
        client_log = self._audit_log.get_client_transaction_history(client_id)
        current_time = datetime.now()
        time_10_min_ago = current_time - timedelta(minutes=10)
        num_of_transaction = 0
        
        for transaction_note in client_log:
            if transaction_note["Processing_time"] is not None:
                if transaction_note["Processing_time"] > time_10_min_ago and transaction_note["Processing_time"] < current_time:
                    num_of_transaction += 1
        return num_of_transaction

    def evaluate_night_time(self):
        pass

    def evaluate_large_sum_transfer(self, transaction: "Transactions.Transaction") -> bool:
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError("Wrong data type")
        transaction_type = transaction._transaction_type
        if transaction_type == "transfer" or transaction_type == "withdraw":
            threshold = self._bank_obj._all_bank_accounts[transaction._sender_acc_id]._balance * self.LARGE_AMOUNT_AS_PERCENT_OF_BALANCE
            if transaction._amount > threshold:
                return True
            else:
                return False
        else:
            return False

    def evaluate_new_account_transfer(self, transaction: "Transactions.Transaction")->bool:
        if not isinstance(transaction, Transactions.Transaction):
            raise BA.InvalidOperationError("Wrong data type")

        history_acc_id = []
        client_log = self._audit_log.get_client_transaction_history(client_id)        
        for transaction_note in client_log:
            if transaction_note["Processing_time"] is not None:
                if transaction_note["Processing_time"] > time_10_min_ago and transaction_note["Processing_time"] < current_time:
                    num_of_transaction += 1
        return num_of_transaction        

        pass
