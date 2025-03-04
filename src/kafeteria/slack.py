"""Handles sending today's menu to the slack channel.

For more information on how to use this module, refer to the README.md file.
"""

import asyncio
import datetime
import logging
import os
from typing import Literal, cast

import holidayskr
import slack_sdk
from slack_sdk.web.async_client import AsyncWebClient

from kafeteria.core import Cafeteria, _make_url, get_menus

_DAYS_OF_WEEK = ("월", "화", "수", "목", "금", "토", "일")

logger = logging.getLogger(__name__)

client = AsyncWebClient(token=os.environ.get("KAFETERIA_SLACK_BOT_TOKEN"))


async def _send_message(message: str | list[str]):
    """Send a message to the slack channel asynchronously."""
    if isinstance(message, list):
        message = "\n".join(message)
    try:
        await client.chat_postMessage(
            channel=os.environ.get("KAFETERIA_SLACK_CID"),
            text=message,
            mrkdwn=True,
            unfurl_links=False,
        )
    except slack_sdk.errors.SlackApiError:
        logger.exception("Error posting message")


def _indent_lines(s: str) -> str:
    return "\n".join([f"\t{line}" for line in s.split("\n")])


async def make_message() -> list[str]:
    """Compose the message to send to the slack channel."""
    now = datetime.datetime.now(datetime.timezone(offset=datetime.timedelta(hours=9)))

    menu_time = int(os.environ.get("KAFETERIA_MENU_TIME", 0))

    if menu_time == 0:
        if now.time() <= datetime.time(9, 0):
            menu_time = 1
        elif now.time() <= datetime.time(14, 0):
            menu_time = 2
        elif now.time() <= datetime.time(19, 30):
            menu_time = 3
        else:
            now = now + datetime.timedelta(days=1)
            menu_time = 1

    menu_key: Literal["조식", "중식", "석식"] = ("조식", "중식", "석식")[menu_time - 1]

    cafeteria_list = cast(
        list[Cafeteria],
        [
            s.strip()
            for s in os.environ.get("KAFETERIA_LIST", "fclt,west,east1,east2")
            .strip()
            .split(",")
        ],
    )
    date: datetime.date = now.date()

    formatted_date: str = (
        f"{date.month}월 {date.day}일 ({_DAYS_OF_WEEK[date.weekday()]})"
    )

    output: list[str] = [f":knife_fork_plate: *{formatted_date} {menu_key}* :yum:"]

    menus = await get_menus(cafeteria_list, date)
    for cafeteria, menu in zip(cafeteria_list, menus, strict=True):
        link = _make_url(cafeteria, date)
        header = f"*{menu['식당']}* " + menu[f"{menu_key}시간"]
        output.append(f"<{link}|{header}>")
        output.append(_indent_lines(menu[menu_key]) + "\n")

    return output


async def publish(*, skip_holiday: bool = False) -> None:
    """Send today's menu to the slack channel.

    Parameters
    ----------
    skip_holiday : bool
        If True, the message will not be sent if today is a holiday.
    """
    if skip_holiday:
        now = datetime.datetime.now(
            datetime.timezone(offset=datetime.timedelta(hours=9))
        )
        is_holiday: bool = any(
            holiday[0] == now.date()
            for holiday in holidayskr.year_holidays(str(now.year))
        )
        if is_holiday:
            logger.info("Today is a holiday. Skipping the publication.")
            return

    await _send_message(await make_message())
    logger.info("Message sent")


def run_publish(*, skip_holiday: bool = False) -> None:
    """Run `publish` synchronously."""
    asyncio.run(publish(skip_holiday=skip_holiday))
