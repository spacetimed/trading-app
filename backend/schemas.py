from pydantic import BaseModel, EmailStr, Field, ConfigDict

from datetime import datetime

from decimal import Decimal

# register models
class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # mold input to model based off matching fields

# login models
class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel): 
    token: str
    token_type: str

class DepositPayload(BaseModel):
    amount: Decimal = Field(gt=0)

class DepositResponse(BaseModel):
    cash_balance: Decimal

class WithdrawPayload(BaseModel):
    amount: Decimal = Field(gt=0)

class WithdrawResponse(BaseModel):
    cash_balance: Decimal

class AccountSummaryResponse(BaseModel):
    cash_balance: Decimal
    total_deposits: Decimal
    total_withdrawals: Decimal
    transaction_count: int

class QuoteResponse(BaseModel):
    symbol: str
    price: Decimal

class BuyOrderPayload(BaseModel):
    symbol: str
    quantity: int = Field(gt=0)

class BuyOrderResponse(BaseModel):
    symbol: str
    quantity: int
    price: Decimal
    total_cost: Decimal
    cash_balance: Decimal

class PositionResponse(BaseModel):
    symbol: str
    quantity: int
    avg_cost: Decimal
    current_price: Decimal
    cost_basis: Decimal
    market_value: Decimal
    unrealized_gain_loss: Decimal
    unrealized_gain_loss_percent: Decimal

    model_config = ConfigDict(from_attributes=True) # fit Position objects dynamically

class TradeResponse(BaseModel):
    symbol: str
    side: str
    quantity: int
    price: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SellOrderPayload(BaseModel):
    symbol: str
    quantity: int = Field(gt=0)

class SellOrderResponse(BaseModel):
    symbol: str
    quantity: int
    price: Decimal
    total_proceeds: Decimal
    cash_balance: Decimal
