from fastapi import HTTPException, status
from mainflux_client import (
    Configuration,
    ApiClient,
    ThingsApi,
    ChannelsApi,
    MessagesApi,
    ReadersApi,
    UsersApi,
    PoliciesApi
    )
from iot_backend.settings import settings


def get_mainflux_config(
    access_token: str = None, thing_secret: str = None, port: int = None
):
    if access_token:
        if port:
            return Configuration(
                host=f"{settings.mainflux_host}:9009", access_token=access_token
            )
        return Configuration(host=settings.mainflux_host, access_token=access_token)
    else:
        if not thing_secret:
            # raise ValueError("Either access_token or thing_secret must be provided")
            return Configuration(host=settings.mainflux_host)

        return Configuration(host=f"{settings.mainflux_host}/http", api_key=thing_secret, api_key_prefix="Thing ")


def get_api_client(config: Configuration) -> ApiClient:
    """
    Get Mainflux API client instance.

    Args:
        config (Configuration): Mainflux client configuration.

    Returns:
        ApiClient: Mainflux API client instance.
    """
    return ApiClient(config)


def get_things_api(access_token: str) -> ThingsApi:
    """
    Get Mainflux Things API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        ThingsApi: Mainflux Things API client instance.
    """
    config = get_mainflux_config(access_token)
    api_client = get_api_client(config)
    return ThingsApi(api_client)


def get_channels_api(access_token: str) -> ChannelsApi:
    """
    Get Mainflux Channels API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        ThingsApi: Mainflux Things API client instance.
    """
    config = get_mainflux_config(access_token)
    api_client = get_api_client(config)
    return ChannelsApi(api_client)


def get_messages_api(thing_secret: str) -> MessagesApi:
    """
    Get Mainflux Messages API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        MessagesApi: Mainflux Messages API client instance.
    """
    config = get_mainflux_config(thing_secret=thing_secret)
    api_client = get_api_client(config)
    return MessagesApi(api_client)


def get_reader_api(access_token: str) -> ReadersApi:
    """
    Get Mainflux Messages API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        MessagesApi: Mainflux Messages API client instance.
    """
    config = get_mainflux_config(access_token=access_token, port=9009)
    api_client = get_api_client(config)
    return ReadersApi(api_client)


def get_users_api() -> UsersApi:
    """
    Get Mainflux Users API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        UsersApi: Mainflux Users API client instance.
    """
    config = get_mainflux_config()
    api_client = get_api_client(config)
    return UsersApi(api_client)


def get_policies_api(access_token: str) -> PoliciesApi:
    """
    Get Mainflux Policies API client instance.

    Args:
        api_client (ApiClient): Mainflux API client.

    Returns:
        PoliciesApi: Mainflux Policies API client instance.
    """
    config = get_mainflux_config(access_token=access_token)
    api_client = get_api_client(config)
    return PoliciesApi(api_client)

def get_channel_id(uuid: str = None, name: str = None) -> str:
    """
    Retrieves the ID of a channel based on either its name or UUID.

    Args:
        uuid: The UUID of the channel.
        name: The name of the channel.

    Returns:
        The ID of the channel.

    Raises:
        HTTPException: If no channel is found with the provided name or UUID.
    """

    if not (uuid or name):
        raise ValueError("Either uuid or name must be provided")

    channel_name = f"actions_{uuid}" if uuid else name
    channels_api = get_channels_api(access_token=settings.mainflux_token)
    channels = channels_api.channels_get(name=channel_name).channels
    if len(channels) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No channels Found")
    return channels[0].id

