import datetime
import random
from datetime import timedelta
from typing import Any

from nonebot import get_driver
from nonebot import get_plugin_config
from nonebot import logger
from nonebot import on_command
from nonebot import on_fullmatch
from nonebot import require
from nonebot.adapters import Event
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot as OneBot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.params import Fullmatch
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

from .config import Config
from .reply import replies
from .model import UserDict, get_user, User
from .utils import is_blank

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
sexy_value = on_command("我要色色")
lucky_value = on_command("看运气")


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


async def get_user_info(bot: OneBot, event: Event):
    user_id = event.get_user_id()
    user = get_user(user_id)
    user_info = await bot.get_stranger_info(user_id=int(user_id))
    return user_id, user, user_info


@query_status.handle()
async def query_status_handler(bot: OneBot, event: Event):
    user_id, user, user_info = await get_user_info(bot, event)
    await bot.send(event,
                   f"""{user_info["nickname"]} 现在有 {user.energy_value} 点精液值\n已连续签到 {user.check_in_count} 天""",
                   reply_message=True)


@admin_check.handle()
async def admin_check_handler(bot: OneBot, event: Event, args: Message = CommandArg()):
    if user_id := args.extract_plain_text():
        user = get_user(user_id)
        await bot.send(event, user.model_dump_json(), reply_message=True)
    else:
        await bot.send(event, "不知道你要看谁!", reply_message=True)


async def get_group_member_info(bot: OneBot, event: GroupMessageEvent):
    user_id = event.get_user_id()
    user = get_user(user_id)
    user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=int(user_id))
    return user_id, user, user_info


def card_or_nickname(user_info: dict[str, Any]) -> Any:
    card = user_info.get("card", None)
    if is_blank(card):
        return user_info.get("nickname", None)

    return card


@sexy_value.handle()
async def sexy_value_handler(bot: OneBot, event: GroupMessageEvent):
    user_id, user, user_info = await get_group_member_info(bot, event)
    today = datetime.date.today()

    if user.sexy_value_acquisition_date != today:
        user.sexy_value = round(random.uniform(0, 100), 2)
        user.sexy_value_acquisition_date = today

        match user.sexy_value:
            case v if 0 <= v <= 40:
                check_in(user_id, 1.0)
            case v if 40 < v <= 60:
                check_in(user_id, 2.0)
            case v if 60 < v <= 80:
                check_in(user_id, 2.5)
            case v if 80 < v <= 90:
                check_in(user_id, 3.0)
            case _:
                check_in(user_id, 4.0)

    __reply = ""
    match user.sexy_value:
        case v if 0 <= v <= 1:
            __reply = f"...{v}%, 这么低的性欲水平, 今天你就做群里大家的胶犬好好积攒色色能量吧! 要前锁后塞, 尿道也不可以放过, 乖乖张嘴收集大家的色色能量吧!"
        case v if 1 < v <= 10:
            __reply = f"...sad, 你今天的性欲水平只打败了 {v}% 的人, 色色能量严重不足啦uwu 建议前锁后塞并塞上尿道堵禁欲别射了嗷!"
        case v if 10 < v <= 20:
            __reply = f"...咳咳, 你今天的性欲水平只打败了 {v}% 的人, 昨天一定没少冲吧? 建议戴锁恢复一下色色能量嗷!"
        case v if 20 < v <= 40:
            __reply = f"...hmmm, 你今天的性欲水平只打败了 {v}% 的人, 低于正常水平, 多刷点推特好男人来激发色色能量嗷!"
        case v if 40 < v <= 60:
            __reply = f"...oh, 你今天的性欲水平打败了 {v}% 的人, 处于正常水平www 今天愉快的对着 xp 男人冲一发吧!"
        case v if 60 < v <= 80:
            __reply = f"...oh, 你今天的性欲水平打败了 {v}% 的人, 中等偏上哦, 今天记得射精两发并拍照发在群里打卡!"
        case v if 80 < v <= 90:
            __reply = f"...wow, 你今天的性欲水平打败了 {v}% 的人! 鸡鸡要爆掉啦, 赶快找个男人射爆他! 记得偷偷录像, 群友都想看!"
        case v if 90 < v < 99:
            __reply = f"...震惊!!! 你今天的性欲水平打败了 {v}% 的人! 色色能量满溢而出啦, 快去找十个男人开房做爱吧! 淫乱 party 记得录像了发群里哦!"
        case _:
            __reply = f"...{v}%, 你今天的性欲水平打败了几乎所有人, 今天就做大家的胶犬 rbq 吧! 想射的话, 要在肚子里收集每个人的精液才行哦!"

    await bot.send(event, f"""让我看看...{card_or_nickname(user_info)}{__reply}""", reply_message=True)


@lucky_value.handle()
async def lucky_value_handler(bot: OneBot, event: GroupMessageEvent):
    user_id, user, user_info = await get_group_member_info(bot, event)
    today = datetime.date.today()

    if user.lucky_value_acquisition_date != today:
        user.lucky_value = round(random.uniform(0, 100), 2)
        user.lucky_value_acquisition_date = today
        check_in(user_id, user.lucky_value / 100 + 1.5)

    await bot.send(event, f"""今天的 {card_or_nickname(user_info)} 比 {user.lucky_value}% 的人更幸运www""",
                   reply_message=True)
