import traceback
import time
import json
import random
import datetime

import click
import yaml

from cdc_website import CDCWebsite, Types
from cdc_notifier import CDCNotifier


@click.command()
@click.option(
    "--telegram",
    is_flag=True,
    help="Enable telegram notifications when slots are available",
)
@click.option("-c", "--configuration", help="Your configuration file")
@click.option("-u", "--username", help="Your CDC learner ID")
@click.option("-p", "--password", "password_", help="Your CDC password")
def main(username, password_, configuration, telegram):
    config = {}
    if configuration is not None:
        with open(configuration, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

    username = config.get("username", username)
    password = config.get("password", password_)
    telegram = config.get("telegram", telegram)
    refresh_rate = config.get("refresh_rate", 60)
    notifier = CDCNotifier(
        token=str(config.get("telegram_token", "")),
        chat_id=str(config.get("telegram_chat_id", "")),
    )

    with CDCWebsite(
        username=username,
        password=password,
        headless=False,
    ) as cdc_website:
        cdc_website.open_home_website()
        cdc_website.login()
        while True:
            cdc_website.open_booking_overview()
            cdc_website.open_practical_lessons_booking(type=Types.PRACTICAL)

            try:
                session_count = cdc_website.get_session_available_count()
                available_sessions = cdc_website.get_available_sessions()
                now = datetime.datetime.now()
                print(
                    f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Available slots: {session_count}"
                )
                print(f"available sessions: {json.dumps(available_sessions, indent = 4)}")

                if telegram and session_count > 0:
                    notifier.send_message(f"Available slots: {session_count}")
                    notifier.send_message(
                        f"Available sessions: {json.dumps(available_sessions, indent = 4)}"
                    )

            except Exception:
                traceback.print_exc()

            # keep in the page. We add/substract randomly 20% from target refresh rate
            # in order to try to prevent patttern recognition
            varianace_seconds = int(refresh_rate * 0.2)
            random_variance = random.randint(-varianace_seconds, varianace_seconds)
            next_refresh = refresh_rate + random_variance
            print(f"Sleeping for {next_refresh}s...")
            time.sleep(next_refresh)


if __name__ == "__main__":
    main()
