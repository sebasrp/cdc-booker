# cdc-booker

Having troubles booking your lessons at the CDC center? This tool let's you know when a slot is available!

## Dependencies

* Tesseract: see [installation page](https://tesseract-ocr.github.io/tessdoc/Home.html#binaries)
* ChromeDriver: see [installation page](https://chromedriver.chromium.org/downloads)
* Appium
  * archlinux: sudo pacman -S nodejs
  * macos: brew install node
  * sudo npm install -g appium
  * sudo npm install wd
  * sudo npm install -g appium-doctor
* Android Studio (for an android emulator)
  * archlinux: yay -S android-studio-beta

## Create config.yml

If using the cli arguments is not something you fancy, you can define the configuration on its own file.
A file `config.yml` needs to be created, with the following attributes

    # your cdc username
    username: '00123456'

    # your cdc password
    password: '123456'

    # how long to wait between refreshes. We will add/remove up to 10% of the time
    # in order to randomnize the refresh rate
    refresh_rate: 60

    # Set to true if you want to check circuit revision instead of class
    circuit_revision: true

    # Set to true if you want to check road revision instead of practical class
    road_revision: true

    # telegram bot token (required for telegram notifications)
    # see https://core.telegram.org/bots#creating-a-new-bot for instructionscr
    telegram_token:'your_own_bot_token'

    # telegram chat id to send updates to
    # see https://stackoverflow.com/a/50736131/91468
    telegram_chat_id: '1234567890'