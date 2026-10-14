import Bank_Account_class as BA

frozen_acc = BA.BankAccount(name='John', surname='Doe', status='frozen' )
new_acc = BA.BankAccount(name='PAul', surname='McCurtney', status='active' )

# Заморежнный акк
try:
    frozen_acc.deposit(200)
except BA.AccountFrozenError as e:
    print (f'Operation falied: {e}')

# Нормальнывй акк
print(new_acc)

try:
    new_acc.deposit(150)
except BA.InvalidOperationError as e:
    print (f'Operation falied: {e}')

print(new_acc)

#отрицательная сумма 
try:
    new_acc.deposit(-150)
except BA.InvalidOperationError as e:
    print (f'Operation falied: {e}')

print(new_acc)

#Снимаем больше чем есть на счете 
try:
    new_acc.withdraw(500)
except BA.InsufficientFundsError as e:
    print (f'Operation falied: {e}')

print(new_acc)

#Снимаем норм 
try:
    new_acc.withdraw(110)
except BA.InsufficientFundsError as e:
    print (f'Operation falied: {e}')

print(new_acc)

