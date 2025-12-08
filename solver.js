/**
 * WordleSolver.js
 * 輕量化版本：移除 Entropy，僅使用頻率法 (Frequency Score)
 * 策略：Hybrid, Pure Wordle, Standard
 */

export class WordleSolver {
    constructor() {
        this.allWords = [];      // 完整詞庫
        this.words = [];         // 候選字
        this.pastAnswers = new Set();
        
        this.hybridMode = false;
        this.historyExcluded = false; // 是否已執行過排除
        this.attempts = 0;
        
        this.charCount = {};
        this.wordScores = [];
    }

    /**
     * 初始化：載入 CSV 資料
     */
    async init(vocabUrl = 'data/vocabularies.csv', answersUrl = 'data/answers.csv', config = {}) {
        this.hybridMode = config.hybridMode || false;
        const excludeHistory = config.excludeHistory || false;

        // 1. 並行載入資料
        const [vocabText, answersText] = await Promise.all([
            this._fetchText(vocabUrl),
            this._fetchText(answersUrl)
        ]);

        this.allWords = this._parseCSV(vocabText);
        this.pastAnswers = this._parseAnswers(answersText);
        
        // 初始候選池 = 所有單字
        this.words = [...this.allWords];

        // 2. 策略處理
        // 如果是 Pure Wordle 模式，一開始就排除
        if (excludeHistory && !this.hybridMode) {
            this.excludePastAnswers();
            console.log("[Mode] Pure Wordle: History excluded from start.");
        } else if (this.hybridMode) {
            console.log("[Mode] Hybrid: Will exclude history after guess #1.");
        } else {
            console.log("[Mode] Standard: History included.");
        }

        // 3. 計算初始分數
        this._updateScores();
        return this;
    }

    /**
     * 排除過往答案 (用於 Hybrid 模式或手動觸發)
     */
    excludePastAnswers() {
        if (this.historyExcluded) return;
        if (this.pastAnswers.size === 0) return;

        const originalCount = this.words.length;
        this.words = this.words.filter(w => !this.pastAnswers.has(w));
        this.historyExcluded = true;

        this._updateScores();
        console.log(`[Strategy] Excluded history. Reduced from ${originalCount} to ${this.words.length}.`);
    }

    /**
     * 根據回饋過濾單字
     */
    filterWords(guess, feedback) {
        guess = guess.toUpperCase();
        feedback = feedback.toUpperCase();
        
        const filtered = [];
        for (const word of this.words) {
            if (this._isValid(word, guess, feedback)) {
                filtered.push(word);
            }
        }

        this.words = filtered;
        this.attempts++;
        
        this._updateScores();
    }

    getTopGuesses(n = 10) {
        return this.wordScores.slice(0, n);
    }

    // ================= 私有方法 =================

    _updateScores() {
        // 1. 統計目前候選字的字元頻率
        this.charCount = this._analyzeUniqueCharFreq(this.words);
        // 2. 計算每個字的分數
        this.wordScores = this._score(this.words);
    }

    async _fetchText(url) {
        try {
            const resp = await fetch(url);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            return await resp.text();
        } catch (e) {
            console.warn(`Failed to load ${url}:`, e);
            return "";
        }
    }

    _parseCSV(text) {
        return text.split(/[\r\n,]+/)
            .map(w => w.trim().toUpperCase())
            .filter(w => w.length === 5 && /^[A-Z]{5}$/.test(w));
    }

    _parseAnswers(text) {
        const words = this._parseCSV(text);
        return new Set(words);
    }

    _analyzeUniqueCharFreq(words) {
        const counts = {};
        for (const word of words) {
            // 使用 Set 只計算單字中出現過的字母 (不重複計分)
            const uniqueChars = new Set(word);
            for (const char of uniqueChars) {
                counts[char] = (counts[char] || 0) + 1;
            }
        }
        return counts;
    }

    _score(words) {
        // 簡單高效的頻率評分法
        const scores = words.map(word => {
            let score = 0;
            const uniqueChars = new Set(word);
            for (const char of uniqueChars) {
                score += (this.charCount[char] || 0);
            }
            return { word: word, score: score };
        });

        // 分數高到低排序
        return scores.sort((a, b) => b.score - a.score);
    }

    _isValid(word, guess, feedback) {
        // 1. Check Greens
        for (let i = 0; i < 5; i++) {
            if (feedback[i] === 'G') {
                if (word[i] !== guess[i]) return false;
            }
        }

        // 2. Check Yellows/Grays (需計數處理)
        const wordCounts = {};
        for (let i = 0; i < 5; i++) {
            if (feedback[i] !== 'G') {
                const char = word[i];
                wordCounts[char] = (wordCounts[char] || 0) + 1;
            }
        }

        for (let i = 0; i < 5; i++) {
            const char = guess[i];
            const state = feedback[i];

            if (state === 'G') continue;

            if (state === 'Y') {
                if (word[i] === char) return false; // 黃色位置不能相同
                if (!wordCounts[char] || wordCounts[char] <= 0) return false;
                wordCounts[char]--;
            } else if (state === 'X') {
                if (wordCounts[char] > 0) return false;
            }
        }
        return true;
    }
}
