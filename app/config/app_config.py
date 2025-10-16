import os

DEBUG = os.environ.get("DEBUG", "False").upper() in ("TRUE", "Y", "YES", "1")

APP_TITLE = "Event Manager"
APP_PREFIX = f"/api/{APP_TITLE.replace(' ', '_').lower()}"

APP_VERSION = "1"

V1_OPTIONS = {
    "root_path": f"{APP_PREFIX}/v{APP_VERSION}",
    "title": APP_TITLE,
    "version": APP_VERSION,
}
