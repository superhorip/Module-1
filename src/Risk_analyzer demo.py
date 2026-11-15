
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import Bank as Bank
import Bank_Account_class as BA
import Transactions as T
from Risk_analyzer import AuditLog, RiskAnalyzer


# Создаём банк, клиентов и счета
bank = Bank.Bank()

clients = {}
accounts = {}

for name in ("Alice", "Bob", "Charlie", "Dave"):
    clients[name] = bank.add_client(
        name=name, surname="Smith",
        age=30, phone_number="111111"
    )
    accounts[name] = bank.open_account(
        client_id=clients[name],
        account_type=BA.BankAccount,
        currency="RUB"
    )

bank.deposit(
    client_id=clients["Alice"],
    amount=10000,
    acccount_uuid=accounts["Alice"]
)


def create_transfer(recipient, amount):
    return T.Transaction(
        bank_object=bank,
        transaction_type="transfer",
        currency="RUB",
        amount=amount,
        sender_id=clients["Alice"],
        sender_acc_id=accounts["Alice"],
        recipient_id=clients[recipient],
        recipient_acc_id=accounts[recipient]
    )


def create_withdraw(amount):
    return T.Transaction(
        bank_object=bank,
        transaction_type="withdraw",
        currency="RUB",
        amount=amount,
        sender_id=clients["Alice"],
        sender_acc_id=accounts["Alice"]
    )


with TemporaryDirectory() as folder:
    filename = str(Path(folder) / "audit.json")

    log = AuditLog(filename)
    converter = T.CurrencyConverter()
    analyzer = RiskAnalyzer(log, bank, converter)
    processor = T.TransactionProcessor()
    queue = T.TransactionQueue()

    def process(description, transaction, expected_risk, expected_status):
        queue.add_transaction(transaction_obj=transaction, prioprity="2")

        processor.make_transaction(
            transaction_queue=queue,
            bank_obj=bank,
            currency_convertr=converter,
            risk_analyser=analyzer
        )

        audit_note = log._audit_log[-1]
        risk = audit_note["risk_level"]

        print(f"{description:30} {risk:7} {transaction._status}")

        assert risk == expected_risk
        assert transaction._status == expected_status
        assert audit_note["Transaction status"] == expected_status
        assert audit_note["Transation ID"] == transaction._id
        assert len(queue._transaction_queue) == 0

    # 1. Обычный перевод: новый счёт +20 = LOW
    process(
        "Обычный перевод",
        create_transfer("Bob", 100),
        "LOW",
        "completed"
    )

    # 2. Крупный перевод: сумма +30, новый счёт +20 = MEDIUM
    process(
        "Крупный перевод",
        create_transfer("Charlie", 5500),
        "MEDIUM",
        "completed"
    )

    # 3. Пять реальных операций через процессор
    print("\n--- Проверка частоты операций ---")

    for i in range(5):
        process(
            f"Снятие №{i + 1}",
            create_withdraw(100),
            "LOW",
            "completed"
        )

    count = analyzer.evaluate_max_per_10_min_ops(clients["Alice"])

    print(f"Операций за 10 минут: {count}")
    assert count >= 5

    # 4. HIGH: сумма +30, частота +20, новый счёт +20
    print("\n--- Проверка блокировки HIGH ---")

    alice_balance_before = bank._all_bank_accounts[accounts["Alice"]]._balance
    dave_balance_before = bank._all_bank_accounts[accounts["Dave"]]._balance

    process(
        "Подозрительный перевод",
        create_transfer("Dave", 6000),
        "HIGH",
        "failed"
    )

    alice_balance_after = bank._all_bank_accounts[accounts["Alice"]]._balance
    dave_balance_after = bank._all_bank_accounts[accounts["Dave"]]._balance

    assert alice_balance_before == alice_balance_after
    assert dave_balance_before == dave_balance_after
    assert log._audit_log[-1]["Failure reason"] == "High risk transaction"

    print("PASS: HIGH заблокирован, балансы не изменились")

    # 5. Статистика ошибок
    print("\n--- Статистика ошибок ---")

    failed_count, failure_reasons = log.make_failures_count()

    print(f"Количество ошибок: {failed_count}")
    print(f"Причины: {failure_reasons}")

    assert failed_count == 1
    assert failure_reasons["High risk transaction"] == 1

    # 6. Проверка сохранения и загрузки JSON
    print("\n--- Проверка AuditLog ---")

    restored_log = AuditLog(filename)
    history = restored_log.get_client_transaction_history(clients["Alice"])

    assert len(history) == 8
    assert all(
        isinstance(t["Processing_time"], datetime)
        for t in history
    )

    completed = sum(
        t["Transaction status"] == "completed"
        for t in history
    )

    failed = sum(
        t["Transaction status"] == "failed"
        for t in history
    )

    assert completed == 7
    assert failed == 1

    print(f"Восстановлено из JSON: {len(history)}")
    print(f"Успешных: {completed}, отклонённых: {failed}")

    print("\nPASS: все интеграционные проверки пройдены")
