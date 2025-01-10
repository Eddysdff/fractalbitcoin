import cloudscraper
import time
from datetime import datetime
import pandas as pd
import chardet
from apscheduler.schedulers.background import BackgroundScheduler

# 移除不再使用的detect_encoding函数
# def detect_encoding(file_path):
#     with open(file_path, 'rb') as file:
#         raw_data = file.read()
#     return chardet.detect(raw_data)['encoding']

def load_addresses_and_proxies(excel_file):
    addresses_proxies = []
    try:
        # 移除encoding参数
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            addresses_proxies.append((row['address'], row['proxy'], row['username'], row['password']))
    except Exception as e:
        print(f"读取Excel文件时发生错误: {str(e)}")
        raise
    return addresses_proxies

def format_proxy(proxy, username, password):
    if username and password:
        proxy_parts = proxy.split('://')
        return f"{proxy_parts[0]}://{username}:{password}@{proxy_parts[1]}"
    return proxy

def claim_faucet(address, proxy, username, password):
    url = "https://explorer.unisat.io/fractal-testnet/faucet"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    data = {
        "address": address
    }
    formatted_proxy = format_proxy(proxy, username, password)
    proxies = {"http": formatted_proxy, "https": formatted_proxy}

    scraper = cloudscraper.create_scraper()

    try:
        response = scraper.get(url, headers=headers, data=data, proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"{datetime.now()} - 成功为地址 {address} 领水")
        else:
            print(f"{datetime.now()} - 为地址 {address} 领水失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"{datetime.now()} - 为地址 {address} 领水时发生错误: {str(e)}")

def main_claim_process():
    print(f"{datetime.now()} - 开始执行领水过程...")
    try:
        addresses_proxies = load_addresses_and_proxies("address.xlsx")
        for address, proxy, username, password in addresses_proxies:
            claim_faucet(address, proxy, username, password)
            time.sleep(2)  # 在每次请求之间添加短暂延迟
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")
    print(f"{datetime.now()} - 领水过程执行完毕")

if __name__ == "__main__":
    print("自动领水脚本已启动...")
    scheduler = BackgroundScheduler()
    
    # 立即执行一次
    main_claim_process()
    
    # 然后每6小时执行一次
    scheduler.add_job(main_claim_process, 'interval', hours=6)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()