from __future__ import annotations

from collections import defaultdict
from typing import Any

import requests
from sqlalchemy.orm import Session

from common.constants import (
    InventoryChangesIndexes,
    ConditionsOrders,
    INSTANCE_BY_EVENT_MANAGER_INDEX,
    EVENT_INDEXES_BY_INSTANCES,
)
from config.security_config import (
    KEYCLOAK_REDIRECT_PROTOCOL,
    KEYCLOAK_REDIRECT_HOST,
    KEYCLOAK_REALM,
    SECURITY_TYPE,
)
from routers.event_router.schemas import (
    GetEventsByInstanceTypeRequest,
    GetParameterHistoryByObjectIdsRequest,
    GetEventsByInstanceTypeResponse,
    ElasticSearchResponse,
)
from services.elastic_service.elastic_client import elastic_client
from services.event_processor.inventory_processor.constants import (
    AvailableInventoryInstances,
)


class GetEventsByFilters:
    def __init__(
        self,
        session: Session,
        request: GetEventsByInstanceTypeRequest,
        token: str,
    ):
        self._session = session
        self._request = request
        self._token = token

    @staticmethod
    def _add_filter_by_date(
        filter_query: dict, request: GetEventsByInstanceTypeRequest
    ):
        updated_query = dict(filter_query)

        if request.date_from or request.date_to:
            date_range: dict[str, Any] = {}
            if request.date_from:
                date_range["gte"] = request.date_from.isoformat()

            if request.date_to:
                date_range["lte"] = request.date_to.isoformat()

            updated_query["query"]["bool"]["filter"].append(
                {"range": {"valid_from": date_range}}
            )

        return updated_query

    def _create_filter_query(
        self, request: GetEventsByInstanceTypeRequest
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "query": {"bool": {"must": [], "filter": []}},
            "sort": [],
            "from": request.offset,
            "size": request.limit,
        }

        query = self._add_filter_by_date(filter_query=query, request=request)

        for filter_instance in request.filter_column:
            if filter_instance.field == "instance":
                continue
            term_query = {
                "term": {
                    filter_instance.field: {"value": filter_instance.value}
                }
            }

            condition = filter_instance.condition.value.lower()

            if condition == ConditionsOrders.AND.value.lower():
                query["query"]["bool"]["must"].append(term_query)

            else:
                if "should" not in query["query"]["bool"]:
                    query["query"]["bool"]["should"] = []
                    query["query"]["bool"]["minimum_should_match"] = 1
                query["query"]["bool"]["should"].append(term_query)

        return query

    @staticmethod
    def _create_sort_query(
        filter_query: dict, request: GetEventsByInstanceTypeRequest
    ) -> dict[str, Any]:
        updated_query = dict(filter_query)

        updated_query["sort"].append(
            {request.sort_by.field: {"order": request.sort_by.descending.value}}
        )
        return updated_query

    def _get_event_instances_by_filters(self) -> ElasticSearchResponse:
        filter_conditions = self._create_filter_query(request=self._request)
        filter_with_sorting = self._create_sort_query(
            filter_query=filter_conditions, request=self._request
        )
        index = InventoryChangesIndexes.ALL.value
        for filter_instance in self._request.filter_column:
            if filter_instance.field == "instance":
                index = EVENT_INDEXES_BY_INSTANCES.get(
                    filter_instance.value, InventoryChangesIndexes.ALL.value
                )

        response = elastic_client.search(
            index=index,
            body=filter_with_sorting,
            track_total_hits=True,
        )

        return ElasticSearchResponse(
            response=response["hits"]["hits"],
            total_count=response["hits"]["total"]["value"],
        )

    def _get_username_by_user_ids(self) -> dict[str, str]:
        url = f"{KEYCLOAK_REDIRECT_PROTOCOL}://{KEYCLOAK_REDIRECT_HOST}/admin/realms/{KEYCLOAK_REALM}/users"
        response = requests.get(
            url=url, headers={"Authorization": self._token}, timeout=10
        )
        return {
            user_instance["id"]: user_instance["username"]
            for user_instance in response.json()
        }

    def _replace_user_id_by_username(
        self, parameter_event_instances: list[dict[str, Any]]
    ):
        if SECURITY_TYPE == "KEYCLOAK":
            username_by_user_id = self._get_username_by_user_ids()

            for event_instance in parameter_event_instances:
                event_instance["_source"]["user_id"] = username_by_user_id.get(
                    event_instance["_source"]["user_id"]
                )

        return parameter_event_instances

    def execute(self):
        event_instances = self._get_event_instances_by_filters()
        hits = self._replace_user_id_by_username(event_instances.response)

        response = []
        for event in hits:
            data = event["_source"]
            data["instance"] = INSTANCE_BY_EVENT_MANAGER_INDEX.get(
                event["_index"]
            )
            response.append(data)

        return GetEventsByInstanceTypeResponse(
            data=response, total=event_instances.total_count
        )


