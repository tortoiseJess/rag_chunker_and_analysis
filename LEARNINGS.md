## milestone 1
1. learnt that before starting to "fix" or optimize, I should start by experiementing what outputs given an input.
So I can have a better idea what to fix or optimize. 

2. Are they short reviews or long guides? Is the useful information packed into one sentence or spread across a paragraph? The campus life -- few sentences in a lot of documents, threads --need to clean irrelevant "reply" texts and city_guides -- have headings --same for places and the whole document expands on the place.

3. python app.py --corpus advice_threads chunks -n 1 --26 chunks total

## milestone 2 acceptance criteria for retrieval
1. eg. For at least 4 of my 5 test questions, the top results include a chunk containing the answer" — that's a criterion.

2. questions + correct answers ground truth file --questions.py
3. criteria.md gets to evaluate my choice of retrieval --chunking + answer + relevant 
- it should not give out of context sources or wrong grounds 
- experiement with the right chunking criteria:
A useful starting experiment for your RAG QA project would be: to try 100, 300, ..2000 chunks
Research question: How does chunk size affect retrieval quality and final QA accuracy in a RAG system?

Measure separately:
Retrieval Recall@K — did we retrieve the chunk containing the answer?
Answer accuracy — did the LLM answer correctly?
Faithfulness — is the answer supported by the retrieved text?
Token usage / latency — how much context did we have to process?


## Scorer
1. llm as judge 
2. vinilla string match
3. rapidFuzz?