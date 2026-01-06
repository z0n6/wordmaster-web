import os
import requests
import datetime
import csv

# 設定檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/answers.csv')

def get_todays_wordle():
    """從 NYT API 取得今天的 Wordle 答案"""
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WordMasterBot/1.0)"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("solution", "").upper()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def update_csv(new_word):
    """將新單字寫入 CSV"""
    if not new_word or len(new_word) != 5:
        print("Invalid word received.")
        return False

    # 讀取現有內容以避免重複
    existing_words = set()
    if os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            # 根據你的 solver.js 邏輯，它是用 \r, \n 或 , 分隔
            # 這裡我們簡單處理，把所有非字母濾掉後存入 set
            raw_words = content.replace(',', '\n').splitlines()
            for w in raw_words:
                clean_w = w.strip().upper()
                if len(clean_w) == 5:
                    existing_words.add(clean_w)

    if new_word in existing_words:
        print(f"Word '{new_word}' already exists in DB. Skipping.")
        return False
    
    # 寫入新單字 (附加模式)
    # 為了保持格式整潔，我們確保新單字換行寫入
    with open(CSV_FILE_PATH, 'a', encoding='utf-8') as f:
        # 如果檔案不是空的且最後沒有換行，先補一個換行
        if os.path.getsize(CSV_FILE_PATH) > 0:
             # 這裡簡單直接寫入新行，solver.js 的 regex 能夠處理多餘的空白
            f.write(f"\n{new_word}")
        else:
            f.write(new_word)
            
    print(f"Added '{new_word}' to answers.csv")
    return True

if __name__ == "__main__":
    word = get_todays_wordle()
    if word:
        update_csv(word)
