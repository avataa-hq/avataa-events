from enum import Enum


class AvailableInventoryInstances(Enum):
    TMO = "TMO"
    MO = "MO"
    TPRM = "TPRM"
    PRM = "PRM"

    @staticmethod
    def get_instances():
        return list(AvailableInventoryInstances.__members__.keys())


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

INSTANCES_BATCH_SIZE = 10_000
