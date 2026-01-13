---
description: Pydantic v2 data validation with custom validators, serialization, and settings management
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pydantic Data Validation Expert Skill

You are an expert in Pydantic v2 for data validation, serialization, and settings management in Python applications.

### Pydantic v2 Core Concepts

1. **BaseModel**: Foundation for all data models
2. **Field**: Advanced field configuration and validation
3. **Validators**: Custom validation logic
4. **Serialization**: Control JSON/dict output
5. **Settings**: Environment-based configuration

### Basic Model Definition

```python
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class User(BaseModel):
    """User model with validation."""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=1,           # Minimum string length
        from_attributes=True,        # Allow ORM mode
        validate_assignment=True,    # Validate on attribute assignment
        extra="forbid",              # Forbid extra attributes
    )

    id: int = Field(description="Unique identifier")
    username: Annotated[str, Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
        examples=["john_doe", "user123"],
    )]
    email: Annotated[str, Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
        description="Valid email address",
    )]
    age: Annotated[int, Field(ge=0, le=150, description="User's age")]
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Field Types and Constraints

```python
from pydantic import (
    BaseModel, Field, HttpUrl, EmailStr, SecretStr,
    PositiveInt, NonNegativeFloat, constr, conint, conlist
)
from decimal import Decimal
from uuid import UUID


class Product(BaseModel):
    # Constrained types
    id: UUID
    sku: constr(min_length=5, max_length=20, to_upper=True)
    name: str = Field(min_length=1, max_length=200)

    # Numeric constraints
    price: Decimal = Field(gt=0, decimal_places=2)
    quantity: PositiveInt
    discount: NonNegativeFloat = Field(default=0.0, le=1.0)

    # Special types
    website: HttpUrl | None = None
    contact_email: EmailStr
    api_key: SecretStr  # Hidden in repr/logging

    # List constraints
    tags: conlist(str, min_length=1, max_length=10) = []

    # Computed field
    @property
    def total_value(self) -> Decimal:
        return self.price * self.quantity
```

### Custom Validators

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Self


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str
    age: int

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_domain_check(cls, v: str) -> str:
        blocked_domains = ["tempmail.com", "throwaway.com"]
        domain = v.split("@")[-1]
        if domain in blocked_domains:
            raise ValueError(f"Email domain {domain} is not allowed")
        return v.lower()

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int) -> int:
        if v < 13:
            raise ValueError("Must be at least 13 years old")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

### Serialization Control

```python
from pydantic import BaseModel, Field, field_serializer, computed_field
from datetime import datetime
from decimal import Decimal


class Order(BaseModel):
    model_config = ConfigDict(
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
    )

    id: int
    items: list[str]
    total: Decimal
    created_at: datetime
    internal_notes: str = Field(exclude=True)  # Exclude from serialization

    @field_serializer("total")
    def serialize_total(self, value: Decimal) -> str:
        return f"${value:.2f}"

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @computed_field
    @property
    def item_count(self) -> int:
        return len(self.items)


# Serialization options
order = Order(id=1, items=["a", "b"], total=Decimal("99.99"),
              created_at=datetime.now(), internal_notes="secret")

order.model_dump()                    # Dict
order.model_dump(exclude={"id"})      # Exclude fields
order.model_dump(include={"total"})   # Include only
order.model_dump(by_alias=True)       # Use field aliases
order.model_dump_json()               # JSON string
```

### Aliases and Field Names

```python
from pydantic import BaseModel, Field, AliasChoices, AliasPath


class ExternalAPIResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Simple alias
    user_id: int = Field(alias="userId")

    # Multiple alias choices (for compatibility)
    email_address: str = Field(
        validation_alias=AliasChoices("email", "emailAddress", "mail")
    )

    # Nested alias path
    city: str = Field(validation_alias=AliasPath("address", "city"))

    # Separate serialization alias
    full_name: str = Field(
        validation_alias="fullName",
        serialization_alias="name",
    )


# Parse from external format
data = {"userId": 1, "emailAddress": "test@example.com",
        "address": {"city": "NYC"}, "fullName": "John Doe"}
response = ExternalAPIResponse.model_validate(data)
```

### Generic Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int


class UserSummary(BaseModel):
    id: int
    username: str


# Usage
paginated_users = PaginatedResponse[UserSummary](
    items=[UserSummary(id=1, username="john")],
    total=100,
    page=1,
    limit=20,
    pages=5,
)
```

### Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from pydantic import Discriminator


class CreditCardPayment(BaseModel):
    type: Literal["credit_card"] = "credit_card"
    card_number: str
    expiry: str
    cvv: str


class PayPalPayment(BaseModel):
    type: Literal["paypal"] = "paypal"
    email: str


class BankTransfer(BaseModel):
    type: Literal["bank_transfer"] = "bank_transfer"
    account_number: str
    routing_number: str


# Discriminated union
Payment = Annotated[
    Union[CreditCardPayment, PayPalPayment, BankTransfer],
    Field(discriminator="type"),
]


class Order(BaseModel):
    id: int
    payment: Payment


# Validation automatically selects correct type
order1 = Order(id=1, payment={"type": "credit_card", "card_number": "...",
                              "expiry": "12/25", "cvv": "123"})
order2 = Order(id=2, payment={"type": "paypal", "email": "user@paypal.com"})
```

### Settings Management

```python
from pydantic import Field, SecretStr, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",           # All env vars prefixed with APP_
        case_sensitive=False,
        extra="ignore",
    )

    # Required settings (no default)
    database_url: PostgresDsn
    secret_key: SecretStr

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"

    # Nested settings with env prefix
    redis_url: RedisDsn | None = None

    # List from comma-separated env var
    allowed_hosts: list[str] = Field(default=["localhost"])

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v


# Usage
settings = Settings()
# Reads from environment variables:
# APP_DATABASE_URL=postgresql://...
# APP_SECRET_KEY=mysecret
# APP_DEBUG=true
# APP_ALLOWED_HOSTS=localhost,example.com
```

### Request/Response Schema Patterns

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# Base schema with common fields
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str


# Create schema (input)
class UserCreate(UserBase):
    password: str = Field(min_length=8)


# Update schema (all optional)
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None


# Response schema (output)
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Detail response with relationships
class UserDetailResponse(UserResponse):
    orders: list["OrderSummary"] = []
    total_orders: int = 0
```

### Error Handling

```python
from pydantic import BaseModel, ValidationError
import json


class User(BaseModel):
    name: str
    age: int


try:
    user = User(name="", age="invalid")
except ValidationError as e:
    # Structured error info
    print(e.error_count())     # Number of errors
    print(e.errors())          # List of error dicts
    print(e.json())            # JSON formatted errors

    # Custom error formatting
    for error in e.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        print(f"{field}: {message}")


# Custom error messages
class StrictUser(BaseModel):
    name: str = Field(min_length=1, json_schema_extra={
        "error_messages": {"min_length": "Name cannot be empty"}
    })
```

### Validation Checklist

- [ ] Use Pydantic v2 syntax (`model_config` instead of `class Config`)
- [ ] Define appropriate constraints (`min_length`, `ge`, `le`, etc.)
- [ ] Use `Annotated` with `Field` for complex validations
- [ ] Implement `field_validator` for custom logic
- [ ] Use `model_validator` for cross-field validation
- [ ] Configure serialization with `field_serializer`
- [ ] Handle optional fields with `| None` syntax
- [ ] Use discriminated unions for polymorphic data
- [ ] Leverage `pydantic-settings` for configuration
- [ ] Write comprehensive validation error handling

---

When implementing data validation, always use Pydantic v2 patterns and ensure comprehensive validation coverage.
