import traceback
import time
import pprint

import click
import yaml

from cdc_website import CDCWebsite, Types


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
    with CDCWebsite(
        username=username,
        password=password_,
        headless=False,
        telegram=telegram,
        configuration=config,
    ) as cdc_website:
        cdc_website.open_home_website()
        cdc_website.login()
        while True:
            cdc_website.open_booking_overview()
            cdc_website.open_practical_lessons_booking(type=Types.PRACTICAL)

            try:
                print(cdc_website.get_session_available_count())
                available_sessions = cdc_website.get_available_sessions()
                print(f"available sessions: {pprint.pprint(available_sessions)}")
            except Exception:
                traceback.print_exc()

            # keep in the page
            print("Sleeping for 60s...")
            time.sleep(60)


if __name__ == "__main__":
    main()
