let allWords = [];
let filteredWords = [];

async function loadWords() {
    try {
        const response = await fetch('bookworm_dict.txt');
        const text = await response.text();
        allWords = text.trim().split('\n').filter(word => word.length > 0);
        filteredWords = [...allWords];
        displayWords();
        updateWordCount();
    } catch (error) {
        console.error('Error loading words:', error);
        document.getElementById('wordList').innerHTML = '<div class="word-item">Error loading dictionary file</div>';
        document.getElementById('wordCount').textContent = 'Error loading words';
    }
}

function displayWords() {
    const wordList = document.getElementById('wordList');
    const fragment = document.createDocumentFragment();
    
    filteredWords.forEach(word => {
        const wordDiv = document.createElement('div');
        wordDiv.className = 'word-item';
        wordDiv.textContent = word;
        fragment.appendChild(wordDiv);
    });
    
    wordList.innerHTML = '';
    wordList.appendChild(fragment);
}

function filterWords(filterText) {
    if (filterText === '') {
        filteredWords = [...allWords];
    } else {
        filteredWords = allWords.filter(word => 
            word.toUpperCase().startsWith(filterText.toUpperCase())
        );
    }
    displayWords();
    updateWordCount();
}

function updateWordCount() {
    const count = filteredWords.length;
    const total = allWords.length;
    const wordCountElement = document.getElementById('wordCount');
    
    if (count === total) {
        wordCountElement.textContent = `Showing all ${total} words`;
    } else {
        wordCountElement.textContent = `Showing ${count} of ${total} words`;
    }
}

function setupEventListeners() {
    const filterInput = document.getElementById('filterInput');
    
    filterInput.addEventListener('input', function(e) {
        let value = e.target.value;
        value = value.toUpperCase();
        e.target.value = value;
        filterWords(value);
    });
    
    filterInput.addEventListener('keydown', function(e) {
        if (e.key.match(/[a-z]/i) && e.key.length === 1) {
            return true;
        }
        if (['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'Tab'].includes(e.key)) {
            return true;
        }
        if (e.ctrlKey || e.metaKey) {
            return true;
        }
        e.preventDefault();
    });
    
    filterInput.addEventListener('paste', function(e) {
        e.preventDefault();
        const paste = (e.clipboardData || window.clipboardData).getData('text');
        const cleanPaste = paste.replace(/[^A-Za-z]/g, '').toUpperCase();
        const currentValue = e.target.value;
        const start = e.target.selectionStart;
        const end = e.target.selectionEnd;
        const newValue = currentValue.substring(0, start) + cleanPaste + currentValue.substring(end);
        e.target.value = newValue;
        filterWords(newValue);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    loadWords();
});