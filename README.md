# Kafeteria

[![CI](https://github.com/kmnhan/kafeteria/actions/workflows/ci.yml/badge.svg)](https://github.com/kmnhan/kafeteria/actions/workflows/ci.yml)

Kafeteria is a Python package to asynchronously access the menu of the cafeterias at KAIST.

## Installation

Clone the repository and install from source:

```bash
git clone https://github.com/kmnhan/kafeteria.git
cd kafeteria
pip install .
```

## Usage

Use the `get_menu` function to get the menu for a specific cafeteria, or the `get_menus` function to get the menus for multiple cafeterias at once.

Valid cafeteria codes are:

- `fclt` : 카이마루
- `west` : 서측식당
- `east1` : 동측식당
- `east2` : 동측교직원식당
- `emp` : 교수회관
- `icc` : ICC

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
