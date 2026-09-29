#!/usr/bin/env bash
# Runs every question in QUESTIONS through retrieval only (no model call),
# printing the question, its expected answer, and the full text of each
# retrieved chunk.
set -euo pipefail
cd "$(dirname "$0")"

python3 -c "
import config
import questions
from store import search

for q in questions.QUESTIONS:
    print('=' * 100)
    print(f\"Question: {q['question']}\")
    print(f\"Expected: {q.get('expects', '')}\")
    print()
    results = search(q['question'], top_k=config.TOP_K, corpus=config.CORPUS)
    for i, r in enumerate(results, 1):
        print(f'--- chunk {i} (distance={r.distance:.4f}, source={r.source}) ---')
        print(r.text)
        print()
"
