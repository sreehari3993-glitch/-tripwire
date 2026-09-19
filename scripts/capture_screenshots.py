import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUT_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1440,900")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    print("1. Capturing Login Page...")
    driver.get("http://localhost:5173/login")
    time.sleep(1.5)
    driver.save_screenshot(os.path.join(OUT_DIR, "01_login.png"))

    print("2. Logging in as FAC001...")
    user_input = wait.until(EC.presence_of_element_located((By.ID, "faculty-id")))
    pass_input = driver.find_element(By.ID, "password")
    user_input.send_keys("FAC001")
    pass_input.send_keys("tripwire123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    print("3. Capturing Dashboard...")
    time.sleep(3)
    driver.save_screenshot(os.path.join(OUT_DIR, "02_dashboard.png"))

    print("4. Capturing Student Roster...")
    driver.get("http://localhost:5173/students")
    time.sleep(2)
    driver.save_screenshot(os.path.join(OUT_DIR, "03_students_roster.png"))

    print("5. Capturing Batch Attendance Register Modal...")
    batch_btn = wait.until(EC.element_to_be_clickable((By.ID, "batch-attendance-btn")))
    batch_btn.click()
    time.sleep(2)
    driver.save_screenshot(os.path.join(OUT_DIR, "04_batch_attendance.png"))

    # Close modal
    driver.get("http://localhost:5173/students")
    time.sleep(1)

    print("6. Capturing Student Profile (Rahul - CSE24001)...")
    driver.get("http://localhost:5173/students/CSE24001")
    time.sleep(2.5)
    driver.save_screenshot(os.path.join(OUT_DIR, "05_student_profile_rahul.png"))

    print("7. Capturing Interventions...")
    driver.get("http://localhost:5173/interventions")
    time.sleep(2)
    driver.save_screenshot(os.path.join(OUT_DIR, "06_interventions.png"))

    print("All screenshots successfully captured!")

except Exception as e:
    print("Error during screenshot capture:", e)
finally:
    driver.quit()
