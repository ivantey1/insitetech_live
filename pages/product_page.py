from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ProductPage:
    URL = "https://opm-website.iot-asm-test1.insitech.live/constructor?type=2&manufacturer=28&serial=1066&model=7190"
    CLOSE_COOKIE_BTN = (By.ID, "close_modal_btn")
    ADD_TO_CART_NOTIFICATION = (By.XPATH, "//*[contains(text(), 'Добавлено в корзину')]")  # @TODO  переписать
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "#add_to_cart_btn")
    CART_BUTTON = (By.ID, "go_to_cart_page_btn")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 20)

    def open(self):
        self.driver.get(self.URL)
        self.wait_for_page_load()

    def close_cookie_btn(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.CLOSE_COOKIE_BTN)).click()
        except TimeoutException:
            print("Предупреждение: Не удалось закрыть окно с cookie")

    def add_to_cart(self):
        initial_count = self.get_cart_counter()
        self.wait.until(EC.element_to_be_clickable(self.ADD_TO_CART_BUTTON)).click()
        self.wait_for_cart_update(initial_count)

    def wait_for_cart_update(self, initial_count):
        def cart_count_changed(driver):
            return self.get_cart_counter() != initial_count
        self.wait.until(cart_count_changed)

    def wait_for_add_to_cart_notification(self):
        return self.wait.until(EC.visibility_of_element_located(self.ADD_TO_CART_NOTIFICATION))

    def get_cart_counter(self):
        try:
            cart_button = self.wait.until(EC.visibility_of_element_located(self.CART_BUTTON))
            counter_element = cart_button.find_element(By.CSS_SELECTOR, "p.MuiTypography-root")
            return int(counter_element.text.strip() or "0")
        except (NoSuchElementException, ValueError):
            return 0

    def wait_for_page_load(self):
        self.wait.until(EC.presence_of_element_located(self.ADD_TO_CART_BUTTON))

    def get_current_url(self):
        return self.driver.current_url