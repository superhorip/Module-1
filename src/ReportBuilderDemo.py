
from pathlib import Path
from tempfile import TemporaryDirectory
import json

import pandas as pd

import Bank as Bank
import Bank_Account_class as BA
import Transactions as T
import Risk_analyzer as Risk
from ReportBuilder import ReportBuilder


# 1. Создаём банк, 3 клиентов и 6 счетов

bank = Bank.Bank()

if not bank.check_allowed_time_interval():
    raise RuntimeError(
        'Демонстрация запускается в разрешённые банковские часы (05:00–23:59).'
    )

clients = {}
accounts = {}

for name, surname in [
    ('Alice', 'Brown'),
    ('Bob', 'Smith'),
    ('Charlie', 'Green')
]:
    client_id = bank.add_client(
        name=name,
        surname=surname,
        age=30,
        phone_number='123456'
    )

    clients[name] = client_id
    accounts[name] = {
        'RUB': bank.open_account(
            client_id, BA.BankAccount, currency='RUB'
        ),
        'USD': bank.open_account(
            client_id, BA.BankAccount, currency='USD'
        )
    }


# 2. Очередь, процессор и конвертер

queue = T.TransactionQueue()
processor = T.TransactionProcessor()
converter = T.CurrencyConverter()


with TemporaryDirectory() as folder:
    audit_path = str(Path(folder) / 'day7_audit.json')

    audit_log = Risk.AuditLog(audit_path)
    risk_analyzer = Risk.RiskAnalyzer(
        audit_log, bank, converter
    )

    # 3. Выполнение транзакций без повторных попыток

    def perform(
        kind, amount, currency,
        *,
        sender=None,
        recipient=None,
        sender_currency=None,
        recipient_currency=None
    ):
        transaction = T.Transaction(
            transaction_type=kind,
            bank_object=bank,
            amount=amount,
            currency=currency,
            sender_id=clients[sender] if sender else None,
            recipient_id=clients[recipient] if recipient else None,
            sender_acc_id=(
                accounts[sender][sender_currency]
                if sender else None
            ),
            recipient_acc_id=(
                accounts[recipient][recipient_currency]
                if recipient else None
            )
        )

        queue.add_transaction(
            transaction_obj=transaction,
            prioprity='1'
        )

        processor.make_transaction(
            transaction_queue=queue,
            bank_obj=bank,
            currency_convertr=converter,
            risk_analyser=risk_analyzer
        )

        assert transaction._status == 'completed', (
            f'{kind}: {transaction._status}, '
            f'{transaction._failure_reason}'
        )
        assert transaction._retry_count == 0
        assert not queue._transaction_queue

        return transaction


    # 4. Шесть начальных пополнений через TransactionProcessor

    starting_balances = {
        'Alice': {'RUB': 20000, 'USD': 1000},
        'Bob': {'RUB': 15000, 'USD': 700},
        'Charlie': {'RUB': 12000, 'USD': 600}
    }

    for name, amounts in starting_balances.items():
        for currency, amount in amounts.items():
            perform(
                'deposit',
                amount,
                currency,
                recipient=name,
                recipient_currency=currency
            )


    # 5. Ещё четыре транзакции

    # Крупный перевод Alice -> Bob (MEDIUM risk)
    perform(
        'transfer', 12000, 'RUB',
        sender='Alice',
        recipient='Bob',
        sender_currency='RUB',
        recipient_currency='RUB'
    )

    # Перевод Bob -> Charlie
    perform(
        'transfer', 2000, 'RUB',
        sender='Bob',
        recipient='Charlie',
        sender_currency='RUB',
        recipient_currency='RUB'
    )

    # Снятие Alice
    perform(
        'withdraw', 1000, 'RUB',
        sender='Alice',
        sender_currency='RUB'
    )

    # Межвалютный перевод USD -> RUB
    perform(
        'transfer', 50, 'USD',
        sender='Alice',
        recipient='Charlie',
        sender_currency='USD',
        recipient_currency='RUB'
    )


    # 6. Проверяем транзакции и аудит

    assert len(audit_log._audit_log) == 10

    assert len({
        note['Transation ID']
        for note in audit_log._audit_log
    }) == 10

    assert all(
        note['Transaction status'] == 'completed'
        for note in audit_log._audit_log
    )

    profile = audit_log.make_client_risk_profile(
        clients['Alice']
    )

    assert profile['Mid and high level ops number'] >= 1

    restored = Risk.AuditLog(audit_path)

    assert len(restored._audit_log) == 10
    assert [
        note['Transation ID'] for note in restored._audit_log
    ] == [
        note['Transation ID'] for note in audit_log._audit_log
    ]


    # 7. Генерируем отчёты и графики

    reports = ReportBuilder(bank, risk_analyzer)
    output_dir = reports._report_path

    reports.save_charts(clients['Alice'])

    reports.make_balance_graph(
        clients['Alice'],
        accounts['Alice']['RUB']
    )

    reports.export_to_csv(clients['Alice'])
    reports.export_to_json(clients['Alice'])


    # 8. Проверяем создание файлов

    patterns = [
        f'client_balance_{clients["Alice"]}_*.png',
        'Bank_*.png',
        f'client_risk_profile_{clients["Alice"]}_*.png',
        f'balance_{accounts["Alice"]["RUB"]}_*.png',
        f'Client_csv_balance_{clients["Alice"]}_*.csv',
        f'Client_json_balance_{clients["Alice"]}_*.json'
    ]

    files = []

    for pattern in patterns:
        candidates = list(output_dir.glob(pattern))

        assert candidates, f'Файл не найден: {pattern}'

        path = max(
            candidates,
            key=lambda p: p.stat().st_mtime_ns
        )

        assert path.stat().st_size > 0, (
            f'Пустой файл: {path}'
        )

        files.append(path)


    # 9. Проверяем содержимое CSV и JSON

    expected_balance = bank.get_total_balance(
        clients['Alice'],
        all_bank_clients=False
    )

    with open(files[5], encoding='utf-8') as file:
        assert json.load(file) == expected_balance

    csv_row = pd.read_csv(files[4]).iloc[0]

    for currency, balance in expected_balance.items():
        assert csv_row[currency] == balance


    # 10. Проверяем историю баланса Alice в RUB

    rub_history = [
        note.get('Sender_balance_after')
        if note['Sender_acc_id'] == accounts['Alice']['RUB']
        else note.get('Recipient_balance_after')
        for note in audit_log.get_client_transaction_history(
            clients['Alice']
        )
        if note['Transaction status'] == 'completed'
        and accounts['Alice']['RUB'] in (
            note['Sender_acc_id'],
            note['Recipient_acc_id']
        )
    ]

    assert rub_history == [20000, 7880, 6880], rub_history


    # 11. Результаты демонстрации

    print('\n=== DAY 7: REPORTBUILDER DEMO ===')
    print('Клиентов: 3 | Счетов: 6 | Транзакций: 10')
    print('Повторных попыток: 0')
    print('Риск-профиль Alice:', profile)
    print('Баланс Alice:', expected_balance)
    print('История Alice RUB:', rub_history)

    print('\nСозданные отчёты:')
    for path in files:
        print(path)

    print('\nPASS: 4 PNG, CSV и JSON сохранены и проверены')
