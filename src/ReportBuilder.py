#import pandas as pd
#from matplotlib import pyplot as plt
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import Bank as Bank
import Bank_Account_class as BA
import Transactions as T
from Risk_analyzer import AuditLog, RiskAnalyzer


class ReportBuilder():

    def __init__(self, bank_obj: Bank.Bank):
        if not isinstance (bank_obj, Bank.Bank):
            raise BA.InvalidOperationError('Wrong Object')
        self._bank_obj = bank_obj
        cur_dir = Path.cwd()
        report_dir = '/reports'
        report_path = Path(report_dir)
        if report_path.is_folder():
        

    def make_client_graph(self, client_id: str) -> None:
        '''Будет делать стобчатый график, сколько денег на счетах у пользователя 
        на основе Bank.get_total_balance каждый столбец в единицах той валюты которой он есть
        снизу подпись с названием валюты'''
        BA.validate_string(string=client_id, field_name='client_ id')
        client_balance = self._bank_obj.get_total_balance(client_id, all_bank_clients=False)


    def make_bank_graph(self):
        '''Будет делать толкчатую диаграмму. на основе Bank.get_total_balance по всему банку
        сколько там денег. в банке аждый столбец в единицах той валюты которой он есть
        снизу подпись с названием валюты'''
        bank_balance = self._bank_obj.get_total_balance(all_bank_clients=True)


    def make_risk_graph(self):
        '''Будет рисовать, сколько операций медиум и хай. На круговой диаграмме. на 
        основе Risk.analyzermake_suspicious_operations_log'''
        pass



    def make_balance_graph(self, currency: str):
        ''' рисует баланс счета по логу тразакций в выбранной валюте
        '''
        pass

    def save_report_to_files(self, client_id: str) -> None:
        ''' saves report bout user accounts funds to csv and json'''
