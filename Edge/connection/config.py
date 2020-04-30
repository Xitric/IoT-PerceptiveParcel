import ujson
import os

CONFIG_FILE = "config.json"

def get_string(key: str):
    if CONFIG_FILE in os.listdir():
        config = __read_config()
        return config.get(key)

def get_float(key: str):
    value = get_string(key)
    return float(value) if value else None

def set_value(key: str, value):
    if not CONFIG_FILE in os.listdir():
        config = {}
    else:
        config = __read_config()

    config[key] = value

    with open(CONFIG_FILE, "w") as config_file:
        config_file.write(ujson.dumps(config))

def __read_config():
    with open(CONFIG_FILE, "r") as config_file:
        return ujson.loads("".join(config_file.readlines()))
