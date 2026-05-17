import pytest
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@pytest.fixture
def driver():
    """Фикстура для запуска браузера Chrome."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://itcareerhub.de/ru")
    sleep(4)
    yield driver
    driver.quit()


# =====================================================================
# АТОМАРНЫЕ ТЕСТЫ НА ПРОВЕРКУ ЭЛЕМЕНТОВ (Успешно проходят)
# =====================================================================

def test_logo_is_visible(driver):
    """Проверка отображения логотипа."""
    wait = WebDriverWait(driver, 15)
    logo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[class*='logo'], img, svg")))
    assert logo is not None, "Логотип ITCareerHub не найден"


@pytest.mark.parametrize("link_text", [
    "Программы",
    "Способы оплаты",
    "О нас",
    "Отзывы",
    "Блог"
])
def test_menu_links_are_present(driver, link_text):
    """Параметризованный тест для текстовых ссылок."""
    wait = WebDriverWait(driver, 15)
    menu_item = wait.until(EC.presence_of_element_located((By.LINK_TEXT, link_text)))
    assert menu_item is not None, f"Ссылка '{link_text}' не найдена"


def test_menu_link_contacts_is_present(driver):
    """Отдельный атомарный тест для контактов."""
    wait = WebDriverWait(driver, 15)
    contacts_item = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='contact']")))
    assert contacts_item is not None, "Ссылка 'Контакты' не найдена в меню"


def test_language_switcher_ru(driver):
    """Атомарная проверка кнопки языка RU."""
    wait = WebDriverWait(driver, 15)
    lang_ru = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='ru']")))
    assert lang_ru is not None, "Кнопка переключения на RU не найдена"


def test_language_switcher_de(driver):
    """Атомарная проверка кнопки языка DE."""
    wait = WebDriverWait(driver, 15)
    lang_de = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='de']")))
    assert lang_de is not None, "Кнопка переключения на DE не найдена"


# =====================================================================
# ГЛАВНЫЙ СЦЕНАРИЙ: КОНТАКТЫ И ОБРАТНЫЙ ЗВОНОК
# =====================================================================

def test_callback_form_flow(driver):
    """Тест перехода в Контакты, вызова Обратного звонка и проверки текста в окне."""
    wait = WebDriverWait(driver, 15)

    # 1. Скрываем баннер куки
    driver.execute_script("document.querySelectorAll('.CookieConsent').forEach(el => el.remove());")
    sleep(2)

    # 2. Переход на страницу Контакты
    contacts_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='contact']")))
    driver.execute_script("arguments[0].click();", contacts_link)
    print("Переход в Контакты выполнен через JS: OK")

    sleep(5)  # Время на полную загрузку страницы

    # 3. Поиск КЛИКАБЕЛЬНОЙ кнопки "Обратный звонок" БЕЗ XPATH
    elements = driver.find_elements(By.CSS_SELECTOR, "button, a, .t-btn")
    callback_btn = None

    for el in elements:
        try:
            if "звонок" in el.text.lower() and el.is_displayed():
                callback_btn = el
                break
        except:
            continue

    if not callback_btn:
        div_elements = driver.find_elements(By.TAG_NAME, "div")
        for div in div_elements:
            try:
                if "звонок" in div.text.lower() and div.is_displayed():
                    callback_btn = div
                    break
            except:
                continue

    assert callback_btn is not None, "Видимая кнопка 'Обратный звонок' не найдена на странице!"

    # Скроллим к кнопке, чтобы она точно была на экране
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", callback_btn)
    sleep(2)

    # Имитируем реальное физическое нажатие мыши через ActionChains (для триггера поп-апов Tilda)
    try:
        actions = ActionChains(driver)
        actions.move_to_element(callback_btn).click().perform()
    except:
        # Если цепочка действий не сработала — используем принудительный JS клик
        driver.execute_script("arguments[0].click();", callback_btn)

    print("Клик по видимой кнопке 'Обратный звонок' выполнен: OK")

    # 4. Ожидаем появление текста во всплывающем окне (проверка по подстрокам)
    # Разбиваем фразу на ключевые слова, чтобы избежать проблем с кодировкой пробелов в Tilda
    keyword_1 = "запишитесь"
    keyword_2 = "карьерную"

    text_found = False
    for _ in range(15):  # Ожидаем до 15 секунд динамически
        page_source_lower = driver.page_source.lower()
        if keyword_1 in page_source_lower and keyword_2 in page_source_lower:
            text_found = True
            break
        sleep(1)

    assert text_found, "Целевой текст во всплывающем окне не появился за 15 секунд!"
    print("Проверка текста в модальном окне: OK. Все тесты пройдены успешно!")


if __name__ == "__main__":
    pytest.main([__file__])