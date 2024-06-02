import os
import time
import requests
from zipfile import ZipFile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
import json

def download_browsermob_proxy():
    url = 'https://github.com/lightbody/browsermob-proxy/releases/download/browsermob-proxy-2.1.4/browsermob-proxy-2.1.4-bin.zip'
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def extract_zip(file_path, extract_to='.'):
    with ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def main():
    zip_path = download_browsermob_proxy()
    extract_zip(zip_path, './browsermob-proxy')
    bmp_path = os.path.join(os.getcwd(), 'browsermob-proxy', 'browsermob-proxy-2.1.4', 'bin', 'browsermob-proxy')
    os.chmod(bmp_path, 0o755)
    server = Server(bmp_path)
    try:
        server.start()
    except Exception as e:
        print(f"Error starting Proxy server: {e}")
        return
    
    proxy = server.create_proxy()
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        proxy.new_har("webpage", options={'captureHeaders': True, 'captureContent': True})

        driver.get("https://github.com")

        time.sleep(100)

        with open("code_log.txt", "w") as file:
            cookies = driver.get_cookies()
            file.write("All Cookies:\n")
            for cookie in cookies:
                file.write(json.dumps(cookie) + "\n")
            file.write("\n")

            har_data = proxy.har
            file.write("Network Requests:\n")
            for entry in har_data['log']['entries']:
                request = entry['request']
                response = entry['response']
                file.write(f"Request URL: {request['url']}\n")
                file.write(f"Response Status: {response['status']}\n")
                file.write(f"Response Content: {json.dumps(response['content'], indent=2)}\n")
                file.write("\n")

    finally:
        driver.quit()
        proxy.close()
        server.stop()

if __name__ == "__main__":
    main()
