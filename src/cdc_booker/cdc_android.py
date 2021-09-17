import time
import traceback
import re

from appium import webdriver


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
            platformVersion="11",
            automationName="UiAutomator2",
            deviceName="Android Emulator",
            appPackage=CDCAndroid.PACKAGE,
            appActivity=f"{CDCAndroid.PACKAGE}.{CDCAndroid.MAIN_ACTIVITY}",
        )

        # we connect to the android emulator
        self.driver = webdriver.Remote(
            "http://localhost:4723/wd/hub", self.desired_caps
        )

        # we need to close the splash screen
        time.sleep(5)
        self.driver.find_element_by_id(
            "sg.com.comfortdelgro.cdc_prd:id/btnClose"
        ).click()
        time.sleep(5)

    def login(self):
        try:
            self.driver.find_element_by_xpath(
                '//android.widget.FrameLayout[@content-desc="Login"]/android.widget.ImageView'
            ).click()
            time.sleep(5)

            # we enter the learner id
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_email"
            ).send_keys(self.username)

            # we enter the password
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/xet_signin_password"
            ).send_keys(self.password)

            # we click the login button
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/xbtn_login"
            ).click()
            time.sleep(5)
        except Exception:
            traceback.print_exc()

    def open_lesson_booking(self):
        try:
            self.driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.support.v4.view.ViewPager/android.view.ViewGroup/android.widget.ScrollView/android.widget.LinearLayout/android.widget.RelativeLayout[2]/android.support.v7.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.RelativeLayout"
            ).click()
            time.sleep(2)
        except Exception:
            traceback.print_exc()

    def open_available_practical_lessons(self):
        try:
            # we select practical lesson in the drop down
            self.driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.RelativeLayout[2]/android.widget.Spinner/android.widget.RelativeLayout/android.widget.RelativeLayout"
            ).click()
            time.sleep(2)

            self.driver.find_element_by_xpath(
                "//android.widget.TextView[contains(@text, 'Practical Lesson')]"
            ).click()
            time.sleep(2)

            # we then select the course
            self.driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.ScrollView/android.widget.RelativeLayout/android.widget.RelativeLayout[3]/android.widget.Spinner/android.widget.RelativeLayout/android.widget.RelativeLayout"
            ).click()
            time.sleep(2)

            self.driver.find_element_by_xpath(
                "//android.widget.TextView[contains(@text, 'Class')]"
            ).click()
            time.sleep(2)

            # and we finally look for the slots
            self.driver.find_element_by_id(
                "sg.com.comfortdelgro.cdc_prd:id/btn_selectdatetime"
            ).click()
            time.sleep(5)

        except Exception:
            traceback.print_exc()

    def get_session_available_count(self):
        session_count = 0
        try:
            # select the text view
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
        self.driver.find_element_by_id(
            "sg.com.comfortdelgro.cdc_prd:id/xtbimg_header_back1"
        ).click()
