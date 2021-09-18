import time
import traceback
import re

from appium import webdriver
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
            platformVersion="12",
            automationName="UiAutomator2",
            deviceName="Android Emulator",
            appPackage=CDCAndroid.PACKAGE,
            appActivity=f"{CDCAndroid.PACKAGE}.{CDCAndroid.MAIN_ACTIVITY}",
            newCommandTimeout=300,
        )

        # we connect to the android emulator
        self.driver = webdriver.Remote(
            "http://localhost:4723/wd/hub", self.desired_caps
        )

        # Waiting until the close button shows
        self.wait_by_id_and_click("sg.com.comfortdelgro.cdc_prd:id/btnClose")

    def login(self):
        try:
            # we wait till the login button is available on homescreen
            self.wait_by_xpath_and_click(
                '//android.widget.FrameLayout[@content-desc="Login"]/android.widget.ImageView'
            )

            # Waiting until the login fields appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "sg.com.comfortdelgro.cdc_prd:id/xet_signin_email")
                )
            )

            # we enter the learner id
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_email"
            ).send_keys(self.username)

            # we enter the password
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_password"
            ).send_keys(self.password)

            # we click the login button
            self.wait_by_id_and_click("sg.com.comfortdelgro.cdc_prd:id/xbtn_login")
        except Exception:
            traceback.print_exc()

    def open_lesson_booking(self):
        try:
            self.wait_by_xpath_and_click(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.support.v4.view.ViewPager/android.view.ViewGroup/android.widget.ScrollView/android.widget.LinearLayout/android.widget.RelativeLayout[2]/android.support.v7.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.RelativeLayout",
            )
        except Exception:
            traceback.print_exc()

    def open_available_practical_lessons(self):
        try:
            # we wait till the lesson practical lesson dropdown is there
            self.wait_by_xpath_and_click(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.Spinner/android.widget.RelativeLayout/android.widget.RelativeLayout",
            )

            # we then select the practical lesson
            self.wait_by_xpath_and_click(
                "//android.widget.TextView[contains(@text, 'Practical Lesson')]"
            )

            # we open the course dropdown
            self.wait_by_xpath_and_click(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.RelativeLayout[3]/android.widget.Spinner/android.widget.RelativeLayout/android.widget.RelativeLayout"
            )

            # we select the first class
            self.wait_by_xpath_and_click(
                "//android.widget.TextView[contains(@text, 'Class')]"
            )

            # and we finally look for the slots
            self.wait_by_id_and_click(
                "sg.com.comfortdelgro.cdc_prd:id/btn_selectdatetime"
            )
        except Exception:
            traceback.print_exc()

    def get_session_available_count(self):
        session_count = -1
        try:
            # select the text view
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.TextView",
                    )
                )
            )
            sessions_available = self.driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.view.ViewGroup/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.TextView"
            )
            match = re.search(r"([0-9]*) sesssion", sessions_available.text)
            session_count = int(match.group(1))
            print(f"sessions: {session_count}")
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
            self.driver.find_element_by_xpath(xpath).click()
        except Exception:
            traceback.print_exc()

    def wait_by_id_and_click(self, id, timeout=20):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, id))
            )
            self.driver.find_element_by_id(id).click()
        except Exception:
            traceback.print_exc()
