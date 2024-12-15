from pydantic import BaseModel

class MessageCreate(BaseModel):
    """Schema for creating message."""
    channel_id: str
    publisher: str
    base_name: str | None
    base_time: float | None
    base_unit: str | None
    base_value: float | None
    # base_sum: float | None
    # version: float | None
    name: str | None
    unit: str | None
    value: float | None
    time: float | None
    string_value: str | None
    bool_value: bool | None
    data_value: str | None
    # sum: float | None

