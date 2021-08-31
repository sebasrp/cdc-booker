import traceback
import time

import click

from cdc_website import CDCWebsite, Types


@click.command()
@click.option("-u", "--username", help="Your CDC learner ID")
@click.option("-p", "--password", "password_", help="Your CDC password")
def main(username, password_):
    with CDCWebsite(
        username=username, password=password_, headless=False
    ) as cdc_website:
        cdc_website.open_home_website()
        cdc_website.login()
        while True:
            cdc_website.open_booking_overview()
            cdc_website.open_practical_lessons_booking(type=Types.PRACTICAL)

            try:
                print(cdc_website.get_session_available_count())
            except Exception:
                traceback.print_exc()

            # keep in the page
            print("Sleeping for 60s...")
            time.sleep(60)


if __name__ == "__main__":
    main()
