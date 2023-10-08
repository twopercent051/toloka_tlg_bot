from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    home = State()
    settings = State()
    users_profile = State()
    balance = State()
    send_message = State()


class UsersFSM(StatesGroup):
    home = State()
    send_message = State()
    quantity = State()
    followings_url = State()
    repost_text = State()
    get_work_repost_url = State()
