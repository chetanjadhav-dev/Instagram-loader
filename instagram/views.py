import os
import time
import requests
from django.http import JsonResponse
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# Django Views
# =========================

def home(request):
    return JsonResponse({"message": "Instagram Scraper API Running"})

def save_instagram_posts(request, username):
    """
    Logs into Instagram via Selenium, downloads posts for given username,
    and saves them locally.
    """
    insta_user = "your_instagram_username"
    insta_pass = "your_instagram_password"
    download_folder = os.path.join(settings.MEDIA_ROOT, username)
    os.makedirs(download_folder, exist_ok=True)

    # Setup Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Login
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        driver.find_element(By.NAME, "username").send_keys(insta_user)
        driver.find_element(By.NAME, "password").send_keys(insta_pass)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(7)

        # Open target profile
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)

        # Scroll to load posts
        scroll_count = 3  # Adjust how many scrolls you want
        for _ in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Collect image URLs
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        img_urls = [img.get_attribute("src") for img in img_elements if img.get_attribute("src")]

        saved_files = []
        for idx, img_url in enumerate(img_urls):
            try:
                img_data = requests.get(img_url).content
                file_path = os.path.join(download_folder, f"{username}_{idx}.jpg")
                with open(file_path, "wb") as f:
                    f.write(img_data)
                saved_files.append(file_path)
            except Exception as e:
                print(f"Error saving image {idx}: {e}")

        driver.quit()
        return JsonResponse({"status": "success", "saved_files": saved_files})

    except Exception as e:
        driver.quit()
        return JsonResponse({"status": "error", "message": str(e)})

def fetch_instagram_posts(request, username, post_count):
    """
    Fetch saved posts for a username from local storage.
    """
    download_folder = os.path.join(settings.MEDIA_ROOT, username)
    if not os.path.exists(download_folder):
        return JsonResponse({"status": "error", "message": "No saved posts for this user"})

    files = sorted(os.listdir(download_folder))[:post_count]
    file_urls = [request.build_absolute_uri(settings.MEDIA_URL + f"{username}/{file}") for file in files]

    return JsonResponse({"status": "success", "posts": file_urls})
