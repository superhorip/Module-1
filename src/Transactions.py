from abc import ABC, abstractmethod
from uuid import uuid4
import math
from datetime import datetime

import Bank_Account_class as BA
import Bank as Bank



class Transaction():
    '''
    Stores information bout single operation
    '''