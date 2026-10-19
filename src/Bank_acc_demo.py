import Bank_Account_class as BA

print ('Creating accs')
frozen_acc = BA.BankAccount(name='John', surname='Doe', status='frozen' )
new_acc = BA.BankAccount(name='PAul', surname='McCurtney', status='active' )
savings_acc = BA.SavingsAccount(name='PAul', surname='McCurtney', status='active', min_balance=14, month_interest=5, currency='USD' )
premium_acc = BA.PremiumAccount(name='Peter', surname='Parker', status='active', overdraft_limit=150, currency='USD' )


# Заморежнный акк

print(frozen_acc)
print(new_acc)
print(savings_acc)
print(premium_acc)




try:
    frozen_acc.deposit(200)
except BA.AccountFrozenError as e:
    print (f'Operation falied: {e}')



try:
    new_acc.deposit(150)
except BA.InvalidOperationError as e:
    print (f'Operation falied: {e}')

#print(new_acc)

#отрицательная сумма 
try:
    new_acc.deposit(-150)
except BA.InvalidOperationError as e:
    print (f'Operation falied: {e}')

#print(new_acc)

#Снимаем больше чем есть на счете 
try:
    new_acc.withdraw(500)
except BA.InsufficientFundsError as e:
    print (f'Operation falied: {e}')

#print(new_acc)

#Снимаем норм 
try:
    new_acc.withdraw(110)
except BA.InsufficientFundsError as e:
    print (f'Operation falied: {e}')

#print(new_acc)

