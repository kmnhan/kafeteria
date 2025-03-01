"""Handles sending today's menu to the slack channel.

For more information on how to use this module, refer to the README.md file.
"""

import asyncio
import datetime
import logging
import os
from typing import Literal, cast

import slack_sdk

from kafeteria.core import Cafeteria, _make_url, get_menus

_DAYS_OF_WEEK = ("월", "화", "수", "목", "금", "토", "일")

logger = logging.getLogger(__name__)
client = slack_sdk.WebClient(token=os.environ.get("KAFETERIA_SLACK_BOT_TOKEN"))


def _send_message(message: str | list[str]):
    """Send a message to the slack channel."""
    if isinstance(message, list):
        message = "\n".join(message)
    try:
        _ = client.chat_postMessage(
            channel=os.environ.get("KAFETERIA_SLACK_CID"),
            text=message,
            mrkdwn=True,
            unfurl_links=False,
        )
    except slack_sdk.errors.SlackApiError:
        logger.exception("Error posting message")


def _indent_lines(s: str) -> str:
    return "\n".join([f"\t{line}" for line in s.split("\n")])


def _make_message() -> list[str]:
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
        f"{date.strftime('%-m월 %-d일')} ({_DAYS_OF_WEEK[date.weekday()]})"
    )

    output: list[str] = [f":knife_fork_plate: *{formatted_date} {menu_key}* :yum:"]

    for cafeteria, menu in zip(
        cafeteria_list, asyncio.run(get_menus(cafeteria_list, date)), strict=True
    ):
        link = _make_url(cafeteria, date)
        header = f"*{menu['식당']}* " + menu[f"{menu_key}시간"]
        output.append(f"<{link}|{header}>")
        output.append(_indent_lines(menu[menu_key]) + "\n")

    return output


def publish():
    """Send today's menu to the slack channel."""
    _send_message(_make_message())
    logger.info("Message sent")
