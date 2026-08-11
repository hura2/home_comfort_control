from api.smart_home_devices.switchbot_api import SwitchBotApi


if __name__ == "__main__":
    r = SwitchBotApi().get_device_list()
    print(r)