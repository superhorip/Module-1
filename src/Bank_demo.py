
import Bank_Account_class as BA
import Bank as Bank

my_bank = Bank.Bank()

client_1_id = my_bank.add_client(name='John', surname='Doe', phone_number='88888', age=29)
client_2_id = my_bank.add_client(name='John', surname='Stark', phone_number='88888', age=23)
client_3_id = my_bank.add_client(name='Jake', surname='Smerd', phone_number='88888', age=35)

client_1_acc1 = my_bank.open_account(client_id=client_1_id, account_type=BA.PremiumAccount, currency='RUB')
client_1_acc2 = my_bank.open_account(client_id=client_1_id, account_type=BA.PremiumAccount, currency='USD')
client_1_acc3 = my_bank.open_account(client_id=client_1_id, account_type=BA.InvestmentAccount, currency='USD')
client_2_acc1 = my_bank.open_account(client_id=client_2_id, account_type=BA.PremiumAccount, currency='RUB')
client_2_acc2 = my_bank.open_account(client_id=client_2_id, account_type=BA.PremiumAccount, currency='USD')

client_3_acc1 = my_bank.open_account(client_id=client_2_id, account_type=BA.PremiumAccount, currency='RUB')
client_3_acc2 = my_bank.open_account(client_id=client_2_id, account_type=BA.PremiumAccount, currency='USD')




my_bank._all_bank_accounts[client_1_acc1].deposit(1000)
my_bank.deposit(client_id=client_1_id, acccount_uuid=client_1_acc1, amount=1000)
my_bank.deposit(client_id=client_1_id, acccount_uuid=client_1_acc2, amount=200)
my_bank.deposit(client_id=client_1_id, acccount_uuid=client_1_acc3, amount=540)

my_bank.deposit(client_id=client_2_id, acccount_uuid=client_2_acc1, amount=700)
my_bank.deposit(client_id=client_2_id, acccount_uuid=client_2_acc2, amount=700)

my_bank.deposit(client_id=client_3_id, acccount_uuid=client_3_acc1, amount=700)
my_bank.deposit(client_id=client_3_id, acccount_uuid=client_3_acc2, amount=700)

print(my_bank.get_total_balance())

print(my_bank.search_accounts(name="John", surname='Doe'))
print(my_bank.search_accounts(name="John", surname='Doez'))


# ==========================================
# 1. Проверка балансов
# ==========================================

print('\n--- TOTAL BALANCE ---')

print('All clients:')
print(my_bank.get_total_balance())

print('Client 1:')
print(my_bank.get_total_balance(client_1_id, all_bank_clients=False))

print('Client 1 and Client 2:')
print(my_bank.get_total_balance(client_1_id, client_2_id, all_bank_clients=False))


# ==========================================
# 2. Рейтинг клиентов
# ==========================================

print('\n--- CLIENTS RANKING ---')

print('All clients:')
print(my_bank.get_clients_ranking())

print('Client 1 and Client 3:')
print(my_bank.get_clients_ranking(client_1_id, client_3_id, all_bank_clients=False))


# ==========================================
# 3. Поиск счетов
# ==========================================

print('\n--- SEARCH ACCOUNTS ---')

print(my_bank.search_accounts(name='John', surname='Doe'))
print(my_bank.search_accounts(name='John', surname='Stark'))
print(my_bank.search_accounts(name='Jake', surname='Smerd'))
print(my_bank.search_accounts(name='John', surname='Doez'))


# ==========================================
# 4. Заморозка и разморозка счетов
# ==========================================

print('\n--- FREEZE / UNFREEZE ---')

print('Before freezing:')
print(my_bank._all_bank_accounts[client_1_acc1]._account_status)

my_bank.freeze_account(client_id=client_1_id, uuid_of_acc_to_freeze=client_1_acc1)

print('After freezing:')
print(my_bank._all_bank_accounts[client_1_acc1]._account_status)

my_bank.unfreeze_account(client_id=client_1_id, uuid_of_acc_to_unfreeze=client_1_acc1)

print('After unfreezing:')
print(my_bank._all_bank_accounts[client_1_acc1]._account_status)


# ==========================================
# 5. Закрытие счета
# ==========================================

print('\n--- CLOSE ACCOUNT ---')

print('Before closing:')
print(my_bank._all_bank_accounts[client_2_acc1]._account_status)

my_bank.close_account(client_id=client_2_id, uuid_of_acc_to_close=client_2_acc1)

print('After closing:')
print(my_bank._all_bank_accounts[client_2_acc1]._account_status)


# ==========================================
# 6. Попытка разморозить закрытый счет
# ==========================================

print('\n--- UNFREEZE CLOSED ACCOUNT ---')

try:
    my_bank.unfreeze_account(
        client_id=client_2_id,
        uuid_of_acc_to_unfreeze=client_2_acc1
    )
except BA.InvalidOperationError as e:
    print('Expected error:', e)


# ==========================================
# 7. Авторизация клиента
# ==========================================

print('\n--- AUTHENTICATION ---')

print('Before authentication:')
print(my_bank._all_clients[client_1_id].is_client_authentificated())

my_bank.authenticate_client(client_id=client_1_id, verification_passed=True)

print('After successful authentication:')
print(my_bank._all_clients[client_1_id].is_client_authentificated())


# ==========================================
# 8. Три неправильные попытки входа
# ==========================================

print('\n--- FAILED LOGIN ATTEMPTS ---')

my_bank.authenticate_client(client_id=client_3_id, verification_passed=False)
my_bank.authenticate_client(client_id=client_3_id, verification_passed=False)

try:
    my_bank.authenticate_client(client_id=client_3_id, verification_passed=False)
except BA.InvalidOperationError as e:
    print('Expected error:', e)

print('Client 3 blocked:')
print(my_bank._all_clients[client_3_id].is_client_blocked())

print('Number of failed attempts:')
print(my_bank._all_clients[client_3_id]._num_of_login_attempts)


# ==========================================
# 9. Попытка операции заблокированного клиента
# ==========================================

print('\n--- BLOCKED CLIENT OPERATION ---')

try:
    my_bank.open_account(
        client_id=client_3_id,
        account_type=BA.PremiumAccount,
        currency='RUB'
    )
except BA.InvalidOperationError as e:
    print('Expected error:', e)


# ==========================================
# 10. Журнал подозрительных действий
# ==========================================

print('\n--- SUSPICIOUS ACTIONS ---')

for action in my_bank._suspecious_actions:
    print(action)


# ==========================================
# 11. Проверка разрешенного времени
# ==========================================

print('\n--- ALLOWED TIME ---')

print(my_bank.check_allowed_time_interval())


# ==========================================
# 12. Проверка итогового состояния
# ==========================================

print('\n--- FINAL STATE ---')

print('Number of clients:', len(my_bank._all_clients))
print('Number of accounts:', len(my_bank._all_bank_accounts))

print('Client 1 accounts:')
print(my_bank._all_clients[client_1_id]._uuids)

print('Client 2 accounts:')
print(my_bank._all_clients[client_2_id]._uuids)

print('Client 3 accounts:')
print(my_bank._all_clients[client_3_id]._uuids)

print('Final ranking:')
print(my_bank.get_clients_ranking())



