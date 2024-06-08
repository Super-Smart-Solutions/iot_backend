from pydantic import BaseModel


class GroupDTO(BaseModel):
    """
    DTO for groups.

    It is returned when accessing groups from the API.
    """

    id: int
    name: str
    organization_id: int
    # group_config = ConfigDict(from_attributes=True)


class GroupInputDTO(BaseModel):
    """DTO for creating a new group."""

    name: str
    organization_id: int
