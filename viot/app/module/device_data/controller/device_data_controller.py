from typing import Annotated
from uuid import UUID

from classy_fastapi import get
from fastapi import Path, Query
from injector import inject

from app.common.controller import Controller
from app.common.fastapi.serializer import JSONResponse
from app.database.dependency import DependSession
from app.module.auth.dependency import RequireTeamPermission
from app.module.auth.permission import TeamDeviceDataPermission

from ..constants import DeviceAttributeScope
from ..dto.device_attribute_dto import DeviceAttributeDto, ScopeKeysDto
from ..dto.device_data_dto import (
    DataPointDto,
    KeySetQuery,
    LatestDataPointDto,
    TimeseriesAggregationQueryDto,
)
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
        responses={200: {"model": ScopeKeysDto}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_all_attribute_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
    ) -> JSONResponse[ScopeKeysDto]:
        """
        Get all attribute keys

        Returns a set of unique keys for the device attributes.
        The responses will include key names set for all attribute scopes:
        - SERVER_SCOPE
        - SHARED_SCOPE
        - CLIENT_SCOPE
        """
        return JSONResponse(
            content=await self._device_attribute_service.get_all_keys_by_device_id(
                device_id=device_id
            ),
            status_code=200,
        )

    @get(
        "/{device_id}/attributes/keys/{scope}",
        summary="Get keys by scope",
        status_code=200,
        responses={200: {"model": set[str]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_keys_by_scope(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        scope: Annotated[
            DeviceAttributeScope,
            Path(..., description="0: SERVER_SCOPE, 1: SHARED_SCOPE, 2: CLIENT_SCOPE"),
        ],
    ) -> JSONResponse[set[str]]:
        """Get keys by scope"""
        return JSONResponse(
            content=await self._device_attribute_service.get_all_key_by_scope_and_device_id(
                device_id=device_id, scope=scope
            )
        )

    @get(
        "/{device_id}/attributes/{scope}",
        summary="Get all attributes by keys",
        status_code=200,
        responses={200: {"model": list[DeviceAttributeDto]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_all_attributes_by_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        scope: Annotated[
            DeviceAttributeScope,
            Path(..., description="0: SERVER_SCOPE, 1: SHARED_SCOPE, 2: CLIENT_SCOPE"),
        ],
        keys: KeySetQuery,
    ) -> JSONResponse[list[DeviceAttributeDto]]:
        """
        Returns all attributes of a specified scope. List of possible attribute scopes
        depends on the entity type:
        - SERVER_SCOPE
        - SHARED_SCOPE
        - CLIENT_SCOPE
        """
        return JSONResponse(
            content=await self._device_attribute_service.get_all_by_device_id(
                device_id=device_id, keys=keys, scope=scope
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
        responses={200: {"model": list[DeviceAttributeDto]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_latest_timeseries_data_by_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        keys: KeySetQuery,
    ) -> JSONResponse[list[LatestDataPointDto]]:
        """Get latest data by keys"""
        return JSONResponse(
            content=await self._device_data_service.get_latest_data_by_keys(
                device_id=device_id, keys=keys
            ),
            status_code=200,
        )

    @get(
        "/{device_id}/timeseries",
        summary="Get timeseries data by keys",
        status_code=200,
        responses={200: {"model": list[DeviceAttributeDto]}},
        dependencies=[RequireTeamPermission(TeamDeviceDataPermission.READ)],
    )
    async def get_timeseries_data_by_keys(
        self,
        *,
        device_id: Annotated[UUID, Path(...)],
        query_dto: Annotated[TimeseriesAggregationQueryDto, Query(...)],
    ) -> JSONResponse[dict[str, list[DataPointDto]]]:
        """
        Returns a time series range for the device timeseries data.
        By default, the data is not aggregated.
        To enable server-side aggregation, use the `agg` parameter for the aggregation function,
         `intervalType` for the aggregation interval and `interval`.
         Server-side aggregation is typically more
        efficient than retrieving all records without processing.

        ```json
        {
          "kwh": [
            {
              "ts": "2021-08-12T00:00:00Z",
              "value": 100.0
            },
            {
              "ts": "2021-08-13T00:00:00Z",
              "value": 200.0
            }
          ]
        }
        ```
        """
        return JSONResponse(
            content=await self._device_data_service.get_timeseries_data_by_keys(
                device_id=device_id, query_dto=query_dto
            ),
            status_code=200,
        )
