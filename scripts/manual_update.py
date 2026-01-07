import os
import requests
import datetime
import time
import argparse
import sys

# 設定檔案路徑
BASE_DIR = os.path.dirname(__file__)
ANSWERS_PATH = os.path.join(BASE_DIR, '../data/answers.csv')
VOCAB_PATH = os.path.join(BASE_DIR, '../data/vocabularies.csv')

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

def load_word_set(filepath):
    """通用讀取函式：讀取 CSV 資料到 Set 中"""
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
    """通用寫入函式：將單字附加到檔案末尾"""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            # 檢查檔案是否為空，若不為空確保有換行
            if os.path.getsize(filepath) > 0:
                f.write(f"\n{word}")
            else:
                f.write(word)
        return True
    except Exception as e:
        print(f"寫入錯誤 {filepath}: {e}")
        return False

def run_update(days_to_check):
    existing_answers = load_word_set(ANSWERS_PATH)
    existing_vocab = load_word_set(VOCAB_PATH)
    
    today = datetime.date.today()
    
    # 這裡範圍改回從 days_to_check 到 0 (包含今天)
    for i in range(days_to_check, -1, -1):
        target_date = today - datetime.timedelta(days=i)
        word = get_word_by_date(target_date)
        
        is_today = (i == 0) # 標記是否為今天
        
        if word:
            log_msg = []
            
            # 1. 檢查 Answers (如果是今天，強制跳過；如果不是今天，且不在庫中，則新增)
            if not is_today and word not in existing_answers:
                append_word_to_file(ANSWERS_PATH, word)
                existing_answers.add(word)
                log_msg.append("加入 Answer")
            
            # 2. 檢查 Vocab (無論哪一天，只要不在庫中就新增)
            if word not in existing_vocab:
                append_word_to_file(VOCAB_PATH, word)
                existing_vocab.add(word)
                log_msg.append("加入 Vocab")
                
            if log_msg:
                prefix = "[今日]" if is_today else f"[{target_date}]"
                print(f"{prefix} {word} - >>> {' & '.join(log_msg)} <<<")
            # 僅顯示有變動的，或是你可以選擇全部顯示
            
        time.sleep(0.3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="手動更新 Wordle 答案庫與字庫。")
    parser.add_argument('days', type=int, nargs='?', default=30, 
                        help='要往回檢查的天數 (預設: 30天)')
    args = parser.parse_args()

    if args.days < 0:
        print("天數必須是正整數")
        sys.exit(1)

    run_update(args.days)
