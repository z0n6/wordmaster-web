import os
import requests
import datetime
import time
import argparse
import sys

# 設定檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/answers.csv')

def get_word_by_date(date_obj):
    """取得指定日期的 Wordle 答案"""
    date_str = date_obj.strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WordMasterBot/1.0)"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        return data.get("solution", "").upper()
    except Exception as e:
        print(f"[{date_str}] Error: {e}")
        return None

def load_existing_words():
    """讀取現有的 CSV 資料到 Set 中"""
    existing_words = set()
    if os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            raw_words = content.replace(',', '\n').splitlines()
            for w in raw_words:
                clean_w = w.strip().upper()
                if len(clean_w) == 5:
                    existing_words.add(clean_w)
    return existing_words

def run_update(days_to_check):
    existing_words = load_existing_words()
    print(f"目前資料庫有 {len(existing_words)} 個單字")
    print(f"準備檢查過去 {days_to_check} 天的資料...\n")

    new_words_count = 0
    today = datetime.date.today()
    
    # 暫存新發現的單字，避免頻繁開關檔案，最後一次寫入或逐筆寫入皆可
    # 這裡採用逐筆寫入模式，確保中斷時也有存檔
    with open(CSV_FILE_PATH, 'a', encoding='utf-8') as f:
        if os.path.getsize(CSV_FILE_PATH) > 0:
            # 確保不會黏在最後一行，先補換行符號（如果檔案結尾沒有的話）
            # 這裡簡單處理：每次腳本啟動寫入第一筆前，多檢查一次比較保險
            # 但為了邏輯單，我們依靠寫入時的前綴處理
            pass

        for i in range(days_to_check, -1, -1):
            target_date = today - datetime.timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            word = get_word_by_date(target_date)
            
            if word:
                if word in existing_words:
                    print(f"[{date_str}] {word} - 已存在 (跳過)")
                else:
                    print(f"[{date_str}] {word} - >>> 新增 <<<")
                    f.write(f"\n{word}") # 寫入時前方加換行，確保格式
                    existing_words.add(word)
                    new_words_count += 1
            else:
                print(f"[{date_str}] 無資料 (可能尚未發布)")
            
            # 避免對 API 請求過快
            time.sleep(0.3)

    print(f"\n更新完成！共新增了 {new_words_count} 個單字。")

if __name__ == "__main__":
    # 設定參數解析器
    parser = argparse.ArgumentParser(description="手動更新 Wordle 答案庫，可指定回溯天數。")
    
    # 添加 'days' 參數
    # type=int: 確保輸入是數字
    # nargs='?': 參數是選填的
    # default=30: 如果沒填，預設回溯 30 天
    parser.add_argument('days', type=int, nargs='?', default=30, 
                        help='要往回檢查的天數 (預設: 30天)')

    args = parser.parse_args()

    # 執行主程式
    if args.days < 0:
        print("天數必須是正整數")
        sys.exit(1)

    run_update(args.days)
