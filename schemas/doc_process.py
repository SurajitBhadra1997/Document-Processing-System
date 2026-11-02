from typing import Optional, Any
from pydantic import BaseModel, Field


class MerchantDetails(BaseModel):
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None
    merchant_contact: Optional[str] = None
    merchant_tax_id: Optional[str] = None


class TransactionDetails(BaseModel):
    transaction_id: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_time: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None


class FinancialDetails(BaseModel):
    subtotal: Optional[str] = None
    total_tax: Optional[str] = None
    discount: Optional[str] = None
    shipping_charges: Optional[str] = None
    total_amount: Optional[str] = None
    amount_paid: Optional[str] = None
    balance_due: Optional[str] = None


class LineItem(BaseModel):
    description: Optional[str] = None
    item_code: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[str] = None
    discount: Optional[str] = None
    tax_amount: Optional[str] = None
    total_amount: Optional[str] = None


class DocumentData(BaseModel):
    document_type: Optional[str] = None
    expense_category: Optional[str] = None

    merchant_details: MerchantDetails = Field(default_factory=MerchantDetails)

    transaction_details: TransactionDetails = Field(default_factory=TransactionDetails)

    financial_details: FinancialDetails = Field(default_factory=FinancialDetails)

    line_items: list[LineItem] = Field(default_factory=list)

    additional_details: dict[str, Any] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)


class DocProcessResponse(BaseModel):
    filename: str
    status: str
    data: DocumentData
    validation: ValidationResult
    humanreview: bool = False
