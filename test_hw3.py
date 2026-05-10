from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pytest


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://itcareerhub.de/ru")
    yield driver
    driver.quit()


def test_full_homepage_flow(driver):
    # Явное ожидание до 10 секунд
    wait = WebDriverWait(driver, 10)

    # 0. Убираем баннер куки
    sleep(2)
    driver.execute_script("document.querySelectorAll('.CookieConsent').forEach(el => el.remove());")

    # 1. Переход в Контакты 
    contacts_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'contact')]")))
    driver.execute_script("arguments[0].click();", contacts_link)
    print("Переход в Контакты: OK")

    # 2. Ждем загрузки страницы Контактов и ищем кнопку
    # Ищем ЛЮБОЙ элемент, содержащий текст "звонок" (без учета регистра для надежности)
    sleep(3)  # Даем скриптам на странице прогрузиться

    try:
        # Ищем через XPATH, который не боится лишних пробелов
        callback_xpath = "//*[contains(translate(text(), 'ЗВОНОК', 'звонок'), 'звонок')]"
        callback_btn = wait.until(EC.element_to_be_clickable((By.XPATH, callback_xpath)))

        # Скроллим к ней и кликаем через JS
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", callback_btn)
        sleep(1)
        driver.execute_script("arguments[0].click();", callback_btn)
        print("Клик по кнопке звонка: OK")
    except:
        # Если не нашли, выведем все тексты кнопок для отладки
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Найдено кнопок: {len(buttons)}. Тексты: {[b.text for b in buttons if b.text]}")
        pytest.fail("Кнопка с текстом 'звонок' не найдена")

    # 3. Проверка появления текста консультации
    sleep(3)
    expected_text = "консультац"  # Ищем часть слова, чтобы не споткнуться об окончания

    # Ждем появления текста на странице
    wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{expected_text}')]")))

    assert "консультац" in driver.page_source.lower()
    print("Тест полностью пройден! Поздравляю!")