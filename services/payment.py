from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class Payment(BaseModel):
    id: Optional[int] = None
    user_id: int
    course_id: int
    amount: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    class Config:
        orm_mode = True


class PaymentService:
    """Service for managing payments in the online course platform."""
    
    async def create_payment(self, payment_data: dict) -> Payment:
        """Create a new payment."""
        payment = Payment(**payment_data)
        # In a real implementation, this would save to a database
        return payment
    
    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Get a payment by ID."""
        # In a real implementation, this would fetch from a database
        return None
    
    async def update_payment(self, payment_id: int, payment_data: dict) -> Optional[Payment]:
        """Update a payment's information."""
        # In a real implementation, this would update in a database
        return None
    
    async def list_payments(self, 
                           skip: int = 0, 
                           limit: int = 100, 
                           filters: Optional[Dict[str, Any]] = None) -> List[Payment]:
        """List all payments with pagination and optional filtering."""
        # In a real implementation, this would fetch from a database with filters
        return []
    
    async def get_user_payments(self, user_id: int) -> List[Payment]:
        """Get all payments made by a specific user."""
        # In a real implementation, this would fetch from a database
        return []
    
    async def get_course_payments(self, course_id: int) -> List[Payment]:
        """Get all payments for a specific course."""
        # In a real implementation, this would fetch from a database
        return []
    
    async def process_payment(self, payment_id: int) -> Optional[Payment]:
        """Process a pending payment."""
        # In a real implementation, this would interact with a payment gateway
        # and update the payment status accordingly
        return None
    
    async def refund_payment(self, payment_id: int) -> Optional[Payment]:
        """Refund a completed payment."""
        # In a real implementation, this would interact with a payment gateway
        # to process the refund and update the payment status
        return None