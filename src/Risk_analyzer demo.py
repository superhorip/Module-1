
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import Bank as Bank
import Bank_Account_class as BA
import Transactions as T
from Risk_analyzer import AuditLog, RiskAnalyzer


# Создаём банк, клиентов и счета
bank = Bank.Bank()

alice = bank.add_client(name="Alice", surname="Brown", age=30, phone_number="111111")
bob = bank.add_client(name="Bob", surname="Smith", age=35, phone_number="222222")
charlie = bank.add_client(name="Charlie", surname="Green", age=40, phone_number="333333")

alice_acc = bank.open_account(
    client_id=alice, account_type=BA.BankAccount, currency="RUB"
)
bob_acc = bank.open_account(
    client_id=bob, account_type=BA.BankAccount, currency="RUB"
)
charlie_acc = bank.open_account(
    client_id=charlie, account_type=BA.BankAccount, currency="RUB"
)

bank.deposit(client_id=alice, amount=10000, acccount_uuid=alice_acc)


def transfer(recipient, account, amount):
    return T.Transaction(
        bank_object=bank,
        transaction_type="transfer",
        currency="RUB",
        amount=amount,
        sender_id=alice,
        sender_acc_id=alice_acc,
        recipient_id=recipient,
        recipient_acc_id=account
    )


def check(description, transaction, expected):
    result = analyzer.evaluate_transaction_risk(transaction)
    print(f"{description:32} {result:7} ожидалось: {expected}")
    assert result == expected, f"{description}: {result} != {expected}"


with TemporaryDirectory() as folder:
    filename = str(Path(folder) / "audit.json")

    log = AuditLog(filename)
    analyzer = RiskAnalyzer(log, bank, T.CurrencyConverter())

    # 1. Обычный перевод: новый счёт +20 = LOW
    check(
        "Обычный перевод",
        transfer(bob, bob_acc, 100),
        "LOW"
    )

    # 2. Крупный перевод: сумма +30, новый счёт +20 = MEDIUM
    check(
        "Крупный перевод",
        transfer(charlie, charlie_acc, 6000),
        "MEDIUM"
    )

    # 3. Создаём историю из пяти операций за последние 10 минут
    for _ in range(5):
        t = T.Transaction(
            bank_object=bank,
            transaction_type="withdraw",
            currency="RUB",
            amount=100,
            sender_id=alice,
            sender_acc_id=alice_acc
        )
        t._status = "completed"
        t._processing_time = datetime.now() - timedelta(seconds=1)

        log.add_transation_to_log(t, "LOW", filename)

    count = analyzer.evaluate_max_per_10_min_ops(alice)
    print(f"Операций за 10 минут: {count}")
    assert count == 5

    # 4. Сумма +30, частота +20, новый счёт +20 = HIGH
    check(
        "Подозрительный перевод",
        transfer(charlie, charlie_acc, 6000),
        "HIGH"
    )

    # 5. Проверяем восстановление журнала из JSON
    restored_log = AuditLog(filename)
    history = restored_log.get_client_transaction_history(alice)

    assert len(history) == 5
    assert all(
        isinstance(t["Processing_time"], datetime)
        for t in history
    )

    print(f"Записей восстановлено из JSON: {len(history)}")
    print("\nPASS: все проверки анализатора рисков пройдены")
