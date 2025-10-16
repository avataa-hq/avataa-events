from elasticsearch import Elasticsearch

from common.constants import InventoryChangesIndexes
from config.elastic_config import ES_URL, ES_PROTOCOL, ES_PASS, ES_USER

if ES_PROTOCOL == "https":
    print("Creating certified client...")
    elastic_client = Elasticsearch(
        ES_URL,
        # ca_certs="./elastic/ca.crt",
        verify_certs=False,  # Disable  s SSL verification
        http_auth=(ES_USER, ES_PASS),
        retry_on_status=(500, 502, 503, 504),
        max_retries=5,
        request_timeout=10000,
        retry_on_timeout=True,
    )

else:
    print("Creating client...")
    elastic_client = Elasticsearch(ES_URL)


def create_basic_indexes_if_not_exists():
    print(ES_URL)
    indexes_list = [
        InventoryChangesIndexes.TMO.value,
        InventoryChangesIndexes.MO.value,
        InventoryChangesIndexes.TPRM.value,
        InventoryChangesIndexes.PRM.value,
    ]

    for index in indexes_list:
        if elastic_client.indices.exists(index=index):
            continue

        elastic_client.indices.create(
            index=index,
            body={
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1,
                    "refresh_interval": "1s",
                },
                "mappings": {
                    "dynamic": "false",
                    "properties": {
                        "event_type": {"type": "keyword"},
                        "user_id": {
                            "type": "long",
                            "ignore_malformed": True,
                            "null_value": None,
                        },
                        "session_id": {"type": "keyword", "null_value": None},
                        "instance_id": {"type": "long"},
                        "attribute": {"type": "keyword"},
                        "version": {"type": "integer"},
                        "valid_to": {
                            "type": "date",
                            "ignore_malformed": True,
                            "null_value": None,
                        },
                        "is_active": {"type": "boolean"},
                        "valid_from": {"type": "date"},
                    },
                    "runtime": {
                        "old_value_num": {
                            "type": "double",
                            "script": """
def v = params._source.old_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof Number) emit(((Number)x).doubleValue()); } }
else if (v instanceof Number) { emit(((Number)v).doubleValue()); }
""",
                        },
                        "new_value_num": {
                            "type": "double",
                            "script": """
def v = params._source.new_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof Number) emit(((Number)x).doubleValue()); } }
else if (v instanceof Number) { emit(((Number)v).doubleValue()); }
""",
                        },
                        "old_value_str": {
                            "type": "keyword",
                            "script": """
def v = params._source.old_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof String) emit(x); } }
else if (v instanceof String) { emit(v); }
""",
                        },
                        "new_value_str": {
                            "type": "keyword",
                            "script": """
def v = params._source.new_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof String) emit(x); } }
else if (v instanceof String) { emit(v); }
""",
                        },
                        "old_value_bool": {
                            "type": "boolean",
                            "script": """
def v = params._source.old_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof Boolean) emit(x); } }
else if (v instanceof Boolean) { emit(v); }
""",
                        },
                        "new_value_bool": {
                            "type": "boolean",
                            "script": """
def v = params._source.new_value;
if (v == null) return;
if (v instanceof List) { for (def x : (List)v) { if (x instanceof Boolean) emit(x); } }
else if (v instanceof Boolean) { emit(v); }
""",
                        },
                        "old_value_dt": {
                            "type": "date",
                            "script": """
def v = params._source.old_value;
if (v == null) return;
if (v instanceof List) {
  for (def x : (List)v) {
    if (x == null) continue;
    if (x instanceof String) {
      try { emit(java.time.Instant.parse(x).toEpochMilli()); }
      catch (Exception e1) {
        try { emit(java.time.ZonedDateTime.parse(x).toInstant().toEpochMilli()); }
        catch (Exception e2) {}
      }
    } else if (x instanceof Number) {
      emit(((Number)x).longValue()); // epoch millis
    }
  }
} else {
  if (v instanceof String) {
    try { emit(java.time.Instant.parse(v).toEpochMilli()); }
    catch (Exception e1) {
      try { emit(java.time.ZonedDateTime.parse(v).toInstant().toEpochMilli()); }
      catch (Exception e2) {}
    }
  } else if (v instanceof Number) {
    emit(((Number)v).longValue()); // epoch millis
  }
}
""",
                        },
                        "new_value_dt": {
                            "type": "date",
                            "script": """
def v = params._source.new_value;
if (v == null) return;
if (v instanceof List) {
  for (def x : (List)v) {
    if (x == null) continue;
    if (x instanceof String) {
      try { emit(java.time.Instant.parse(x).toEpochMilli()); }
      catch (Exception e1) {
        try { emit(java.time.ZonedDateTime.parse(x).toInstant().toEpochMilli()); }
        catch (Exception e2) {}
      }
    } else if (x instanceof Number) {
      emit(((Number)x).longValue()); // epoch millis
    }
  }
} else {
  if (v instanceof String) {
    try { emit(java.time.Instant.parse(v).toEpochMilli()); }
    catch (Exception e1) {
      try { emit(java.time.ZonedDateTime.parse(v).toInstant().toEpochMilli()); }
      catch (Exception e2) {}
    }
  } else if (v instanceof Number) {
    emit(((Number)v).longValue()); // epoch millis
  }
}
""",
                        },
                        "old_value_len": {
                            "type": "long",
                            "script": """
def v = params._source.old_value;
if (v instanceof List) emit(((List)v).size());
""",
                        },
                        "new_value_len": {
                            "type": "long",
                            "script": """
def v = params._source.new_value;
if (v instanceof List) emit(((List)v).size());
""",
                        },
                    },
                },
            },
        )
