import datetime as dt

import aiohttp
import pytest

from kafeteria import InvalidCafeteriaError, Menu, get_menus


@pytest.fixture
def menu_requests(monkeypatch):
    requests = []

    class Response:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def text(self):
            return """<div class="item" id="tab_item_1">
<h3>[ 서측식당 ] 메뉴 10/01(일)</h3>
<p>설명</p>
<th scope="col">조식 08:00</th>
<th scope="col">중식 12:00</th>
<th scope="col">석식 18:00</th>
<!-- <ul class="list-1st"> -->아침<!-- </ul> -->
<ul class="list-1st">점심</ul>
<ul class="list-1st">저녁</ul>"""

    def get(_session, url):
        requests.append(url)
        return Response()

    monkeypatch.setattr(aiohttp.ClientSession, "get", get)
    return requests


@pytest.mark.asyncio
async def test_get_menus_valid_cafeterias(menu_requests):
    cafeteria_list = ["fclt", "west", "east1", "east2", "emp", "icc", "hawam", "seoul"]
    selected_date = dt.date(2023, 10, 1)
    menus = await get_menus(cafeteria_list, selected_date)
    assert menu_requests == [
        "https://kaist.ac.kr/kr/html/campus/053001.html?"
        f"dvs_cd={cafeteria}&stt_dt=2023-10-01"
        for cafeteria in cafeteria_list
    ]
    assert len(menus) == len(cafeteria_list)
    for menu in menus:
        assert set(menu) == set(Menu.__annotations__)
        assert menu["식당"] == "서측식당"
        assert (menu["조식"], menu["중식"], menu["석식"]) == ("아침", "점심", "저녁")


@pytest.mark.asyncio
async def test_get_menus_invalid_cafeteria():
    cafeteria_list = ["invalid"]
    selected_date = dt.date(2023, 10, 1)
    with pytest.raises(InvalidCafeteriaError) as exc_info:
        await get_menus(cafeteria_list, selected_date)
    for code in ("fclt", "west", "east1", "east2", "emp", "icc", "hawam", "seoul"):
        assert repr(code) in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_menus_no_date(menu_requests):
    cafeteria_list = ["fclt", "west"]
    korea = dt.timezone(dt.timedelta(hours=9))
    before = dt.datetime.now(korea).date()
    menus = await get_menus(cafeteria_list)
    after = dt.datetime.now(korea).date()
    assert len(menus) == len(cafeteria_list)
    assert len(menu_requests) == len(cafeteria_list)
    for cafeteria, url in zip(cafeteria_list, menu_requests, strict=True):
        assert url in {
            "https://kaist.ac.kr/kr/html/campus/053001.html?"
            f"dvs_cd={cafeteria}&stt_dt={date.isoformat()}"
            for date in (before, after)
        }


@pytest.mark.asyncio
async def test_get_menus_empty_list():
    cafeteria_list = []
    menus = await get_menus(cafeteria_list)
    assert menus == []
