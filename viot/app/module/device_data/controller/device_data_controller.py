from typing import Annotated
from uuid import UUID

from classy_fastapi import get
from fastapi import Path
from injector import inject

from app.common.controller import Controller
from app.common.fastapi.serializer import JSONResponse
from app.database.dependency import DependSession
from app.module.auth.dependency import RequireTeamPermission
from app.module.auth.permission import TeamDeviceDataPermission

from ..dto.device_attribute_dto import DeviceAttributeDto
from ..dto.device_data_dto import DeviceDataDto, KeySetQuery
from ..service.device_attribute_service import DeviceAttributeService
from ..service.device_data_service import DeviceDataService


class DeviceDataController(Controller):
    @inject
    def __init__(
        self,
        device_data_service: DeviceDataService,
        device_attribute_service: DeviceAttributeService,
    ) -> None:
        super().__init__(
            prefix="/teams/{team_id}/devices",
            tags=["Device Data"],
            dependencies=[DependSession],
        )
        self._device_data_service = device_data_service
        self._device_attribute_service = device_attribute_service

    @get(
        "/{device_id}/attributes/keys",
        summary="Get all keys",
        status_code=200,
        responses={200: {"model": set[str]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_all_attribute_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
    ) -> JSONResponse[set[str]]:
        """Get all attribute keys"""
        return JSONResponse(
            content=await self._device_attribute_service.get_all_keys(device_id=device_id),
            status_code=200,
        )

    @get(
        "/{device_id}/attributes",
        summary="Get all attributes by keys",
        status_code=200,
        responses={200: {"model": list[DeviceAttributeDto]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_all_attributes_by_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        keys: KeySetQuery,
    ) -> JSONResponse[list[DeviceAttributeDto]]:
        """Get all attributes by keys"""
        return JSONResponse(
            content=await self._device_attribute_service.get_all_by_device_id(
                device_id=device_id, keys=keys
            ),
            status_code=200,
        )

    @get(
        "/{device_id}/timeseries/keys",
        summary="Get all timeseries keys",
        status_code=200,
        responses={200: {"model": set[str]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_all_timeseries_data_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
    ) -> JSONResponse[set[str]]:
        """Get all timeseries data keys"""
        return JSONResponse(
            content=await self._device_data_service.get_all_keys(device_id=device_id),
            status_code=200,
        )

    @get(
        "/{device_id}/timeseries/latest",
        summary="Get latest timeseries data by keys",
        status_code=200,
        responses={200: {"model": list[DeviceDataDto]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_latest_timeseries_data_by_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        keys: KeySetQuery,
    ) -> JSONResponse[list[DeviceDataDto]]:
        """Get latest data by keys"""
        return JSONResponse(
            content=await self._device_data_service.get_latest_data_by_keys(
                device_id=device_id, keys=keys
            ),
            status_code=200,
        )