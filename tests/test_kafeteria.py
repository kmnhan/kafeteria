import datetime

import pytest

from kafeteria import InvalidCafeteriaError, Menu, get_menus


@pytest.mark.asyncio
async def test_get_menus_valid_cafeterias():
    cafeteria_list = ["fclt", "west", "east1", "east2"]
    dt = datetime.date(2023, 10, 1)
    menus = await get_menus(cafeteria_list, dt)
    assert len(menus) == len(cafeteria_list)
    for menu in menus:
        assert isinstance(menu, dict)
        assert all(key in menu for key in Menu.__annotations__)


@pytest.mark.asyncio
async def test_get_menus_invalid_cafeteria():
    cafeteria_list = ["invalid"]
    dt = datetime.date(2023, 10, 1)
    with pytest.raises(InvalidCafeteriaError):
        await get_menus(cafeteria_list, dt)


@pytest.mark.asyncio
async def test_get_menus_no_date():
    cafeteria_list = ["fclt", "west"]
    menus = await get_menus(cafeteria_list)
    assert len(menus) == len(cafeteria_list)
    for menu in menus:
        assert isinstance(menu, dict)
        assert all(key in menu for key in Menu.__annotations__)


@pytest.mark.asyncio
async def test_get_menus_empty_list():
    cafeteria_list = []
    menus = await get_menus(cafeteria_list)
    assert menus == []
