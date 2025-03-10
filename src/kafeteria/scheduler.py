"""Start the scheduler to run `publish` at predefined times."""

import asyncio
import contextlib
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kafeteria.slack import publish

STOP = asyncio.Event()


async def main() -> None:
    scheduler = AsyncIOScheduler()

    job_kwargs = {
        "day_of_week": "mon-fri",
        "timezone": "Asia/Seoul",
        "kwargs": {"skip_holiday": True},
        "misfire_grace_time": None,
    }

    # Schedule the function to run at 11:30 and 17:30 every weekday.
    scheduler.add_job(publish, "cron", hour=11, minute=30, **job_kwargs)
    scheduler.add_job(publish, "cron", hour=17, minute=30, **job_kwargs)
    scheduler.start()

    print("Press Ctrl+{} to exit".format("Break" if os.name == "nt" else "C"))  # noqa: T201

    await STOP.wait()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
