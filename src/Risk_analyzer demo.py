from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank
import Transactions
import Risk_analyzer

bank_obj = Bank.Bank()

alice = bank_obj.add_client(
    name="Alice", surname="Brown",
    age=30, phone_number="111111"
)

bob = bank_obj.add_client(
    name="Bob", surname="Smith",
    age=35, phone_number="222222"
)

charlie = bank_obj.add_client(
    name="Charlie", surname="Green",
    age=40, phone_number="333333"
)

risk_analyzer = Risk_analyzer.RiskAnalyzer()
# ============================================================
# 2. ОТКРЫВАЕМ СЧЕТА
# ============================================================

alice_rub = bank_obj.open_account(
    client_id=alice,
    account_type=BA.BankAccount,
    currency="RUB"
)

bob_usd = bank_obj.open_account(
    client_id=bob,
    account_type=BA.BankAccount,
    currency="USD"
)

charlie_rub = bank_obj.open_account(
    client_id=charlie,
    account_type=BA.PremiumAccount,
    currency="RUB",
    overdraft_limit=1000,
    bank_fee=2,
    withdrawal_limit=10000
)


# ============================================================
# 3. НАЧАЛЬНЫЕ БАЛАНСЫ
# ============================================================

bank_obj.deposit(
    client_id=alice, amount=10000,
    acccount_uuid=alice_rub
)

bank_obj.deposit(
    client_id=bob, amount=200,
    acccount_uuid=bob_usd
)

bank_obj.deposit(
    client_id=charlie, amount=500,
    acccount_uuid=charlie_rub
)

accounts = {
    "Alice RUB": alice_rub,
    "Bob USD": bob_usd,
    "Charlie RUB Premium": charlie_rub
}


def show_balances(title):
    print(f"\n--- {title} ---")

    for label, account_id in accounts.items():
        account = bank_obj._all_bank_accounts[account_id]

        print(
            f"{label:22} "
            f"{account._balance:12.2f} "
            f"{account._currency}"
        )


show_balances("Баланс до транзакций")

queue = Transactions.TransactionQueue()
processor = Transactions.TransactionProcessor()
converter = Transactions.CurrencyConverter()

#5. ДЕСЯТЬ ТЕСТОВЫХ ТРАНЗАКЦИЙ
# ============================================================

# Формат: описание, приоритет, параметры транзакции

cases = [(  "Alice: пополнение RUB", "1", dict(transaction_type="deposit", currency="RUB", amount=1000, recipient_id=alice, recipient_acc_id=alice_rub )),
    (
        "Bob: пополнение USD",
        "1",
        dict(
            transaction_type="deposit",
            currency="USD",
            amount=50,
            recipient_id=bob,
            recipient_acc_id=bob_usd
        )
    ),
    (
        "Charlie: пополнение USD на RUB-счёт",
        "1",
        dict(
            transaction_type="deposit",
            currency="USD",
            amount=10,
            recipient_id=charlie,
            recipient_acc_id=charlie_rub
        )
    ),
    (
        "Alice RUB -> Bob USD",
        "2",
        dict(
            transaction_type="transfer",
            currency="RUB",
            amount=900,
            sender_id=alice,
            sender_acc_id=alice_rub,
            recipient_id=bob,
            recipient_acc_id=bob_usd
        )
    ),
    (
        "Bob USD -> Alice RUB",
        "2",
        dict(
            transaction_type="transfer",
            currency="USD",
            amount=20,
            sender_id=bob,
            sender_acc_id=bob_usd,
            recipient_id=alice,
            recipient_acc_id=alice_rub
        )
    ),
    (
        "Charlie Premium -> Alice RUB",
        "2",
        dict(
            transaction_type="transfer",
            currency="RUB",
            amount=100,
            sender_id=charlie,
            sender_acc_id=charlie_rub,
            recipient_id=alice,
            recipient_acc_id=alice_rub
        )
    ),
    (
        "Alice: слишком большой перевод",
        "2",
        dict(
            transaction_type="transfer",
            currency="RUB",
            amount=1_000_000,
            sender_id=alice,
            sender_acc_id=alice_rub,
            recipient_id=charlie,
            recipient_acc_id=charlie_rub
        )
    ),
    (
        "Alice: снятие RUB",
        "3",
        dict(
            transaction_type="withdraw",
            currency="RUB",
            amount=150,
            sender_id=alice,
            sender_acc_id=alice_rub
        )
    ),
    (
        "Bob: снятие RUB с USD-счёта",
        "3",
        dict(
            transaction_type="withdraw",
            currency="RUB",
            amount=900,
            sender_id=bob,
            sender_acc_id=bob_usd
        )
    ),
    (
        "Charlie Premium: снятие RUB",
        "3",
        dict(
            transaction_type="withdraw",
            currency="RUB",
            amount=50,
            sender_id=charlie,
            sender_acc_id=charlie_rub
        )
    )
]


# ============================================================
# 6. СОЗДАЁМ ТРАНЗАКЦИИ И ДОБАВЛЯЕМ В ОЧЕРЕДЬ
# ============================================================

transactions = []

for description, priority, kwargs in cases:

    transaction = Transactions.Transaction(
        bank_object=bank_obj,
        **kwargs
    )

    transactions.append(
        (description, priority, transaction)
    )

    queue.add_transaction(
        transaction_obj=transaction,
        prioprity=priority
    )

print(f"\nСоздано транзакций: {len(transactions)}")
print(f"В очереди: {len(queue._transaction_queue)}")

# 7. ВЫПОЛНЯЕМ ТРАНЗАКЦИИ
# ============================================================

for number in range(len(transactions)):

    processor.make_transaction(
        transaction_queue=queue,
        bank_obj=bank_obj,
        currency_convertr=converter,
        risk_analyser=risk_analyzer
    )


# ============================================================
# 8. ВЫВОДИМ РЕЗУЛЬТАТЫ
# ============================================================

print("\n--- Результаты (в порядке создания) ---")

for number, (description, priority, transaction) in enumerate(
    transactions, 1
):

    print(f"{number:2}. P{priority} {description}")

    print(
        f"    {transaction._amount:g} "
        f"{transaction._currency} | "
        f"{transaction._status} | "
        f"комиссия {transaction._transfer_fee:g} | "
        f"ошибка: {transaction._failure_reason}"
    )


# ============================================================
# 9. ИТОГОВЫЕ БАЛАНСЫ И ПРОВЕРКИ
# ============================================================

show_balances("Баланс после транзакций")

completed = sum(
    t._status == "completed"
    for _, _, t in transactions
)

failed = sum(
    t._status == "failed"
    for _, _, t in transactions
)

print(
    f"\nИтого: {completed} completed, "
    f"{failed} failed, "
    f"в очереди {len(queue._transaction_queue)}"
)

assert len(transactions) == 10
assert completed == 9 and failed == 1
assert len(queue._transaction_queue) == 0

print("PASS: 10 транзакций обработаны, ожидаемые статусы получены")
