import random

from nonebot import get_plugin_config
from nonebot import on_fullmatch
from nonebot.params import Fullmatch
from nonebot.plugin import PluginMetadata

from .config import Config
from .reply import replies

__plugin_meta__ = PluginMetadata(
    name="kggbot",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

# define commands
say_hi = on_fullmatch(tuple(replies.keys()), ignorecase=True)


@say_hi.handle()
async def say_hi_handler(content: str = Fullmatch()):
    await say_hi.finish(random.choice(replies[content]))
