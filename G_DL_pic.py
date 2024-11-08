import os
import time
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from requests.exceptions import Timeout

def download_image(url, folder_path, count):
    try:
        response = requests.get(url, timeout=10)  # タイムアウトを10秒に設定
        if response.status_code == 200:
            with open(os.path.join(folder_path, f'image_{count}.jpg'), 'wb') as file:
                file.write(response.content)
            print(f"画像 {count} をダウンロードしました: {url}")
        else:
            print(f"画像のダウンロードに失敗しました: {url} ステータスコード: {response.status_code}")
    except Timeout:
        print(f"画像のダウンロードがタイムアウトしました: {url}")
    except Exception as e:
        print(f"画像のダウンロードに失敗しました: {str(e)}")

def search_and_download(query, num_images, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print(f"フォルダを作成しました: {download_folder}")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # ヘッドレスモードで実行
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)  # ページロードのタイムアウトを30秒に設定

    try:
        driver.get('https://www.google.com/imghp?hl=ja')
        print("Google画像検索ページを開きました")
    except Exception as e:
        print(f"Google画像検索ページの読み込みに失敗しました: {str(e)}")
        driver.quit()
        return

    try:
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        print(f"検索クエリ '{query}' を送信しました")
    except Exception as e:
        print(f"検索クエリの送信に失敗しました: {str(e)}")
        driver.quit()
        return

    time.sleep(2)  # ページが読み込まれるのを待つ

    image_urls = set()
    count = 0
    while len(image_urls) < num_images:
        try:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')
            for thumbnail in thumbnails[len(image_urls):num_images]:
                try:
                    thumbnail.click()
                    time.sleep(1)
                    images = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
                    for image in images:
                        src = image.get_attribute('src')
                        if src and 'http' in src:
                            image_urls.add(src)
                            print(f"画像URLを追加しました: {src}")
                            if len(image_urls) >= num_images:
                                break
                except Exception as e:
                    print(f"サムネイルのクリックに失敗しました: {str(e)}")
                if len(image_urls) >= num_images:
                    break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        except Exception as e:
            print(f"画像の取得に失敗しました: {str(e)}")
            break

    driver.quit()

    for i, url in enumerate(image_urls):
        download_image(url, download_folder, i)

def main():
    query = "生ラム肉 画像 写真"
    num_images = 10
    download_folder = r"C:\G_meat"

    try:
        search_and_download(query, num_images, download_folder)
        logging.info(f"{num_images}枚の画像が{download_folder}にダウンロードされました。")
    except Exception as e:
        logging.error(f"エラーが発生しました: {str(e)}")

    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO)
        main()
        
        
