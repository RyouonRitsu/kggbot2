import datetime
import random
from datetime import timedelta

from nonebot import get_driver
from nonebot import get_plugin_config
from nonebot import logger
from nonebot import on_command
from nonebot import on_fullmatch
from nonebot import require
from nonebot.adapters import Event
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.params import CommandArg
from nonebot.params import Fullmatch
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

from .config import Config
from .reply import replies
from .model import UserDict, get_user

__plugin_meta__ = PluginMetadata(
    name="kggbot",
    description="",
    usage="",
    config=Config,
)

driver = get_driver()
config = get_plugin_config(Config)
users_data = store.get_plugin_data_file("users_data")

# define commands
say_hi = on_fullmatch(tuple(replies.keys()), ignorecase=True)
query_status = on_command("状态", aliases={"status", "查询状态"})
admin_check = on_command("check", permission=SUPERUSER)


@driver.on_startup
async def set_up():
    if users_data.is_file():
        model.user_dict = UserDict.model_validate_json(users_data.read_text())
    else:
        model.user_dict = UserDict(user_id_2_user={})

    logger.info(f"[set_up] loaded {len(model.user_dict.user_id_2_user)} users")


@driver.on_shutdown
async def tear_down():
    users_data.write_text(model.user_dict.model_dump_json())
    logger.info(f"[tear_down] saved {len(model.user_dict.user_id_2_user)} users")


def check_in(user_id: str, percent: float) -> bool:
    user = get_user(user_id)
    today = datetime.date.today()

    # already checked in today
    if user.check_in_date == today:
        return False

    # has checked in yesterday
    if user.check_in_date == (today - timedelta(days=1)):
        user.check_in_count += 1
    else:
        user.check_in_count = 1

    user.check_in_date = today
    value = int(round(4 * percent * (1 + user.check_in_count / 10.0), 0))
    user.energy_value += value

    return True


@say_hi.handle()
async def say_hi_handler(bot: OneBot, event: Event, content: str = Fullmatch()):
    user_id = event.get_user_id()

    if content == "kgg":
        check_in(user_id, 1.0)
    else:
        check_in(user_id, 2.7)

    await bot.send(event, random.choice(replies[content]), reply_message=True)


@query_status.handle()
async def query_status_handler(bot: OneBot, event: Event):
    user_id = event.get_user_id()
    user = get_user(user_id)
    user_info = await bot.get_stranger_info(user_id=int(user_id))
    await bot.send(event,
                   f"""{user_info["nickname"]} 现在有 {user.energy_value} 点精液值\n已连续签到 {user.check_in_count} 天""",
                   reply_message=True)


@admin_check.handle()
async def admin_check_handler(bot: OneBot, event: Event, args: Message = CommandArg()):
    if user_id := args.extract_plain_text():
        user = get_user(user_id)
        await bot.send(event, user.model_dump_json())
    else:
        await bot.send(event, "不知道你要看谁!", reply_message=True)
