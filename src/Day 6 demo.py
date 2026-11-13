from collections import Counter
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import Bank as Bank
import Bank_Account_class as BA
import Transactions as Transactions
import Risk_analyzer as Risk


# 1. Банк, 6 клиентов и 12 счетов
bank_obj = Bank.Bank()
clients = {}
accounts = {}

people = [
    ('Alice', 'Brown'), ('Bob', 'Smith'), ('Charlie', 'Green'),
    ('Diana', 'White'), ('Eve', 'Black'), ('Frank', 'Taylor')
]

for number, (name, surname) in enumerate(people, 1):
    client_id = bank_obj.add_client(
        name=name, surname=surname, age=25 + number,
        phone_number=f'555000{number}'
    )
    clients[name] = client_id
    accounts[name] = [
        bank_obj.open_account(client_id=client_id, account_type=BA.BankAccount, currency='RUB'),
        bank_obj.open_account(
            client_id=client_id, account_type=BA.PremiumAccount, currency='USD',
            overdraft_limit=200, bank_fee=1, withdrawal_limit=1000
        )
    ]

# Начальные балансы нужны для симуляции; в 40 транзакций они не входят
for name, client_id in clients.items():
    bank_obj.deposit(client_id=client_id, amount=20000, acccount_uuid=accounts[name][0])
    bank_obj.deposit(client_id=client_id, amount=500, acccount_uuid=accounts[name][1])

queue = Transactions.TransactionQueue()
processor = Transactions.TransactionProcessor()
converter = Transactions.CurrencyConverter()


def create_transaction(kind, sender=None, recipient=None, amount=100, currency='RUB', sender_account=0, recipient_account=0):
    params = dict(bank_object=bank_obj, transaction_type=kind, currency=currency, amount=amount)
    if sender is not None:
        params.update(sender_id=clients[sender], sender_acc_id=accounts[sender][sender_account])
    if recipient is not None:
        params.update(recipient_id=clients[recipient], recipient_acc_id=accounts[recipient][recipient_account])
    return Transactions.Transaction(**params)


# 2. 40 транзакций: 12 пополнений, 12 переводов,  10 снятий, 4 ошибки недостатка средств и 2 HIGH-перевода
cases = []

for name in clients:
    cases.append((f'{name}: пополнение RUB', '1', create_transaction('deposit', recipient=name, amount=300)))
    cases.append((f'{name}: пополнение USD', '1', create_transaction('deposit', recipient=name, amount=20, currency='USD', recipient_account=1)))

names = list(clients)
for i in range(12):
    sender = names[i % 6]
    recipient = names[(i + 1 + i // 6) % 6]
    cases.append((f'{sender} -> {recipient}', '2', create_transaction('transfer', sender=sender, recipient=recipient, amount=250 + i * 25)))

for i in range(10):
    name = 'Alice' if i < 5 else names[i - 4]
    cases.append((f'{name}: снятие RUB', '3', create_transaction('withdraw', sender=name, amount=50)))

for name in names[:4]:
    cases.append((f'{name}: недостаточно средств', '2', create_transaction('withdraw', sender=name, amount=1_000_000)))

for recipient in ('Eve', 'Frank'):
    cases.append((f'Alice -> {recipient}: подозрительный перевод', '2', create_transaction('transfer', sender='Alice', recipient=recipient, amount=15000)))

assert len(cases) == 40


# 3. Очередь, обработка, повторные попытки и аудит
with TemporaryDirectory() as folder:
    file_name = str(Path(folder) / 'day6_audit.json')
    audit_log = Risk.AuditLog(file_name)
    risk_analyzer = Risk.RiskAnalyzer(audit_log, bank_obj, converter)

    print(f'Клиентов: {len(clients)} | Счетов: {len(bank_obj._all_bank_accounts)} | Транзакций: {len(cases)}')
    print('\n--- Очередь и выполнение ---')

    for number, (description, priority, transaction) in enumerate(cases, 1):
        queue.add_transaction(transaction_obj=transaction, prioprity=priority)
        print(f'{number:2}. В очереди: {description} (P{priority})')

        # В текущем TransactionProcessor HIGH не останавливает выполнение.
        # В демо блокируем его перед передачей процессору, без изменения модулей.
        risk = risk_analyzer.evaluate_transaction_risk(transaction)
        if risk == 'HIGH':
            queue.get_next_transaction()
            transaction._processing_time = datetime.now()
            transaction.change_transaction_status('processing')
            transaction._failure_reason = 'High risk: blocked'
            transaction.change_transaction_status('failed')
        else:
            # Процессор сам возвращает failed в очередь до MAX_RETRIES.
            # После каждого вызова забираем следующую попытку.
            while queue._transaction_queue:
                processor.make_transaction(
                    transaction_queue=queue, bank_obj=bank_obj,
                    currency_convertr=converter, risk_analyser=risk_analyzer
                )

        # Фиксируем окончательный результат один раз, после всех повторов.
        audit_log.add_transation_to_log(transaction, risk, file_name)
        print(f'    {transaction._status:9} | риск {risk:6} | попыток {transaction._retry_count} | {transaction._failure_reason or "OK"}')

    # 4. Статистика и пользовательские сценарии
    statuses = Counter(t._status for _, _, t in cases)
    risks = Counter(note['risk_level'] for note in audit_log._audit_log)

    print('\n--- Статистика транзакций ---')
    print('Всего:', len(cases), '| Завершено:', statuses['completed'], '| Отклонено:', statuses['failed'])
    print('Уровни риска:', dict(risks))
    print('Очередь после обработки:', len(queue._transaction_queue))

    print('\n--- Счета Alice ---')
    for account_id in accounts['Alice']:
        account = bank_obj._all_bank_accounts[account_id]
        print(f'{account_id}: {account.get_account_info()["type"]} | {account._balance:.2f} {account._currency}')

    print('\n--- История Alice ---')
    history = audit_log.get_client_transaction_history(clients['Alice'])
    for note in history:
        print(f'{note["Transaction_type"]:9} | {note["Amount"]:10g} {note["Currency"]} | {note["Transaction status"]:9} | {note["risk_level"]}')

    print('\n--- Подозрительные операции Alice ---')
    suspicious = audit_log.make_suspicious_operations_log(clients['Alice'])
    for note in suspicious:
        print(f'{note["Transation ID"][:8]} | {note["risk_level"]:6} | {note["Transaction status"]:9} | {note["Amount"]:g}')
    print('Профиль риска:', audit_log.make_client_risk_profile(clients['Alice']))

    print('\n--- Топ-3 клиентов по активам (метод Bank) ---')
    for place, (client_id, amount) in enumerate(bank_obj.get_clients_ranking()[:3], 1):
        name = next(name for name, cid in clients.items() if cid == client_id)
        print(f'{place}. {name}: {amount:.2f} (сумма чисел в разных валютах без конвертации)')

    print('\n--- Общий баланс по валютам ---')
    for currency, amount in bank_obj.get_total_balance().items():
        print(f'{currency}: {amount:.2f}')

    # 5. Проверка сохранения и восстановления JSON
    restored = Risk.AuditLog(file_name)
    assert len(restored._audit_log) == 40
    assert statuses['completed'] > 0 and statuses['failed'] > 0
    assert risks['HIGH'] > 0
    assert not queue._transaction_queue
    print('\nPASS: 40 транзакций, отчёты и загрузка JSON проверены')
