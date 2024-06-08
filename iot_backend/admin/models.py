from typing import Any, Coroutine

from fastapi import Request
from fastapi_users.password import PasswordHelper
from sqladmin import ModelView

from iot_backend.db.models.alert import Alert
from iot_backend.db.models.device import Device
from iot_backend.db.models.group import Group
from iot_backend.db.models.organization import Organization
from iot_backend.db.models.tag import Tag
from iot_backend.db.models.users import User


class UserView(ModelView, model=User):
    column_list = [
        "email",
        "is_active",
        "is_verified",
        "is_superuser",
        "organization_id",
        "group_id",
        "devices",
    ]

    def insert_model(self, request: Request, data: dict) -> Coroutine[Any, Any, Any]:
        hash_password = PasswordHelper().hash(password=data["hashed_password"])
        data["hashed_password"] = hash_password
        return super().insert_model(request, data)


class OrganizationView(ModelView, model=Organization):
    column_list = ["name"]


class GroupView(ModelView, model=Group):
    column_list = ["name", "organization_id"]


class DeviceView(ModelView, model=Device):
    column_list = [
        "name",
        "meta_data",
        "tags",
        "mainflux_thing_uuid",
        "mainflux_thing_secret",
        "is_configured",
        "tags",
    ]


class AlertView(ModelView, model=Alert):
    column_list = [
        "name",
        "threshold",
        "comparator",
        "status",
        "user_id",
        "device_id",
    ]


class TagView(ModelView, model=Tag):
    column_list = [
        "name",
        "label",
        "mask",
        "graphed",
        "multiplier",
        "target",
        "unit",
    ]
