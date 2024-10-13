import time

import pytest
from pages.product_page import ProductPage


@pytest.fixture
def product_setup(driver):
    page = ProductPage(driver)
    page.open()
    page.close_cookie_btn()
    yield page
    # @TODO page.clear_cart()   Очистка корзины после каждого теста

def test_cart_counter(product_page):
    page = product_page
    time.sleep(5) # @TODO переписать на норм ожидание
    page.add_to_cart()
    assert page.get_cart_counter() == 1, "Неверное значение коунтера у корзины"

def test_add_cart_pop_up(product_page):
    page = product_page
    time.sleep(5) # @TODO переписать на норм ожидание
    page.add_to_cart()
    assert page.wait_for_add_to_cart_notification(), "Уведомление 'Добавлено в корзину' не появилось"





