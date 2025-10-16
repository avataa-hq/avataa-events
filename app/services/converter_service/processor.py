import pickle

from common.constants import InventoryChangesIndexes
from services.converter_service.schemas import ParameterInstance
from services.elastic_service.elastic_client import elastic_client


class ConvertParameterValues:
    @staticmethod
    def _get_parameter_type_attribute_by_id(
        parameter_type_id: int, attribute: str
    ):
        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"instance_id": parameter_type_id}},
                        {"term": {"attribute": attribute}},
                        {"term": {"is_active": True}},
                    ]
                }
            }
        }
        response = elastic_client.search(
            index=InventoryChangesIndexes.TPRM.value, body=query
        )
        if response["hits"]["hits"]:
            if response["hits"]["hits"][0]["_source"]:
                return response["hits"]["hits"][0]["_source"]["new_value"]

        return False

    @staticmethod
    def _convert_parameter_value_single(parameter_value: str, value_type: str):
        match value_type:
            case "int" | "two-way link":
                if "." in parameter_value:
                    return int(float(parameter_value))
                return int(parameter_value)

            case "float":
                return float(parameter_value)

            case "bool":
                conditions = {
                    "true": True,
                    "false": False,
                }
                return conditions[parameter_value.lower()]

            case "mo_link":
                query = {
                    "query": {
                        "bool": {
                            "filter": [
                                {"term": {"instance_id": int(parameter_value)}},
                                {"term": {"attribute": "name"}},
                                {"term": {"is_active": True}},
                            ]
                        }
                    }
                }
                return elastic_client.search(
                    index=InventoryChangesIndexes.MO.value, body=query
                )["hits"]["hits"][0]["_source"]["new_value"]

            case "prm_link":
                query = {
                    "query": {
                        "bool": {
                            "filter": [
                                {"term": {"instance_id": int(parameter_value)}},
                                {"term": {"attribute": "value"}},
                                {"term": {"is_active": True}},
                            ]
                        }
                    }
                }
                return elastic_client.search(
                    index=InventoryChangesIndexes.PRM.value, body=query
                )["hits"]["hits"][0]["_source"]["new_value"]

            case _:
                return parameter_value

    @staticmethod
    def _convert_parameter_value_multiple(
        parameter_value: list, value_type: str
    ):
        match value_type:
            case "int" | "two-way link":
                new_value = []
                for unit in parameter_value:
                    if "." in parameter_value:
                        new_value.append(int(float(unit)))
                        continue
                    new_value.append(int(float(unit)))
                return new_value

            case "float":
                return [float(unit) for unit in parameter_value]

            case "bool":
                new_value = []
                for unit in parameter_value:
                    if unit.lower() == "true":
                        new_value.append(True)
                        continue

                    new_value.append(False)

                return new_value

            case "mo_link":
                new_value = []
                for unit in parameter_value:
                    query = {
                        "query": {
                            "bool": {
                                "filter": [
                                    {"term": {"instance_id": int(unit)}},
                                    {"term": {"attribute": "name"}},
                                    {"term": {"is_active": True}},
                                ]
                            }
                        }
                    }
                    new_value.append(
                        elastic_client.search(
                            index=InventoryChangesIndexes.MO.value, body=query
                        )["hits"]["hits"][0]["_source"]["new_value"]
                    )
                return new_value

            case "prm_link":
                new_value = []
                for unit in parameter_value:
                    query = {
                        "query": {
                            "bool": {
                                "filter": [
                                    {"term": {"instance_id": int(unit)}},
                                    {"term": {"attribute": "value"}},
                                    {"term": {"is_active": True}},
                                ]
                            }
                        }
                    }
                    new_value.append(
                        elastic_client.search(
                            index=InventoryChangesIndexes.PRM.value, body=query
                        )["hits"]["hits"][0]["_source"]["new_value"]
                    )
                return new_value

            case _:
                return parameter_value

    def convert(self, parameter_instance: ParameterInstance):
        is_multiple = self._get_parameter_type_attribute_by_id(
            parameter_type_id=parameter_instance.tprm_id,
            attribute="multiple",
        )
        val_type = self._get_parameter_type_attribute_by_id(
            parameter_type_id=parameter_instance.tprm_id,
            attribute="val_type",
        )

        if not val_type:
            val_type = "str"

        if is_multiple:
            value = pickle.loads(bytes.fromhex(parameter_instance.value))
            return value

        return self._convert_parameter_value_single(
            parameter_value=parameter_instance.value, value_type=val_type
        )
