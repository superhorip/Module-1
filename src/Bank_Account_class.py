from abc import ABC, abstractmethod
from uuid import uuid4
import math

class InsufficientFundsError(Exception):
    pass

class AccountClosedError(Exception):
    pass

class AccountFrozenError(Exception):
    pass

class InvalidOperationError(Exception):
    pass




class AbstractAccount(ABC):
    VALID_STATUSES = ('active', 'frozen', 'closed')
    def __init__(self, name: str, surname: str, status: str = 'active'  )->None:
        self.name = name
        self.surname = surname
        self._balance = 0
        self._uuid = None
        if status not in self.VALID_STATUSES:
            raise ValueError("Wrong status while creating bank account")
        self._account_status = status
       
    @abstractmethod
    def deposit(self, amount:float)->None:
        if self._account_status == 'active':
            self._balance += amount
        else :
            raise ValueError("Account is not active. Deposition is not permitied")

    @abstractmethod
    def withdraw(self, amount:float = 0)->None:
        if self._account_status == 'active':
            self._balance -= amount
        else :
            raise ValueError("Account is not active. Withdrowal is not permitied")

    @abstractmethod
    def get_account_info(self)->dict:
        return {'name':self.name, 'surname':self.surname, 'status':self._account_status, 'balance':self._balance, 'uuid':self._uuid  }





class BankAccount(AbstractAccount):

    """Standart Bank account with deposit and withdrowal operations"""

    CURRENCIES = ('RUB', 'USD', 'EUR', 'KZT', 'CNY')
    def __init__(self, name: str, surname: str, uuid:str | None = None, status: str = 'active', currency:str ='RUB'   )->None:
        super().__init__(name=name, surname=surname, status=status)

        if (uuid == 0 or uuid is None):
            self._uuid = uuid4().hex[:12]
        else:
            self._uuid = uuid

        self.currency = currency
        if self.currency not in self.CURRENCIES:
            raise ValueError ("Wrong currencie  input while creating an account")
        
    def deposit(self, amount : float)->None:
        if self._account_status == 'closed':
            raise AccountClosedError('Closed account error')
        if self._account_status == 'frozen':
            raise AccountFrozenError('Frozen account error')
        if isinstance(amount, bool) or not isinstance(amount,(float, int)):
            raise TypeError('Amount should be int or float')
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')        
        if amount < 0:
            raise InvalidOperationError("Negative or zero amount error")
        super().deposit(amount = amount)


    def withdraw(self, amount : float)->None:
        if self._account_status == 'closed':
            raise AccountClosedError('Closed account error')
        if self._account_status == 'frozen':
            raise AccountFrozenError('Frozen account error')
        if isinstance(amount, bool) or not isinstance(amount,(float, int)):
            raise TypeError('Amount should be int or float')
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')
        if amount <= 0:
            raise InvalidOperationError("Negative or zero amount error")
        if self._balance < amount:
            raise InsufficientFundsError("Not enought funds error ")
        super().withdraw(amount = amount)
        
    def get_account_info(self)->dict:
        return {'name':self.name, 'surname':self.surname, 'type':'BankAccount','status':self._account_status, 'balance':self._balance, 'currency':self.currency,'uuid':str(self._uuid) }
    
    def __str__(self):
        return (f'Bank account, holder name: {self.surname}, {self.name}, uuid: {str(self._uuid)[-4:]}, status: {self._account_status}, type: {self.currency}, balance: {self._balance} ')



class SavingsAccount(BankAccount):

    """Savings Bank account with interest deposit and withdrowal operations
    month interest should be in percents
    """
    def __init__(self, name: str, surname: str,  min_balance: float = 20,
                  month_interest: float = 0, uuid:str | None = None, status: str = 'active', currency:str = 'RUB'  )->None:
        super().__init__(name = name, surname = surname, uuid = uuid, status = status, currency = currency)

        if min_balance < 0:
            raise InvalidOperationError('Min balance should be positive')
        self.min_balance = min_balance
        self.month_interest = month_interest
        if self.month_interest <0:
                    raise InvalidOperationError("Ineterest negative error")

    def withdraw(self, amount : float, )-> None:
        if isinstance(amount, bool) or not isinstance(amount, (float, int)):
            raise TypeError("Withdrowal amount should be float or int")
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')
        if (self._balance - amount ) < self.min_balance:
            raise InvalidOperationError("Withdrowal amount higher then minimum allowed balance")
        super().withdraw(amount = amount)

    def apply_month_interest(self)->None:
        if self._balance == 0 or self.month_interest == 0:
            return
        amount = self._balance * self.month_interest/100
        super().deposit(amount = amount)
        return
  


    def get_account_info(self)->dict:
            info = super().get_account_info()
            info['Minimum_balance'] = self.min_balance
            info['type'] = 'SavingsBankAccount'
            info['month_interest'] = self.month_interest
            return info
    

    def __str__(self)->str:
        parent_string = super().__str__().replace( "Bank account", "SavingsBank account", 1 )
        return (
            f'{parent_string},'
            f'Min. balance: {self.min_balance},'
            f'Monthly interest: {self.month_interest}'
        )
        

