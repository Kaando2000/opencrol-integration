"""Constants for OpenCtrol integration."""

DOMAIN = "opencrol"

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BROKER = "mqtt_broker"
CONF_AUTH_KEY = "auth_key"
CONF_CLIENT_ID = "client_id"

# MQTT Topics
TOPIC_COMMAND = "opencrol/{client_id}/command"
TOPIC_STATUS = "opencrol/{client_id}/status"
TOPIC_SCREEN = "opencrol/{client_id}/screen"
TOPIC_AUDIO = "opencrol/{client_id}/audio"
TOPIC_DEVICES = "opencrol/{client_id}/devices"
TOPIC_APPS = "opencrol/{client_id}/apps"

# Services
SERVICE_MOVE_MOUSE = "move_mouse"
SERVICE_CLICK = "click"
SERVICE_TYPE_TEXT = "type_text"
SERVICE_SEND_KEY = "send_key"
SERVICE_SET_APP_VOLUME = "set_app_volume"
SERVICE_SET_APP_DEVICE = "set_app_device"
SERVICE_TAKE_SCREENSHOT = "take_screenshot"

# Attributes
ATTR_X = "x"
ATTR_Y = "y"
ATTR_BUTTON = "button"
ATTR_TEXT = "text"
ATTR_KEY = "key"
ATTR_KEYS = "keys"
ATTR_PROCESS_ID = "process_id"
ATTR_VOLUME = "volume"
ATTR_DEVICE_ID = "device_id"
ATTR_CLIENT_ID = "client_id"

# Status
STATE_ONLINE = "online"
STATE_OFFLINE = "offline"
STATE_CONNECTING = "connecting"

