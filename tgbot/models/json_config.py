import json


def get_config(key: str):
    with open("config.json") as config_file:
        data = json.loads(config_file.read())
    try:
        return data[key]
    except KeyError:
        return 0
