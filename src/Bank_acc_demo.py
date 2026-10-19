
import Bank_Account_class as BA


# ==========================================
# DAY 1 - BASIC BANK ACCOUNT
# ==========================================

print('========== DAY 1 DEMONSTRATION ==========')

# Creating accounts

print('\nCreating accounts')

frozen_acc = BA.BankAccount(name='John', surname='Doe', status='frozen')
new_acc = BA.BankAccount(name='Paul', surname='McCartney', status='active')

print(frozen_acc)
print(new_acc)


# Frozen account - deposit is not allowed

print('\nTrying to deposit 200 into frozen account')

try:
    frozen_acc.deposit(200)
except BA.AccountFrozenError as e:
    print(f'Operation failed: {e}')

print(frozen_acc)


# Normal deposit

print('\nDepositing 150 into active account')

try:
    new_acc.deposit(150)
except (BA.AccountClosedError, BA.AccountFrozenError, ValueError, TypeError) as e:
    print(f'Operation failed: {e}')

print(new_acc)


# Negative deposit

print('\nTrying to deposit negative amount')

try:
    new_acc.deposit(-150)
except ValueError as e:
    print(f'Operation failed: {e}')

print(new_acc)


# Withdrawal exceeds balance

print('\nTrying to withdraw 500 (balance = 150)')

try:
    new_acc.withdraw(500)
except BA.InsufficientFundsError as e:
    print(f'Operation failed: {e}')

print(new_acc)


# Normal withdrawal

print('\nWithdrawing 110')

try:
    new_acc.withdraw(110)
except BA.InsufficientFundsError as e:
    print(f'Operation failed: {e}')

print(new_acc)


# Account information

print('\nBank account information:')
print(new_acc.get_account_info())


# ==========================================
# DAY 2 - INHERITANCE
# ==========================================

print('\n========== DAY 2 DEMONSTRATION ==========')

# Creating accounts

print('\nCreating accounts')

savings_acc = BA.SavingsAccount(name='Paul', surname='McCartney', status='active', min_balance=50, month_interest=5, currency='USD')
premium_acc = BA.PremiumAccount(name='Peter', surname='Parker', status='active', overdraft_limit=150, bank_fee=5, withdrawal_limit=200, currency='USD')
investment_acc = BA.InvestmentAccount(name='Tony', surname='Stark', status='active', currency='USD')

print(savings_acc)
print(premium_acc)
print(investment_acc)


# ==========================================
# SAVINGS ACCOUNT
# ==========================================

print('\n========== SAVINGS ACCOUNT ==========')

# Deposit money

print('\nDepositing 200 USD')

savings_acc.deposit(200)
print(savings_acc)


# Normal withdrawal

print('\nWithdrawing 100 USD')

savings_acc.withdraw(100)
print(savings_acc)


# Monthly interest: 5% of 100 = 5 USD

print('\nApplying monthly interest')

savings_acc.apply_month_interest()
print(savings_acc)


# Trying to withdraw below minimum balance

print('\nTrying to withdraw 100 USD (minimum balance = 50)')

try:
    savings_acc.withdraw(100)
except BA.InvalidOperationError as e:
    print(f'Operation failed: {e}')

print(savings_acc)


# Account information

print('\nSavings account information:')
print(savings_acc.get_account_info())


# ==========================================
# PREMIUM ACCOUNT
# ==========================================

print('\n========== PREMIUM ACCOUNT ==========')

# Deposit money

print('\nDepositing 100 USD')

premium_acc.deposit(100)
print(premium_acc)


# Withdrawal with bank fee and overdraft
# Balance: 100 - 180 - 5 = -85

print('\nWithdrawing 180 USD with 5 USD bank fee')

premium_acc.withdraw(180)
print(premium_acc)


# Trying to exceed withdrawal limit

print('\nTrying to withdraw 300 USD (withdrawal limit = 200)')

try:
    premium_acc.withdraw(300)
except BA.InvalidOperationError as e:
    print(f'Operation failed: {e}')

print(premium_acc)


# Trying to exceed overdraft limit

print('\nTrying to withdraw 100 USD (overdraft limit = 150)')

try:
    premium_acc.withdraw(100)
except BA.InvalidOperationError as e:
    print(f'Operation failed: {e}')

print(premium_acc)


# Account information

print('\nPremium account information:')
print(premium_acc.get_account_info())


# ==========================================
# INVESTMENT ACCOUNT
# ==========================================

print('\n========== INVESTMENT ACCOUNT ==========')

# Deposit money

print('\nDepositing 1000 USD')

investment_acc.deposit(1000)
print(investment_acc)


# Buying assets

print('\nBuying stocks for 300 USD')
investment_acc.buy_any_asset('stocks', 300)

print('\nBuying bonds for 200 USD')
investment_acc.buy_any_asset('bonds', 200)

print('\nBuying ETF for 100 USD')
investment_acc.buy_any_asset('etf', 100)

print(investment_acc)


# Selling assets

print('\nSelling stocks for 50 USD')

investment_acc.sell_any_asset('stocks', 50)
print(investment_acc)


# Trying to buy more assets than available cash

print('\nTrying to buy stocks for 1000 USD')

try:
    investment_acc.buy_any_asset('stocks', 1000)
except BA.InsufficientFundsError as e:
    print(f'Operation failed: {e}')

print(investment_acc)


# Trying to sell more assets than available

print('\nTrying to sell bonds for 500 USD')

try:
    investment_acc.sell_any_asset('bonds', 500)
except BA.InsufficientFundsError as e:
    print(f'Operation failed: {e}')

print(investment_acc)


# Trying to buy an unknown asset

print('\nTrying to buy crypto')

try:
    investment_acc.buy_any_asset('crypto', 50)
except BA.InvalidOperationError as e:
    print(f'Operation failed: {e}')

print(investment_acc)


# Projecting yearly growth

print('\nCalculating projected yearly growth')

growth_rates = {'stocks': 10, 'bonds': 4, 'etf': 7}

projected_growth = investment_acc.project_yearly_growth(growth_rates)

print(f'Projected yearly growth: {projected_growth} USD')

# Expected:
# Stocks: 250 * 10% = 25
# Bonds: 200 * 4% = 8
# ETF: 100 * 7% = 7
# Total: 40 USD


# Withdrawing available cash

print('\nWithdrawing 100 USD from investment account')

investment_acc.withdraw(100)
print(investment_acc)


# Account information

print('\nInvestment account information:')
print(investment_acc.get_account_info())


# ==========================================
# FINAL RESULTS
# ==========================================

print('\n========== FINAL RESULTS ==========')

print('Day 1:')
print(frozen_acc)
print(new_acc)

print('\nDay 2:')
print(savings_acc)
print(premium_acc)
print(investment_acc)

print('\nDemonstration finished')
