# Kafeteria

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/kafeteria?logo=python&logoColor=white)](https://pypi.org/project/kafeteria/)
[![PyPi](https://img.shields.io/pypi/v/kafeteria?logo=pypi&logoColor=white)](https://pypi.org/project/kafeteria/)
[![CI](https://github.com/kmnhan/kafeteria/actions/workflows/ci.yml/badge.svg)](https://github.com/kmnhan/kafeteria/actions/workflows/ci.yml)

Kafeteria is a Python package to asynchronously access the menu of the cafeterias at KAIST.

KAIST 학식 메뉴를 asyncio를 사용하여 불러올 수 있는 Python 패키지입니다.

## Installation

Install the package using pip:

```bash
pip install kafeteria
```

If you want optional Slack integration, install with the `slack` extra:

```bash
pip install kafeteria[slack]
```

## Usage

Use the `get_menu` function to get the menu for a specific cafeteria, or the `get_menus` function to get the menus for multiple cafeterias at once.

Valid cafeteria codes are:

- `fclt` : 카이마루
- `west` : 서측식당
- `east1` : 동측 학생식당
- `east2` : 동측 교직원식당
- `emp` : 교수회관
- `icc` : 문지캠퍼스
- `hawam` : 화암 기숙사식당
- `seoul` : 서울캠퍼스 구내식당

Here's an example:

```python
import asyncio
import datetime
import kafeteria


async def main():
    # Get the menu for a specific cafeteria
    menu = await kafeteria.get_menu("fclt")
    print(menu)

    # Get the menu for a specific date
    menu = await kafeteria.get_menu("fclt", datetime.date(2025, 1, 3))
    print(menu)

    # Get the menus for multiple cafeterias at once
    menus = await kafeteria.get_menus(["fclt", "east1", "east2"])
    print(menus)


asyncio.run(main())
```

## Slack Integration

You can also publish today's menu to a Slack channel using the `kafeteria.slack.publish` function.

First, you need to [set up a Slack app](https://api.slack.com/quickstart#creating) with the `chat:write` permission. Once you have a bot set up with the necessary permissions, set the following environment variables:

- `KAFETERIA_SLACK_BOT_TOKEN` (required): The bot token for the Slack app.

- `KAFETERIA_SLACK_CHANNEL` (required): The channel ID to post the message to.

  This can be found by right-clicking on the channel in the Slack app and selecting "Copy link". The channel ID is the last part of the URL.

  For more information, see the [slack api documentation](https://api.slack.com/messaging/sending>).

- `KAFETERIA_MENU_TIME` (optional): The menu to send.

  This can be one of 0, 1, 2, or 3. The behavior is as follows:

  - 1: breakfast
  - 2: lunch
  - 3: dinner
  - 0: default, automatically selects the menu based on the current time:

    - breakfast: 19:30 - 09:00
    - lunch: 09:00 - 14:00
    - dinner: 14:00 - 19:30

- `KAFETERIA_LIST` (optional): The list of cafeterias to send the menu for.

  This should be a comma-separated list of cafeteria codes. By default, `fclt,west,east1,east2` is used.

Then, you can publish the menu to a channel using `kafeteria.slack.publish()`:

```python
import asyncio
import kafeteria.slack

asyncio.run(kafeteria.slack.publish())
```

A shortcut function `kafeteria.slack.run_publish()` is provided for running in non-async environments.

`kafeteria.slack.publish()` and `kafeteria.slack.run_publish()` takes an optional keyword-only parameter, `skip_holiday`, which, if set to `True`, skips publishing the menu when the current day is a holiday in Korea.

### Automation

Slack integration can be automated to publish the menu at a specific time every weekday using a scheduler. An example using [apscheduler](https://apscheduler.readthedocs.io/) is provided in the `kafeteria.scheduler` module, which can be started by running the following command:

```bash
python -m kafeteria.scheduler
```

If you want to handle the automation in CI/CD, here is an example GitHub Actions workflow. Note that scheduled workflows may be delayed depending on the GitHub Actions server load.

```yaml
name: Publish Menu

on:
  schedule:
    # Every weekday at 11:30 AM GMT+9 (2:30 AM UTC)
    - cron: "30 2 * * 1-5"

env:
  KAFETERIA_SLACK_BOT_TOKEN: ${{ secrets.KAFETERIA_SLACK_BOT_TOKEN }} # Set in repository secrets
  KAFETERIA_SLACK_CHANNEL: "C0123456789" # Replace with your channel ID
  KAFETERIA_MENU_TIME: "0" # Automatically select the menu based on workflow run time
  KAFETERIA_LIST: "fclt,west,east1,east2"

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: pip install kafeteria[slack]

      - name: Publish menu
        run: python -c 'import kafeteria.slack; kafeteria.slack.run_publish(skip_holiday=True)'
```
