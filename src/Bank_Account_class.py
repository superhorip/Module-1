from abc import ABC, abstractmethod
from uuid import uuid4

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
    def withdraw(self, amount:float)->None:
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
        
    def deposit(self, amount:float)->None:
        if self._account_status == 'closed':
            raise AccountClosedError('Closed account error')
        if self._account_status == 'frozen':
            raise AccountFrozenError('Frozen account error')
        if amount <= 0:
            raise InvalidOperationError("Negative or zero amount error")
        if amount >0:
            super().deposit(amount=amount)


    def withdraw(self, amount:float)->None:
        if self._account_status == 'closed':
            raise AccountClosedError('Closed account error')
        if self._account_status == 'frozen':
            raise AccountFrozenError('Frozen account error')
        if amount <= 0:
            raise InvalidOperationError("Negative or zero amount error")
        if self._balance < amount:
            raise InsufficientFundsError("Not enought funds error ")
        super().withdraw(amount=amount)
        
    def get_account_info(self)->dict:
        return {'name':self.name, 'surname':self.surname, 'type':'BankAccount','status':self._account_status, 'balance':self._balance, 'currency':self.currency,'uuid':str(self._uuid) }
    
    def __str__(self):
        return (f'Bank account, holder name: {self.surname}, {self.name}, uuid: {str(self._uuid)[-4:]}, status: {self._account_status}, type: {self.currency}, balance: {self._balance} ')



class SavingsAccount(BankAccount):

    """Savings Bank account with interest deposit and withdrowal operations
    month interest should be in percents
    """
    def __init__(self, name: str, surname: str,  min_balance: float = 0,
                  month_interest: float = 0, uuid:str | None = None, status: str = 'active', currency:str = 'RUB'  )->None:
        super().__init__(name=name, surname=surname, uuid=uuid, status=status, currency=currency)

        self.min_balance = min_balance
        self.month_interest = month_interest

    def withdraw(self, amount:float, )->None:
        
        if (self._balance - amount )< self.min_balance:
            raise InvalidOperationError("Withdrowal amount higher then minimum allowed balance")
        super().withdraw(amount=amount)

    def apply_month_interest(self):
        current_balance = self._balance
        increment_amount = current_balance * self.month_interest/100
        super().deposit(amount=increment_amount)
  


    def get_account_info(self)->dict:
            info = super().get_account_info()
            info['Minimum_balance'] = self.min_balance
            info['type'] = 'SavingsBankAccount'
            info['month_interest'] = self.month_interest
            return info
    

    
    def __str__(self)->str:
        parent_string = super().__str__()
        return (
            f'{parent_string},' 
            f'Min. balance: {self.min_balance},'
            f'Monthly interest: {self.month_interest}%'
        )
        
        
        
        
        
        
        #return (f'Savings account, holder name: {self.surname}, {self.name}, uuid: {str(self._uuid)[-4:]},  status: {self._account_status}, type: {self.currency}, balance: {self._balance},  Min. allowed balance: {self.min_balance} ')        





