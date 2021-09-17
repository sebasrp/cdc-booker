import traceback
import time
import json
import random
import datetime

import click
import yaml

from cdc_website import CDCWebsite, Types
from cdc_android import CDCAndroid
from cdc_notifier import CDCNotifier


@click.command()
@click.option(
    "--telegram",
    is_flag=True,
    help="Enable telegram notifications when slots are available",
)
@click.option("--scrapper", type=click.Choice(["web", "android"], case_sensitive=False))
@click.option("-c", "--configuration", help="Your configuration file")
@click.option("-u", "--username", help="Your CDC learner ID")
@click.option("-p", "--password", "password_", help="Your CDC password")
def main(username, password_, configuration, scrapper, telegram):
    config = {}
    if configuration is not None:
        with open(configuration, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

    if scrapper is None:
        scrapper = "android"

    username = config.get("username", username)
    password = config.get("password", password_)
    telegram = config.get("telegram", telegram)
    refresh_rate = config.get("refresh_rate", 90)
    if telegram:
        notifier = CDCNotifier(
            token=str(config.get("telegram_token", "")),
            chat_id=str(config.get("telegram_chat_id", "")),
        )
        notifier.send_message(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Vrooom vroom, starting CDC bot"
        )

    if scrapper == "web":
        get_website_slots(
            username=username,
            password=password,
            refresh_rate=refresh_rate,
            notifier=notifier,
        )
    if scrapper == "android":
        get_android_slots(
            username=username,
            password=password,
            refresh_rate=refresh_rate,
            notifier=notifier,
        )


def get_android_slots(username, password, refresh_rate, notifier):
    cdc_android = CDCAndroid(username=username, password=password)
    cdc_android.login()
    cdc_android.open_lesson_booking()

    while True:
        try:
            cdc_android.open_available_practical_lessons()
            session_count = cdc_android.get_session_available_count()
            now = datetime.datetime.now()
            print(
                f"{now.strftime('%Y-%m-%d %H:%M:%S')}: Available slots: {session_count}"
            )
            if (notifier is not None) and session_count > 0:
                notifier.send_message(f"Available slots: {session_count}")

            # we go back to the class selection
            cdc_android.go_back()

        except Exception:
            traceback.print_exc()

        sleep_randomish(refresh_rate)


def get_website_slots(username, password, refresh_rate, notifier):
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
                print(
                    f"available sessions: {json.dumps(available_sessions, indent = 4)}"
                )

                if (notifier is not None) and session_count > 0:
                    notifier.send_message(f"Available slots: {session_count}")
                    notifier.send_message(
                        f"Available sessions: {json.dumps(available_sessions, indent = 4)}"
                    )

            except Exception:
                traceback.print_exc()
            sleep_randomish(refresh_rate)


def sleep_randomish(refresh_rate, variance=0.2):
    # We add/substract randomly 20% (default) from target refresh rate
    # in order to try to prevent patttern recognition
    varianace_seconds = int(refresh_rate * 0.2)
    random_variance = random.randint(-varianace_seconds, varianace_seconds)
    next_refresh = refresh_rate + random_variance
    print(f"Sleeping for {next_refresh}s...")
    time.sleep(next_refresh)


if __name__ == "__main__":
    main()