class GetParameterEventsByObjectIds:
    def __init__(
        self,
        request: GetParameterHistoryByObjectIdsRequest,
        session: Session,
        token: str,
    ):
        self._request = request
        self._session = session
        self._token = token

    @staticmethod
    def _add_filter_by_date(
        filter_query: dict, request: GetParameterHistoryByObjectIdsRequest
    ):
        updated_query = dict(filter_query)
        if request.date_from or request.date_to:
            date_range: dict[str, Any] = {}
            if request.date_from:
                date_range["gte"] = request.date_from.isoformat()
            if request.date_to:
                date_range["lte"] = request.date_to.isoformat()
            updated_query["query"]["bool"]["filter"].append(
                {"range": {"valid_from": date_range}}
            )
        return updated_query

    def _get_query_for_getting_parameter_ids(self) -> dict[str, Any]:
        query: dict[str, Any] = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "new_value_str": list(self._request.object_ids)
                            }
                        },
                        {"term": {"attribute": "mo_id"}},
                    ]
                }
            },
            "_source": ["instance_id", "new_value"],
        }
        return query

    def _get_query_for_parameter_values(self, parameter_ids: set[str]):
        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"terms": {"instance_id": list(parameter_ids)}},
                        {"term": {"attribute": "value"}},
                    ]
                }
            },
            "sort": [
                {"valid_from": {"order": self._request.sort_by_datetime.value}}
            ],
            "from": self._request.offset,
            "size": self._request.limit,
        }
        query = self._add_filter_by_date(
            filter_query=query, request=self._request
        )
        return query

    def execute(self):
        query = self._get_query_for_getting_parameter_ids()
        parameter_instances_on_requested_object_id = elastic_client.search(
            index=InventoryChangesIndexes.PRM.value,
            body=query,
        )

        parameter_instances_on_requested_object_id = (
            parameter_instances_on_requested_object_id["hits"]["hits"]
        )
        parameter_ids = set()
        object_id_by_parameter_id = dict()
        for instance in parameter_instances_on_requested_object_id:
            parameter_id = instance["_source"]["instance_id"]
            object_id = instance["_source"]["new_value"]
            parameter_ids.add(parameter_id)
            object_id_by_parameter_id[parameter_id] = object_id

        parameter_instances = elastic_client.search(
            index=InventoryChangesIndexes.PRM.value,
            body=self._get_query_for_parameter_values(
                parameter_ids=parameter_ids
            ),
            track_total_hits=True,
        )
        response_parameter_instances: list[dict[str, Any]] = []

        for parameter_instance in parameter_instances["hits"]["hits"]:
            src = parameter_instance["_source"]
            response_parameter_instances.append(src)

        tprm_by_param: dict[int, Any] = {}
        if parameter_ids:
            tprm_hits = elastic_client.search(
                index=InventoryChangesIndexes.PRM.value,
                body={
                    "query": {
                        "bool": {
                            "filter": [
                                {"terms": {"instance_id": list(parameter_ids)}},
                                {"term": {"attribute": {"value": "tprm_id"}}},
                            ]
                        }
                    },
                    "_source": ["instance_id", "new_value"],
                },
                track_total_hits=False,
            )["hits"]["hits"]
            tprm_by_param = {
                th["_source"]["instance_id"]: int(th["_source"]["new_value"])
                for th in tprm_hits
            }

        response = defaultdict(list)
        for parameter_instance in response_parameter_instances:
            parameter_id = parameter_instance.get("instance_id")
            object_id = object_id_by_parameter_id[parameter_id]

            parameter_instance["instance"] = (
                AvailableInventoryInstances.PRM.value
            )
            parameter_instance["parameter_type_id"] = tprm_by_param.get(
                parameter_id
            )
            response[object_id].append(parameter_instance)

        return {
            object_id: {"data": parameters, "total": len(parameters)}
            for object_id, parameters in response.items()
        }
