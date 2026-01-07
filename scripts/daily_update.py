import os
import requests
import datetime
from datetime import timedelta

# 設定檔案路徑
BASE_DIR = os.path.dirname(__file__)
ANSWERS_PATH = os.path.join(BASE_DIR, '../data/answers.csv')
VOCAB_PATH = os.path.join(BASE_DIR, '../data/vocabularies.csv')

def get_wordle_answer(target_date):
    """取得指定日期的 Wordle 答案"""
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://www.nytimes.com/svc/wordle/v2/{date_str}.json"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WordMasterBot/1.0)"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print(f"[{date_str}] Data not available yet.")
            return None
        response.raise_for_status()
        data = response.json()
        return data.get("solution", "").upper()
    except Exception as e:
        print(f"[{date_str}] Error fetching data: {e}")
        return None

def load_word_set(filepath):
    """讀取 CSV 料到 Set 中"""
    word_set = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            raw_words = content.replace(',', '\n').splitlines()
            for w in raw_words:
                clean_w = w.strip().upper()
                if len(clean_w) == 5:
                    word_set.add(clean_w)
    return word_set

def append_word_to_file(filepath, word):
    """將新單字附加到檔案末尾"""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            if os.path.getsize(filepath) > 0:
                f.write(f"\n{word}")
            else:
                f.write(word)
        return True
    except Exception as e:
        print(f"Error writing to {filepath}: {e}")
        return False

def process_sync():
    print("--- Daily Sync Start ---")
    today = datetime.date.today()
    yesterday = today - timedelta(days=1)
    
    # 載入現有資料庫
    existing_answers = load_word_set(ANSWERS_PATH)
    existing_vocab = load_word_set(VOCAB_PATH)

    # ==============================
    # 任務 1: 處理「今日」單字 (Today)
    # 目標: 只更新 Vocab，不更新 Answers
    # ==============================
    print(f"Check Today ({today}):")
    word_today = get_wordle_answer(today)
    
    if word_today:
        if word_today not in existing_vocab:
            if append_word_to_file(VOCAB_PATH, word_today):
                print(f"  -> '{word_today}' added to Vocabularies.")
        else:
            print(f"  -> '{word_today}' already known.")
    else:
        print("  -> No data for today.")

    # ==============================
    # 任務 2: 處理「昨日」單字 (Yesterday)
    # 目標: 更新 Answers (歸檔)，並雙重檢查 Vocab
    # ==============================
    print(f"Check Yesterday ({yesterday}):")
    word_yesterday = get_wordle_answer(yesterday)
    
    if word_yesterday:
        # 歸檔到歷史答案
        if word_yesterday not in existing_answers:
            if append_word_to_file(ANSWERS_PATH, word_yesterday):
                print(f"  -> '{word_yesterday}' archived to Answers.")
        else:
            print(f"  -> '{word_yesterday}' already archived.")

        # 再次檢查 Vocab (以防昨天腳本沒跑或失敗)
        if word_yesterday not in existing_vocab: # 注意這裡檢查的是現有庫，雖然上面可能剛加了今天的
             # 重新讀取太耗資源，這裡只要邏輯對即可：
             # 如果昨天的字不在記憶體中的 vocab set，補進檔案
            if append_word_to_file(VOCAB_PATH, word_yesterday):
                print(f"  -> '{word_yesterday}' added to Vocabularies (Late fix).")
    else:
        print("  -> No data for yesterday.")

    print("--- Daily Sync End ---")

if __name__ == "__main__":
    process_sync()
