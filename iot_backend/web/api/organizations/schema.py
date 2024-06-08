from pydantic import BaseModel


class OrganizationDTO(BaseModel):
    """
    DTO for organizations.

    It is returned when accessing organizations from the API.
    """

    id: int
    name: str
    # organization_config = ConfigDict(from_attributes=True)


class OrganizationInputDTO(BaseModel):
    """DTO for creating a new organization."""

    name: str
