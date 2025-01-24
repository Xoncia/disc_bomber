from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar, Dict
from pydantic import BaseModel, Field

T = TypeVar('T')

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: str = Field(description="Error code for programmatic handling")

class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    message: Optional[str] = None

    @classmethod
    def success_response(cls, data: Any = None, message: str = None) -> "BaseResponse":
        return cls(
            success=True,
            data=data,
            message=message,
            timestamp=datetime.utcnow()
        )

    @classmethod
    def error_response(
        cls,
        message: str,
        errors: List[ErrorDetail] = None,
        code: str = "INTERNAL_ERROR"
    ) -> "BaseResponse":
        if not errors:
            errors = [ErrorDetail(message=message, code=code)]
        return cls(
            success=False,
            message=message,
            errors=errors,
            timestamp=datetime.utcnow()
        )

class HealthStatus(BaseModel):
    status: str
    version: str = "1.0.0"
    uptime: str
    uptime_seconds: int
    is_healthy: bool = True
    last_check: datetime

class HealthResponse(BaseResponse[HealthStatus]):
    pass

class MessageResponse(BaseResponse[Dict[str, Any]]):
    pass 