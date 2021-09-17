import time
import base64
import traceback

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import captcha


class Types:
    PRACTICAL = "practical"
    ROAD_REVISION = "rr"
    BTT = "btt"
    RTT = "rtt"
    PT = "pt"


class CDCWebsite:
    def __init__(
        self,
        username=None,
        password=None,
        headless=False,
        home_url="https://www.cdc.com.sg",
        booking_url="https://www.cdc.com.sg:8080",
        is_test=False,
    ):
        self.username = username
        self.password = password

        self.home_url = home_url
        self.booking_url = booking_url
        self.is_test = is_test

        browser_options = Options()
        if headless:
            browser_options.add_argument("--headless")
        browser_options.add_argument("--no-sandbox")
        browser_options.add_argument("--no-proxy-server")

        self.driver = webdriver.Chrome(options=browser_options)
        self.driver.set_window_size(1600, 768)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()

    def _open_website(self, path: str):
        self.driver.get(f"{self.booking_url}/{path}{'.html' if self.is_test else ''}")

    def open_home_website(self):
        self.driver.get(self.home_url)
        assert "ComfortDelGro" in self.driver.title

    def login(self):
        time.sleep(5)
        login_btn = self.driver.find_element_by_xpath('//*[@id="top-menu"]/ul/li[10]/a')
        login_btn.click()

        if self.username not in [None, ""]:
            learner_id_input: WebElement = self.driver.find_element_by_name("userId")
            learner_id_input.send_keys(self.username)

        if self.password not in [None, ""]:
            password_input = self.driver.find_element_by_name("password")
            password_input.send_keys(self.password)

        # wait for user to solve recaptcha
        try:
            while self.driver.find_element_by_name("userId"):
                time.sleep(5)
                print("Waiting for recaptcha")
        except NoSuchElementException:
            print("Recaptcha solved! Continuing")
            time.sleep(5)

    def logout(self):
        self._open_website("NewPortal/logOut.aspx?PageName=Logout")

    def open_booking_overview(self):
        self._open_website("NewPortal/Booking/StatementBooking.aspx")

    def open_practical_lessons_booking(self, type=Types.PRACTICAL):
        self._open_website("NewPortal/Booking/BookingPL.aspx")

        while (
            self.driver.find_element_by_id(
                "ctl00_ContentPlaceHolder1_lblSessionNo"
            ).text
            == ""
        ):
            select = Select(
                self.driver.find_element_by_id("ctl00_ContentPlaceHolder1_ddlCourse")
            )

            # sometimes there are multiple options (like "CLASS 2B CIRCUIT REVISION" and "Class 2B Lesson 5")
            # in that case, choose the "Class 2B Lesson *" as this is much more relevant to be notified for
            select_indx = 1
            avail_options = []
            if len(select.options) > 1:
                for i, option in enumerate(select.options):
                    # skip first option ("Select")
                    if i == 0:
                        continue
                    avail_options.append(option.text.strip())
                    if "Class 2B Lesson" in option.text:
                        select_indx = i
            if len(select.options) > 2:
                print(
                    f"There are two options ({avail_options}) available. Choosing the practical lesson ({select.options[select_indx].text.strip()})."
                )
            self.lesson_name_practical = avail_options[select_indx - 1]
            select.select_by_index(select_indx)

            # we try to solve captcha till we succeed:
            # print(
            #    f"text of ctl00_ContentPlaceHolder1_lblSessionNo: {self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_lblSessionNo').text}"
            # )

            print("entering while loop for captch handler")
            # we need to handle the captcha
            try:
                captcha_img = self.driver.find_element_by_id(
                    "ctl00_ContentPlaceHolder1_CaptchaImg"
                )

                captcha_base64_string = captcha_img.get_attribute("src")
                with open("captcha_tmp.png", "wb") as fh:
                    fh.write(base64.b64decode(captcha_base64_string.split(",")[1]))

                captcha_text = captcha.resolve_3("captcha_tmp.png")
                print(f"captcha text: {captcha_text}")
                captcha_input: WebElement = self.driver.find_element_by_name(
                    "ctl00$ContentPlaceHolder1$txtVerificationCode"
                )

                # wait for the popup to appear
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.ID, "ctl00_ContentPlaceHolder1_txtVerificationCode")
                    )
                )
                captcha_input.send_keys(captcha_text)

                # click in submit
                self.driver.find_element_by_name(
                    "ctl00$ContentPlaceHolder1$Button1"
                ).click()

                # wait for the popup to appear
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.ID, "ctl00_ContentPlaceHolder1_txtVerificationCode")
                    )
                )
            except Exception:
                traceback.print_exc()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.ID, "ctl00_ContentPlaceHolder1_lblSessionNo")
            )
        )
        return True

    def get_session_available_count(self):
        session_available_span = self.driver.find_element_by_id(
            "ctl00_ContentPlaceHolder1_lblSessionNo"
        )
        return int(session_available_span.text)

    def _get_all_session_dates(self):
        available_times = []
        available_days = []
        for row in self.driver.find_elements_by_css_selector(
            "table#ctl00_ContentPlaceHolder1_gvLatestav tr"
        ):
            th_cells = row.find_elements_by_tag_name("th")
            for i, th_cell in enumerate(th_cells):
                if i < 2:
                    continue

                available_times.append(str(th_cell.text).split("\n")[1])

            td_cells = row.find_elements_by_tag_name("td")
            if len(td_cells) > 0:
                available_days.append(td_cells[0].text)
        return available_days, available_times

    def get_available_sessions(self):
        available_sessions = {}
        available_days, available_times = self._get_all_session_dates()

        # iterate over all "available motorcycle" images to get column and row
        # to later on get the date & time of that session
        input_elements = self.driver.find_elements_by_tag_name("input")
        for input_element in input_elements:
            # Images1.gif -> available slot
            input_element_src = input_element.get_attribute("src")
            if "Images1.gif" in input_element_src or "Images3.gif" in input_element_src:
                # e.g. ctl00_ContentPlaceHolder1_gvLatestav_ctl02_btnSession4 (02 is row, 4 is column)
                element_id = str(input_element.get_attribute("id"))
                # remove 2 to remove th row (for mapping to available_days)
                row = int(element_id.split("_")[3][-1:]) - 2
                # remove 1 to remove first column (for mapping to available_times)
                column = int(element_id[-1]) - 1
                if "Images1.gif" in input_element_src:
                    # create or append to list of times (in case there are multiple sessions per day)
                    # row is date, column is time
                    if row not in available_sessions.keys():
                        available_sessions.update(
                            {available_days[row]: [available_times[column]]}
                        )
                    else:
                        available_sessions.update(
                            {
                                available_days[row]: available_sessions[row].append(
                                    available_times[column]
                                )
                            }
                        )
        return available_sessions
