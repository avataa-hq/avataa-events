import os

ES_PROTOCOL = os.environ.get("ES_PROTOCOL", "https")
ES_HOST = os.environ.get("ES_HOST", "elasticsearch")
ES_PORT = os.environ.get("ES_PORT", "9200")
ES_PASS = os.environ.get("ES_PASS", "")
ES_USER = os.environ.get("ES_USER", "event_manager_user")
ES_URL = f"{ES_PROTOCOL}://{ES_HOST}"

if ES_PORT:
    ES_URL += f":{ES_PORT}"
