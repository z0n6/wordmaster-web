# WordMaster - AI Wordle Solver

A web-based AI-powered Wordle solver that helps you solve Wordle puzzles efficiently using frequency-based scoring algorithms.

## Features

- **AI-Powered Suggestions**: Uses frequency analysis to suggest optimal next guesses
- **Multiple Strategies**:
  - Standard: Includes all possible words
  - Hybrid: Excludes past Wordle answers (like real Wordle gameplay)
- **Interactive UI**: Click tiles to provide feedback (Gray → Yellow → Green)
- **Dark/Light Theme**: Automatic theme detection with manual toggle
- **Real-time Updates**: Suggestions update after each guess
- **Responsive Design**: Works on desktop and mobile devices

## How to Use

1. **Open the App**: Open `index.html` in your web browser
2. **Choose Strategy**: Select Standard or Hybrid mode from the dropdown
3. **Enter Guess**: Type a 5-letter word in the input field
4. **Provide Feedback**:
   - Click the tiles below the input to cycle through states:
     - Gray (X): Letter not in word
     - Yellow (Y): Letter in word, wrong position
     - Green (G): Letter in word, correct position
5. **Analyze**: Click "Analyze Feedback" to get new suggestions
6. **Repeat**: Use the top suggestions for your next guess

## Installation

No installation required! Simply open `index.html` in any modern web browser.

## Project Structure

```
WordMaster-web/
├── index.html          # Main application UI
├── solver.js           # WordleSolver class with AI logic
├── data/
│   ├── vocabularies.csv # Complete word list (guesses)
│   └── answers.csv      # Possible answer words
└── README.md           # This file
```

## Technologies

- **Frontend**: HTML5, CSS3, JavaScript (ES6 Modules)
- **Algorithm**: Frequency-based word scoring
- **Data**: CSV word lists

## Algorithm

The solver uses a frequency-based approach to score words:
- Analyzes character frequency in remaining possible words
- Prioritizes words with unique, common letters
- Updates scores dynamically after each guess

## Data Sources

- `vocabularies.csv`: Comprehensive 5-letter word list for guesses
- `answers.csv`: Official Wordle answer words

## Browser Support

Works in all modern browsers that support:
- ES6 Modules
- Fetch API
- CSS Custom Properties

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License