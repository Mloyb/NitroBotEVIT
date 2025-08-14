import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string

# === Configuration ===
delay_after_detect = 4.05
dynamic_check_delay = 1.0
typing_speed_wpm = 0  # Set to 0 for instant typing
accuracy = 1
wrong_char_delay = 0.2

NEW_USERNAME = "Devenstupid"
NEW_PASSWORD = "StrongPassword123"

# === Setup WebDriver ===
service = Service(executable_path="C:\\Users\\MSylv275\\Downloads\\chromedriver.exe")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 120)

# Calculate delay per character
delay_per_char = 0 if typing_speed_wpm == 0 else 60 / (typing_speed_wpm * 5)

def get_current_race_text():
    try:
        element = driver.find_element(By.CLASS_NAME, "dash-copy")
        return " ".join(element.text.strip().split()), element
    except:
        try:
            container = driver.find_element(By.CSS_SELECTOR, "div[class*='paragraph']")
            spans = container.find_elements(By.CSS_SELECTOR, "span")
            text = "".join(span.text for span in spans)
            return " ".join(text.strip().split()), container
        except:
            return "", None

def perform_dynamic_typing():
    print(f"⌨️ Typing speed: {'INSTANT' if delay_per_char == 0 else f'{typing_speed_wpm} WPM (~{delay_per_char:.4f}s per char)'} | Accuracy: {accuracy*100:.1f}%")

    body = driver.find_element(By.TAG_NAME, "body")
    ActionChains(driver).click(body).perform()  # Click to focus typing

    typed = ""
    while True:
        current_text, _ = get_current_race_text()
        if not current_text:
            print("⚠️ No race text available — stopping typing.")
            break

        # Determine untyped section
        if current_text.startswith(typed):
            to_type = current_text[len(typed):]
        else:
            overlap_index = current_text.find(typed[-20:]) if len(typed) >= 20 else -1
            if overlap_index != -1:
                to_type = current_text[overlap_index + len(typed[-20:]):]
            else:
                to_type = current_text

        if not to_type:
            break

        actions = ActionChains(driver)

        if delay_per_char == 0:
            # INSTANT MODE
            for char in to_type:
                if char != " " and random.random() > accuracy:
                    actions.send_keys(random.choice(string.ascii_letters + string.punctuation + " "))
                    actions.pause(wrong_char_delay)
                actions.send_keys(char)
                typed += char
            actions.perform()
        else:
            # TIMED MODE
            for char in to_type:
                if char != " " and random.random() > accuracy:
                    actions.send_keys(random.choice(string.ascii_letters + string.punctuation + " "))
                    actions.pause(wrong_char_delay)
                    actions.send_keys(char)
                else:
                    actions.send_keys(char)

                actions.pause(delay_per_char)
                typed += char

            actions.perform()

        time.sleep(dynamic_check_delay)

    print("✅ Typing complete.")

def wait_for_text_to_appear():
    print("Waiting for race text to appear...")
    try:
        wait.until(lambda d: d.find_elements(By.CLASS_NAME, "dash-copy") or d.find_elements(By.CSS_SELECTOR, "div[class*='paragraph']"))
        print("✅ Race text element detected.")
        time.sleep(delay_after_detect)
        return True
    except:
        print("❌ Timed out waiting for race text.")
        return False

def wait_for_race_end_fallback():
    print("⏳ Waiting for race to end...")
    try:
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "dash-input")))
        print("✅ Typing input disappeared — race likely ended.")
        return
    except:
        pass

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "raceAgain")))
        print("✅ 'Race Again' button found — race ended.")
    except:
        print("⚠️ Could not confirm race end — continuing anyway.")

def create_new_account():
    print("Waiting for sign-up form to appear...")
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = driver.find_element(By.NAME, "password")

    username_field.clear()
    username_field.send_keys(NEW_USERNAME)
    password_field.clear()
    password_field.send_keys(NEW_PASSWORD)

    print("Filled in sign-up info — click 'Sign Up' manually.")
    input("✅ Press Enter AFTER clicking 'Sign Up'...")

def main():
    print("🚀 Opening Nitro Type...")
    driver.get("https://www.nitrotype.com/race")

    if wait_for_text_to_appear():
        perform_dynamic_typing()
        wait_for_race_end_fallback()
    else:
        print("⚠️ Skipping tutorial race — no text found.")

    create_new_account()

    while True:
        input("🔁 Press Enter to start next race...")
        if wait_for_text_to_appear():
            perform_dynamic_typing()
            wait_for_race_end_fallback()
        else:
            print("⚠️ Skipping this race — no text found.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user.")
    finally:
        driver.quit()
