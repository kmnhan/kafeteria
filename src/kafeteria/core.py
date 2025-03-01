__all__ = [
    "Cafeteria",
    "InvalidCafeteriaError",
    "Menu",
    "MenuParsingError",
    "get_menu",
    "get_menus",
]

import asyncio
import datetime
import html
import re
from typing import Literal, TypedDict, get_args, get_type_hints

import aiohttp

Cafeteria = Literal["fclt", "west", "east1", "east2", "emp", "icc", "hawam", "seoul"]
"""
Valid cafeteria codes.

- "fclt": 카이마루
- "west": 서측식당
- "east1": 동측 학생식당
- "east2": 동측 교직원식당
- "emp": 교수회관
- "icc": 문지캠퍼스
- "hawam": 화암 기숙사식당
- "seoul": 서울캠퍼스 구내식당

"""


class Menu(TypedDict):
    """A dictionary representing the menu for a single day."""

    식당: str
    날짜: str
    설명: str
    조식시간: str
    중식시간: str
    석식시간: str
    조식: str
    중식: str
    석식: str


class InvalidCafeteriaError(ValueError):
    """Raised when an invalid cafeteria code is provided."""

    def __init__(self, cafeteria: str):
        super().__init__(
            f"Invalid cafeteria code: {cafeteria}, must be one of {get_args(Cafeteria)}"
        )


class MenuParsingError(RuntimeError):
    """Raised when the menu cannot be parsed."""

    def __init__(self):
        super().__init__("Failed to parse menu")


FOOD_PATTERN = re.compile(
    r"<div class=\"item\" id=\"tab_item_1\">[\s]*?<h3>\[ ([가-힣 ]+) \].+?(\d{2}\/\d{2}\([가-힣]\))<\/h3>[\s]*?<p>([\s\S]*?)\s*?<\/p>[\s\S]*?<th scope=\"col\">조식 (.*?)<\/th>[\s]*?<th scope=\"col\">중식 (.*?)<\/th>[\s]*?<th scope=\"col\">석식 (.*?)<\/th>[\s\S]*?<!-- <ul class=\"list-1st\"> -->[\s]*([\s\S]*?)[\s]*(?:<br\/>)?[\s]*<!-- <\/ul> -->[\s\S]*?<ul class=\"list-1st\">[\s]*([\s\S]*?)[\s]*(?:<br\/>)?[\s]*<\/ul>[\s\S]*?<ul class=\"list-1st\">[\s]*([\s\S]*?)[\s]*(?:<br\/>)?[\s]*<\/ul>"  # noqa: E501
)
"""Regex pattern to extract menu information from the KAIST website."""


def _make_url(cafeteria: Cafeteria, dt: datetime.date) -> str:
    return (
        "http://kaist.ac.kr/kr/html/campus/053001.html?"
        f"dvs_cd={cafeteria}&"
        f"stt_dt={dt.strftime('%Y-%m-%d')}"
    )


def _parse_group(group: str) -> str:
    return (
        html.unescape(group)
        .replace("<br />", "")
        .replace("<br/>", "")
        .strip()
        .replace("\r", "\n")
    )


async def get_menu(cafeteria: Cafeteria, dt: datetime.date | None = None) -> Menu:
    """
    Retrieve the menu for a specified cafeteria on a given date from the KAIST website.

    Parameters
    ----------
    cafeteria : CafeteriaCode
        Code for the cafeteria. Must be one of "fclt", "west", "east1", "east2", "emp",
        "icc".
    dt : datetime.date, optional
        Date object representing the date to retrieve the menu for. If None, the current
        date is used.

    Returns
    -------
    Menu
        A dictionary representing the menu for the specified cafeteria on the specified
        date.

    Example
    -------
    >>> menu = await get_menu("fclt")
    """
    if dt is None:
        dt = datetime.datetime.now(
            datetime.timezone(offset=datetime.timedelta(hours=9))
        ).date()

    if cafeteria not in get_args(Cafeteria):
        raise InvalidCafeteriaError(cafeteria)

    async with (
        aiohttp.ClientSession() as session,
        session.get(_make_url(cafeteria, dt)) as response,
    ):
        src = await response.text()

    groups = FOOD_PATTERN.search(src).groups()
    if groups is None:
        raise MenuParsingError

    return dict(
        zip(get_type_hints(Menu).keys(), (_parse_group(s) for s in groups), strict=True)
    )


async def get_menus(
    cafeteria_list: list[Cafeteria], dt: datetime.date | None = None
) -> list[Menu]:
    """
    Retrieve the menus for multiple cafeterias on a given date from the KAIST website.

    Example
    -------
    >>> menus = await get_menus(["fclt", "west", "east1", "east2"])
    """
    coroutines = [get_menu(cafeteria, dt) for cafeteria in cafeteria_list]
    return await asyncio.gather(*coroutines)
