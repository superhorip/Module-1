import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import Bank as Bank
import Bank_Account_class as BA
import Transactions as T
from Risk_analyzer import AuditLog, RiskAnalyzer


class ReportBuilder():

    def __init__(self, bank_obj: "Bank.Bank", risk_analyzer_obj: "RiskAnalyzer"):
        if not isinstance (bank_obj, Bank.Bank):
            raise BA.InvalidOperationError('Wrong Object')
        if not isinstance (risk_analyzer_obj, RiskAnalyzer):
            raise BA.InvalidOperationError('Wrong Object')        
        self._bank_obj = bank_obj
        self._risk_analyzer_obj = risk_analyzer_obj
        report_dir = 'reports'
        report_path = Path(report_dir)
        if not report_path.is_dir():
            report_path.mkdir()
        self._report_path = report_path



    def save_charts(self, client_id: str) -> None:
        BA.validate_string(string=client_id, field_name='client_ id')
        '''Будет делать стобчатый график, сколько денег на счетах у пользователя 
        на основе Bank.get_total_balance каждый столбец в единицах той валюты которой он есть
        снизу подпись с названием валюты'''
        client_balance = self._bank_obj.get_total_balance(client_id, all_bank_clients=False)
        currencies = ['RUB', 'USD', 'EUR', 'KZT', 'CNY']
        balances = [client_balance.get(currency, 0) for currency in currencies]
        plt.figure(figsize=(8, 5))
        plt.bar(currencies, balances)
        plt.title(f'Client balances: {client_id}')
        plt.xlabel('Currency')
        plt.ylabel('Amount')
        plt.tight_layout()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'client_balance_{client_id}_{timestamp}.png'
        file_path = self._report_path / file_name
        plt.savefig(file_path)
        plt.close()

        '''Будет делать толкчатую диаграмму. на основе Bank.get_total_balance по всему банку
        сколько там денег. в банке аждый столбец в единицах той валюты которой он есть
        снизу подпись с названием валюты'''
        bank_balance = self._bank_obj.get_total_balance(all_bank_clients=True)
        currencies = ['RUB', 'USD', 'EUR', 'KZT', 'CNY']
        balances = [bank_balance.get(currency, 0) for currency in currencies]
        plt.figure(figsize=(8, 5))
        plt.bar(currencies, balances)
        plt.title(f'Client balances: {client_id}')
        plt.xlabel('Currency')
        plt.ylabel('Amount')
        plt.tight_layout()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'Bank_{timestamp}.png'
        file_path = self._report_path / file_name
        plt.savefig(file_path)
        plt.close()

        '''Будет рисовать, сколько операций медиум и хай and low. На круговой диаграмме. на 
        основе Risk.analyzermake_suspicious_operations_log'''
        risks_stat = self._risk_analyzer_obj._audit_log.make_client_risk_profile(client_id=client_id)
        if risks_stat['Total ops number'] == 0:
            return
        # {'Total ops number': len(client_transactions), 'Mid and high level ops number': medium_and_high_risk_ops}
        low_risk_transactions_number = risks_stat['Total ops number'] - risks_stat['Mid and high level ops number']
        labels = ['Low risk transaction number', 'High and medium risk transaction number']
        sizes = [low_risk_transactions_number, risks_stat['Mid and high level ops number']]
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'client_risk_profile_{client_id}_{timestamp}.png'
        file_path = self._report_path / file_name
        plt.savefig(file_path)
        plt.close(fig=fig)        


    def make_balance_graph(self, client_id: str, account_id: str) -> None:
        BA.validate_string(string=client_id, field_name='Client ID')
        BA.validate_string(string=account_id, field_name='Account ID')

        Bank.validate_account_to_client_id(
            client_id=client_id,
            accountt_uuid=account_id,
            bank_object=self._bank_obj
        )

        transactions = self._risk_analyzer_obj._audit_log.get_client_transaction_history(client_id)

        balances = []

        for transaction in transactions:
            if transaction['Transaction status'] != 'completed':
                continue

            if transaction['Sender_acc_id'] == account_id:
                balance = transaction.get('Sender_balance_after')
            elif transaction['Recipient_acc_id'] == account_id:
                balance = transaction.get('Recipient_balance_after')
            else:
                continue

            if balance is not None:
                balances.append(balance)

        if not balances:
            return

        steps = range(1, len(balances) + 1)

        fig, ax = plt.subplots()
        ax.plot(steps, balances, marker='o')
        ax.set_xlabel('Transaction number')
        ax.set_ylabel('Balance')
        ax.set_title(f'Balance history: {account_id}')
        ax.grid(True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'balance_{account_id}_{timestamp}.png'
        file_path = self._report_path / file_name

        fig.savefig(file_path)
        plt.close(fig)

        

    def export_to_csv(self, client_id: str) -> None:
        ''' saves report bout user accounts funds to '''
        BA.validate_string(string=client_id, field_name='client_ id')
        client_balance = self._bank_obj.get_total_balance(client_id, all_bank_clients=False)
        currencies = ['RUB', 'USD', 'EUR', 'KZT', 'CNY']
        balances = [client_balance.get(currency, 0) for currency in currencies]        
        df = pd.DataFrame(data=[balances], columns=currencies)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'Client_csv_balance_{client_id}_{timestamp}.csv'
        df.to_csv(self._report_path / file_name)


    def export_to_json(self, client_id: str) -> None:
        ''' saves report bout user accounts funds to json'''
        BA.validate_string(string=client_id, field_name='client_ id')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        client_balance = self._bank_obj.get_total_balance(client_id, all_bank_clients=False)
        file_name = f'Client_json_balance_{client_id}_{timestamp}.json'        
        with open(self._report_path / file_name, 'w', encoding='utf-8') as file:
            json.dump(client_balance, file, indent=4, default=str)            
