"""
Lab 10: Statistical Language Models (Bigram uLM & Trigram SLM) for Dispatch Alerts
Simplicity: Pure re + Counter n-gram Markov estimators for autocomplete and generation.
"""
import os, re
from collections import Counter, defaultdict

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "corpus.txt")

def load_and_tokenize():
    # Step 1: Read corpus and extract lowercase alphanumeric word tokens
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        text = f.read().lower()
    return re.findall(r"\b[a-z0-9]+\b", text)

TOKENS = load_and_tokenize()

def build_models(tokens):
    # Step 2: Build Unigram, Bigram, and Trigram frequency counters
    unigrams = Counter(tokens)
    bigrams = defaultdict(Counter)
    trigrams = defaultdict(Counter)
    
    for i in range(len(tokens) - 1):
        w1, w2 = tokens[i], tokens[i+1]
        bigrams[w1][w2] += 1
        
    for i in range(len(tokens) - 2):
        w1, w2, w3 = tokens[i], tokens[i+1], tokens[i+2]
        trigrams[(w1, w2)][w3] += 1
        
    return unigrams, bigrams, trigrams

UNIGRAMS, BIGRAMS, TRIGRAMS = build_models(TOKENS)

def predict_next(words, n=3):
    # Step 3: Predict top-n next words with Markov conditional probabilities
    if isinstance(words, str):
        tokens = re.findall(r"\b[a-z0-9]+\b", words.lower())
    else:
        tokens = [w.lower() for w in words]
        
    # Attempt Trigram prediction if 2+ context words exist
    if len(tokens) >= 2:
        context = (tokens[-2], tokens[-1])
        if context in TRIGRAMS and TRIGRAMS[context]:
            total = sum(TRIGRAMS[context].values())
            return [{"word": w, "prob": round(c / total, 3), "model": "trigram"}
                    for w, c in TRIGRAMS[context].most_common(n)]
                    
    # Backoff to Bigram prediction if 1 context word exists
    if len(tokens) >= 1:
        last = tokens[-1]
        if last in BIGRAMS and BIGRAMS[last]:
            total = sum(BIGRAMS[last].values())
            return [{"word": w, "prob": round(c / total, 3), "model": "bigram"}
                    for w, c in BIGRAMS[last].most_common(n)]
                    
    # Backoff to Unigram prior frequency
    total = sum(UNIGRAMS.values())
    return [{"word": w, "prob": round(c / total, 3), "model": "unigram"}
            for w, c in UNIGRAMS.most_common(n)]

def generate(seed="fire reported", length=8):
    # Step 4: Autonomously generate dispatch message following highest transition prob
    current = re.findall(r"\b[a-z0-9]+\b", seed.lower())
    for _ in range(length):
        preds = predict_next(current, n=1)
        if not preds:
            break
        next_word = preds[0]["word"]
        current.append(next_word)
        if next_word in ("now", "immediately", "scene", "urgently"):
            break
    return " ".join(current)

def run_demo(seed="send fire"):
    # Step 5: Demo packaging demonstrating autocomplete suggestions and text generation
    suggestions = predict_next(seed, n=3)
    generated_msg = generate(seed=seed, length=8)
    return {
        "lab": "Lab 10: Statistical Language Models (Bigram & Trigram)",
        "status": "success",
        "seed_phrase": seed,
        "autocomplete_suggestions": suggestions,
        "generated_dispatch_message": generated_msg,
        "corpus_tokens_count": len(TOKENS),
        "unique_vocab_size": len(UNIGRAMS),
        "viva_insight": "Trigrams condition on 2-word history (Markov order 2), providing situational emergency context over simple unigram word frequency."
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run_demo(), indent=2))
