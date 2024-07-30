import time
import traceback
import re

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CDCAndroid:
    PACKAGE = "sg.com.comfortdelgro.cdc_prd"
    MAIN_ACTIVITY = "Activities.SplashActivity"

    def __init__(
        self,
        username=None,
        password=None,
    ):
        self.username = username
        self.password = password
        self.desired_caps = dict(
            platformName="Android",
            automationName="UiAutomator2",
            deviceName="Android Emulator",
            appPackage=CDCAndroid.PACKAGE,
            appActivity=f"{CDCAndroid.PACKAGE}.{CDCAndroid.MAIN_ACTIVITY}",
            newCommandTimeout=300,
        )
        self.exception_count = 0

        # we connect to the android emulator
        self.driver = webdriver.Remote(
            "http://localhost:4723", options=UiAutomator2Options().load_capabilities(self.desired_caps)
        )

        # Waiting until the close button shows
        self.wait_by_id_and_click("sg.com.comfortdelgro.cdc_prd:id/btnClose")

    def login(self):
        try:
            # we wait till the login button is available on homescreen
            self.wait_by_xpath_and_click(
                '//android.widget.FrameLayout[@content-desc="Login"]'
            )

            # Waiting until the login fields appear

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "sg.com.comfortdelgro.cdc_prd:id/xet_signin_email")
                )
            )

            # we enter the learner id
            self.driver.find_element(by=AppiumBy.ID, value=
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_email"
            ).send_keys(self.username)

            # we enter the password
            self.driver.find_element(by=AppiumBy.ID, value=
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_password"
            ).send_keys(self.password)

            # we click the login button
            self.wait_by_id_and_click("sg.com.comfortdelgro.cdc_prd:id/xbtn_login")
        except Exception:
            self.exception_count += 1
            traceback.print_exc()

    def open_lesson_booking(self):
        try:
            self.wait_by_xpath_and_click(
                """(//android.widget.ImageView[@resource-id="sg.com.comfortdelgro.cdc_prd:id/cat_img"])[2]""",
            )
        except Exception:
            self.exception_count += 1
            traceback.print_exc()

    def open_available_practical_lessons(self, circuit_revision=False, road_revision=False):
        try:
            # we wait till the lesson practical lesson dropdown is there
            self.wait_by_xpath_and_click(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.Spinner/android.widget.RelativeLayout/android.widget.RelativeLayout",
            )

            # we then select the practical lesson
            self.wait_by_xpath_and_click(
                """//android.widget.TextView[@resource-id="sg.com.comfortdelgro.cdc_prd:id/text" and @text="Practical Lesson"]"""
            )

            # we open the course dropdown
            self.wait_by_xpath_and_click(
                """//android.widget.Spinner[@resource-id="sg.com.comfortdelgro.cdc_prd:id/select_course_spinner"]""")

            # if override for circuit revision, do that. otherwise, we select the first class
            if circuit_revision:
                self.wait_by_xpath_and_click(
                    "//android.widget.TextView[contains(@text, 'CIRCUIT REVISION')]"
                )
            elif road_revision:
                self.wait_by_xpath_and_click(
                    "//android.widget.TextView[contains(@text, 'ROAD REVISION')]"
                )
            else:
                self.wait_by_xpath_and_click(
                    "//android.widget.TextView[contains(@text, 'Class')]"
                )

            # and we finally look for the slots
            self.wait_by_id_and_click(
                "sg.com.comfortdelgro.cdc_prd:id/btn_selectdatetime"
            )
        except Exception:
            self.exception_count += 1
            traceback.print_exc()

    def get_session_available_count(self):
        session_count = -1

        # we wait 2sec before and after taking screenshot
        time.sleep(2)
        # we take a screenshot of the sessions
        self.driver.save_screenshot("cdc_screenshot.png")

        # we wait 2sec before and after taking screenshot
        time.sleep(2)

        # we first try to see whether we have 0 sessions (most cases)
        try:
            no_sessions_xpath = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.TextView"
            # select the text view
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, no_sessions_xpath))
            )
            sessions_available = self.driver.find_element_by_xpath(no_sessions_xpath)
            match = re.search(r"([0-9]*) session", sessions_available.text)
            session_count = int(match.group(1))
        except Exception:
            traceback.print_exc()

        if session_count == 0:
            return session_count

        # then we check whether there are available sessions
        try:
            avail_sessions_id = "sg.com.comfortdelgro.cdc_prd:id/header_name"
            # find if there are sessions
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        avail_sessions_id,
                    )
                )
            )
            sessions_available = self.driver.find_element(by=AppiumBy.ID, value=avail_sessions_id)
            match = re.search(r"([0-9]*) session", sessions_available.text)
            session_count = int(match.group(1))
        except Exception:
            traceback.print_exc()

        return session_count

    def go_back(self):
        self.wait_by_id_and_click("sg.com.comfortdelgro.cdc_prd:id/xtbimg_header_back1")

    def wait_by_xpath_and_click(self, xpath, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self.driver.find_element(by=AppiumBy.XPATH, value=xpath).click()
        except Exception:
            self.exception_count += 1
            traceback.print_exc()

    def wait_by_id_and_click(self, id, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            self.driver.find_element(by=AppiumBy.ID, value=id).click()
        except Exception:
            self.exception_count += 1
            traceback.print_exc()
