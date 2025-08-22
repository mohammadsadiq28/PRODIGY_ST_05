import random, string, time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

BASE_URL = "http://www.automationpractice.pl/index.php"

def random_email() -> str:
    user = "test_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{user}@example.com"

def make_driver(browser: str = "chrome"):
    browser = browser.lower()
    if browser == "chrome":
        opts = webdriver.ChromeOptions()
        opts.add_argument("--start-maximized")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    if browser == "firefox":
        opts = webdriver.FirefoxOptions()
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=opts)
    if browser == "edge":
        opts = webdriver.EdgeOptions()
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=opts)
    raise ValueError("browser must be chrome|firefox|edge")

def page_h1(driver):
    try:
        return driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except Exception:
        return ""

@pytest.fixture(params=["chrome"])  # add "firefox", "edge" if you have them installed
def driver(request):
    drv = make_driver(request.param)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()

def test_checkout_e2e_success(driver, tmp_path):
    wait = WebDriverWait(driver, 25)

    # 1) Home → search and open a product
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located((By.ID, "search_query_top"))).send_keys("Faded Short Sleeve T-shirts")
    driver.find_element(By.NAME, "submit_search").click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.product-name[title='Faded Short Sleeve T-shirts']"))).click()

    # 2) Product page → add to cart
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#add_to_cart button"))).click()

    # 3) Layer cart modal → Proceed to checkout
    wait.until(EC.visibility_of_element_located((By.ID, "layer_cart")))
    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Proceed to checkout']"))).click()

    # 4) Summary → Proceed
    assert "SHOPPING-CART SUMMARY" in page_h1(driver).upper()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//p[@class='cart_navigation clearfix']//a[@title='Proceed to checkout']"))).click()

    # 5) Authentication → Create account
    assert "AUTHENTICATION" in page_h1(driver).upper()
    email = random_email()
    wait.until(EC.visibility_of_element_located((By.ID, "email_create"))).send_keys(email)
    driver.find_element(By.ID, "SubmitCreate").click()

    # 6) Registration form
    wait.until(EC.visibility_of_element_located((By.ID, "account-creation_form")))
    driver.find_element(By.ID, "customer_firstname").send_keys("Test")
    driver.find_element(By.ID, "customer_lastname").send_keys("User")
    driver.find_element(By.ID, "passwd").send_keys("Password123")

    driver.find_element(By.ID, "address1").send_keys("123 Main St")
    driver.find_element(By.ID, "city").send_keys("New York")
    Select(driver.find_element(By.ID, "id_state")).select_by_visible_text("Alabama")
    driver.find_element(By.ID, "postcode").send_keys("12345")
    driver.find_element(By.ID, "phone_mobile").send_keys("1234567890")
    alias = driver.find_element(By.ID, "alias")
    alias.clear()
    alias.send_keys("My Address")
    driver.find_element(By.ID, "submitAccount").click()

    # 7) Addresses → proceed
    assert "ADDRESSES" in page_h1(driver).upper()
    wait.until(EC.element_to_be_clickable((By.NAME, "processAddress"))).click()

    # 8) Shipping → accept TOS → proceed
    assert "SHIPPING" in page_h1(driver).upper()
    wait.until(EC.element_to_be_clickable((By.ID, "cgv"))).click()
    driver.find_element(By.NAME, "processCarrier").click()

    # 9) Payment → choose bank wire
    assert "PLEASE CHOOSE YOUR PAYMENT METHOD" in page_h1(driver).upper()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.bankwire"))).click()

    # 10) Confirm order
    assert "ORDER SUMMARY" in page_h1(driver).upper()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#cart_navigation button[type='submit']"))).click()

    # 11) Order confirmation
    assert "ORDER CONFIRMATION" in page_h1(driver).upper()
    msg = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p.cheque-indent strong"))).text.strip().lower()
    assert "complete" in msg  # "Your order on My Store is complete."
    # optional proof: save screenshot
    driver.save_screenshot(str(tmp_path / "order_confirm.png"))

def test_registration_validation_message(driver):
    """Negative check: trigger a form error (invalid zip) and assert alert text."""
    wait = WebDriverWait(driver, 20)
    driver.get(BASE_URL)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.login"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "email_create"))).send_keys(random_email())
    driver.find_element(By.ID, "SubmitCreate").click()
    wait.until(EC.visibility_of_element_located((By.ID, "account-creation_form")))

    driver.find_element(By.ID, "customer_firstname").send_keys("Bad")
    driver.find_element(By.ID, "customer_lastname").send_keys("Data")
    driver.find_element(By.ID, "passwd").send_keys("Password123")
    driver.find_element(By.ID, "address1").send_keys("123 Main St")
    driver.find_element(By.ID, "city").send_keys("New York")
    Select(driver.find_element(By.ID, "id_state")).select_by_visible_text("Alabama")
    driver.find_element(By.ID, "postcode").send_keys("12")  # invalid zip
    driver.find_element(By.ID, "phone_mobile").send_keys("1234567890")
    driver.find_element(By.ID, "submitAccount").click()

    alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-danger")))
    assert "invalid" in alert.text.lower() or "required" in alert.text.lower()