class PremiumAccount(BankAccount):

    """Premium Bank account with interest deposit and withdrowal operations
    month interest should be in percents
    """
    def __init__(self, name: str, surname: str, 
                   uuid:str | None = None, status: str = 'active', currency:str = 'RUB',
                    overdraft_limit: float = 0, bank_fee: float = 0, withdrawal_limit: float = 200 )->None:
        super().__init__(name=name, surname=surname, uuid=uuid, status=status, currency=currency)

        if isinstance((overdraft_limit, withdrawal_limit), bool) or not isinstance((overdraft_limit, withdrawal_limit), (int, float)):
            raise TypeError('Wrong type for overdraft_limit, withdrawal_limit the should be float or int')
        if not math.isfinite(overdraft_limit):
            raise ValueError('Overdraft_limit should be finit number')
        if not math.isfinite(withdrawal_limit):
            raise ValueError('withdrawal_limit should be finit number')        
        if overdraft_limit < 0 or withdrawal_limit < 0:
            raise InvalidOperationError ('Overdraft or withdrowal limit a less then zero')
        
        self.overdraft_limit = overdraft_limit
        self.withdrawal_limit = withdrawal_limit
        if(bank_fee < 0):
            raise InvalidOperationError('Bank fee has negative value')
        self.bank_fee = bank_fee



    def withdraw(self, amount : float)->None:
        if self._account_status == 'closed':
            raise AccountClosedError('Closed account error')
        if self._account_status == 'frozen':
            raise AccountFrozenError('Frozen account error')
        if isinstance(amount, bool) or not isinstance(amount,(float, int)):
            raise TypeError('Amount should be int or float')
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')
        if amount <= 0:
            raise InvalidOperationError("Negative or zero amount error")
        if (amount > self.withdrawal_limit):
            raise InvalidOperationError("Withdrowal exeeds withdrowal limit")
        if (self._balance - amount - self.bank_fee ) < -1 * self.overdraft_limit:
            raise InvalidOperationError("Withdrowal exeeds overdraft limit")
        if self._account_status != 'active':
            raise ValueError("Account is not active. Withdrowal is not permitied")
        self._balance -= (amount + self.bank_fee)
       

    def get_account_info(self)->dict:
            info = super().get_account_info()
            info['Overdraft limit'] = self.overdraft_limit
            info['Bank commission'] = self.bank_fee
            info['type'] = 'PremiumBankAccount'
            return info

    

    def __str__(self)->str:
        parent_string = super().__str__().replace( "Bank account", "PremiumBank account", 1 )
        return (
            f'{parent_string},' 
            f'Overdraft limit: {self.overdraft_limit}, '
            f'Bank commission: {self.bank_fee}'
             )


class InvestmentAccount(BankAccount):
    
    """Investment Bank account with several assests month interest should be in percents
    project_yearly_growth(growth_rates) allows to calculate actives amount increase for one yeat ahead
    """
    def __init__(self, name: str, surname: str, 
                   uuid:str | None = None, status: str = 'active', currency: str = 'RUB' )->None:
        super().__init__(name = name, surname = surname, uuid = uuid, status = status, currency = currency)

        self.portfolio: dict[str, float] = {'stocks': 0, 'bonds': 0, 'etf': 0} #Dict for allowed assest
        self.growth_rates: dict[str, float] = {'stocks': 10, 'bonds': 4, 'etf': 7} #Dict for allowed assest interests

    def buy_any_asset(self, asset_name: str, amount: float )-> None:
        '''
        Money -> Asset
        '''
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be int or float, but not bool")
        if not isinstance(asset_name, str):
            raise TypeError('AssestName should be str')
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')        

        if asset_name not in self.portfolio.keys():
            raise InvalidOperationError('No such asset in portfolio')
        if (amount > self._balance):
            raise InsufficientFundsError('Not enogh money bro')

        super().withdraw(amount = amount)
        self.portfolio[asset_name] = self.portfolio[asset_name] + amount 

    def sell_any_asset(self, asset_name: str, amount: float )-> None:
        '''
        Assest -> money
        '''
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be int or float, but not bool")
        if not isinstance(asset_name, str):
            raise TypeError('AssestName should be str type')
        if not math.isfinite(amount):
            raise ValueError('Value should ba finite number')        

        if asset_name not in self.portfolio.keys():
            raise InvalidOperationError('No such asset in portfolio')
        if (amount > self.portfolio[asset_name]):
            raise InsufficientFundsError('Not enogh money on your assets bro')

        super().deposit(amount = amount)
        self.portfolio[asset_name] = self.portfolio[asset_name] - amount 

    def project_yearly_growth(self, growth_rates: dict[str, float])-> float:
        '''
        Growth rates values should be string and float. 
        '''
        calculated_growth: float = 0

        if not isinstance(growth_rates, dict):
            raise TypeError('Invalid type of groth rates it shlould be a dict')

        for asset, value in growth_rates.items():
            if not isinstance (asset, str):
                raise TypeError('Invalid type of asset it shlould be a str')
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError('Invalid type of asset it shlould be a foat or int')
            if not math.isfinite(value):
                raise ValueError('Value should ba finite number')          
            #if (value <= 0):    #. Rates can positive and negative. Markets are so unpredictable
            #    raise ValueError("Value shoilud be positive and grater than zero")

        if growth_rates.keys() != self.portfolio.keys():
            raise InvalidOperationError("Asset types do not match portfolio")
        
        for asset, value in growth_rates.items():            
            calculated_growth = calculated_growth + self.portfolio[asset] * (value/100)
            
        return calculated_growth
            
    def withdraw(self, amount: float)-> None:
        super().withdraw(amount = amount)

    def get_account_info(self)->dict:
            info = super().get_account_info()
            info['type'] = 'InvestmentBankAccount'
            info['Assetes'] = self.portfolio
            return info
    

    def __str__(self)->str:
        parent_string = super().__str__().replace( "Bank account", "InvestmentBank account", 1 )
        return (
            f'{parent_string},' 
            f'Assets: {self.portfolio}'
            
        )
        
        
        
        
        





