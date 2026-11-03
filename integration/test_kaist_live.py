"""Check the menu parser against the live KAIST website.

Run separately from the offline test suite with ``pytest integration``.
"""

from datetime import datetime, timedelta, timezone

import pytest

from kafeteria import Menu, get_menu


@pytest.mark.asyncio
@pytest.mark.parametrize("cafeteria", ["fclt", "west", "east1", "east2"])
async def test_live_menu(cafeteria):
    selected_date = datetime.now(timezone(timedelta(hours=9))).date()
    menu = await get_menu(cafeteria, selected_date)

    assert set(menu) == set(Menu.__annotations__)
    assert all(isinstance(value, str) for value in menu.values())
    assert menu["식당"]
    assert menu["날짜"].startswith(selected_date.strftime("%m/%d"))
