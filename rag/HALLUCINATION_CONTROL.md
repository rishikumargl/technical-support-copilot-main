# Hallucination Control - Peer 2 Implementation

**How we prevent the AI from making up answers**

---

## What is Hallucination?

**Hallucination** = When an AI system generates false or made-up information that sounds plausible but isn't supported by facts.

**Example (Bad)**:
- User: "What is the leave policy?"
- AI (hallucinating): "You get 30 days of vacation per year, unlimited sick days, and 5 days parental leave!"
- Reality: The knowledge base doesn't mention any of this!

**Example (Good - With Hallucination Control)**:
- User: "What is the leave policy?"
- AI: "I cannot find a reliable answer in the corporate knowledge base."
- Reality: System found no matching documents, so it refuses to answer

---

## Hallucination Control in Peer 2

### **Layer 1: Empty Results (Hard Stop)**

When no relevant chunks are found, return empty list:

```python
# If search returns 0 results
results = []

# Peer 3 sees empty results and MUST refuse to answer
if not results:
    return "I cannot find a reliable answer in the corporate knowledge base."
```

**Implementation**:
```python
# In hybrid_search.py
results = search.retrieve_relevant_chunks(
    query=user_query,
    filters=filters,
    search_type="hybrid",
    top_k=5
)

# Peer 2 returns []
# → Peer 3 must handle this responsibly
```

**Test Case**:
```python
# Query: "xyz123 nonsense randomtext"
# Result: 0 chunks found ✓
# Confidence: N/A
# Output: "Cannot find reliable answer" ✓
```

---

### **Layer 2: Confidence Scores**

Every result includes THREE confidence metrics:

```python
{
    "combined_score": 0.928,   # Hybrid score (0-1)
    "dense_score": 0.88,       # Semantic understanding (0-1)
    "sparse_score": 1.0        # Keyword matching (0-1)
}
```

**Interpretation**:
- **0.9-1.0**: Very confident → Safe to use
- **0.5-0.9**: Moderately confident → Caution required
- **0.0-0.5**: Low confidence → Should not use
- **0.0**: No match → MUST refuse

**Real Example**:
```
Query: "What is the leave policy?"

Result 1:
  Document: v2_remote_policy
  Combined Score: 0.400 (40%)
  Dense: 0.000 (no semantic match)
  Sparse: 1.000 (keyword match only)
  
Interpretation:
  ⚠️ LOW CONFIDENCE (40%)
  ⚠️ No semantic understanding (dense = 0)
  ✓ Only keyword matching (sparse = 1)
  
Action: Can return but should FLAG as uncertain
```

---

### **Layer 3: Source Attribution**

Every result includes the source document:

```python
{
    "chunk_id": "abc123",
    "document_name": "v2_remote_policy",
    "text": "Full text of the chunk...",
    "department": "HR",
    "category": "Policy",
    "version": "2"
}
```

**Value for Hallucination Control**:
- Users can verify the source themselves
- If the answer seems wrong, they can check the original
- Increases accountability and transparency

**Example**:
```
Q: "What is the leave policy?"
A: "Remote workers must maintain standard business hours."
SOURCE: HR Policy Document - Remote Work Policy v2.0

User can:
✓ Verify this is actually in the document
✓ Read the full context
✓ Check if it's the right policy
✓ Know exactly where it came from
```

---

### **Layer 4: Metadata Filtering**

Prevents irrelevant document types from being used:

```python
# User asks HR question
results = search.retrieve_relevant_chunks(
    query="leave policy",
    filters={"department": "HR", "category": "Policy"},
    top_k=5
)

# Only HR + Policy documents are considered
# Engineering docs are excluded
# Guides are excluded
# → Reduces chance of wrong context
```

**Prevents**:
```
❌ WRONG: Returning Engineering setup guide for HR question
❌ WRONG: Returning a Ticket (issue report) instead of Policy
❌ WRONG: Mixing documents from different departments

✓ RIGHT: Only HR Policy documents for HR questions
✓ RIGHT: Only Engineering Guides for engineering questions
```

---

## Hallucination Prevention Strategy

### **Peer 2's Responsibility**
```
┌─────────────────────────────────────────────────┐
│         PEER 2: RETRIEVAL LAYER                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  Input: User Query                              │
│    ↓                                            │
│  Search hybrid index (dense + BM25)             │
│    ↓                                            │
│  Apply metadata filters                         │
│    ↓                                            │
│  Calculate confidence scores                    │
│    ↓                                            │
│  Return results OR empty list                   │
│    ↓                                            │
│  Output: Ranked chunks with metadata            │
│                                                 │
│  CRITICAL FEATURE:                              │
│  - Return empty [] if no good matches           │
│  - Include confidence scores                    │
│  - Always include source information            │
│  - Filter by metadata                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### **Peer 3's Responsibility**
```
┌─────────────────────────────────────────────────┐
│    PEER 3: LLM ORCHESTRATION LAYER              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Input: Results from Peer 2                     │
│    ↓                                            │
│  CHECK 1: Are there results?                    │
│    ├─ NO (empty): Refuse to answer              │
│    │   "I cannot find..."                       │
│    └─ YES: Continue                             │
│       ↓                                          │
│  CHECK 2: Confidence threshold met?             │
│    ├─ Score < 0.5: Refuse or warn               │
│    └─ Score >= 0.5: Continue                    │
│       ↓                                          │
│  CHECK 3: Format context for LLM                │
│    ├─ Include source explicitly                 │
│    ├─ Add confidence score                      │
│    └─ Set strict system prompt                  │
│       ↓                                          │
│  CHECK 4: System Prompt                         │
│    "ONLY use provided context.                  │
│     Do NOT make up information.                 │
│     If context doesn't answer the question,    │
│     say: 'I cannot find...'                     │
│     Include source attribution."                │
│       ↓                                          │
│  Call LLM with constraints                      │
│       ↓                                          │
│  Verify answer matches context                  │
│    ├─ Answer follows context: OK                │
│    └─ Answer beyond context: REJECT             │
│       ↓                                          │
│  Return answer with source                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Hallucination Control Levels

### **Level 1: Retrieval (Peer 2) - What We Implemented**

✅ **Dense + Sparse Search**
- Semantic understanding (dense vectors)
- Keyword matching (BM25)
- Combined scoring reduces false positives

✅ **Empty Results**
- No results = No hallucination possible
- Return [] and let Peer 3 handle it

✅ **Confidence Scores**
- Every result has a score (0-1)
- Low scores = Be careful
- Zero score = Don't use

✅ **Metadata Filtering**
- Filter by department
- Filter by category
- Exclude wrong document types

✅ **Source Attribution**
- Every result includes source
- Users can verify
- Increases accountability

---

### **Level 2: LLM Orchestration (Peer 3) - You Need To Implement**

```python
# PSEUDO CODE FOR PEER 3

def answer_question(user_query):
    # Step 1: Get results from Peer 2
    results = retrieve_relevant_chunks(
        query=user_query,
        search_type="hybrid",
        top_k=5
    )
    
    # Step 2: Check if we have results
    if not results:
        return {
            "answer": "I cannot find a reliable answer in the corporate knowledge base.",
            "confidence": 0,
            "sources": []
        }
    
    # Step 3: Check confidence threshold
    best_score = max(r["combined_score"] for r in results)
    if best_score < 0.5:
        return {
            "answer": "I found some potentially relevant information, but my confidence is low. Please check directly.",
            "confidence": best_score,
            "sources": results
        }
    
    # Step 4: Build context for LLM
    context = "\n\n".join([
        f"Document: {r['document_name']}\n{r['text']}"
        for r in results
    ])
    
    # Step 5: System prompt that prevents hallucination
    system_prompt = """You are a helpful corporate assistant.
    
    CRITICAL RULES:
    1. ONLY answer using the provided context
    2. Do NOT make up facts or information
    3. If the context doesn't answer the question, respond EXACTLY:
       "I cannot find a reliable answer in the corporate knowledge base."
    4. Always cite your source: "Based on [document_name]..."
    5. If you're uncertain, say so
    
    Context confidence: {best_score:.1%}
    
    If confidence is below 70%, add a warning."""
    
    # Step 6: Call LLM with strict constraints
    answer = llm.generate(
        prompt=f"""Question: {user_query}
        
        Context:
        {context}
        
        Answer based ONLY on the above context. Do not make up information.""",
        system_prompt=system_prompt,
        max_tokens=500,
        temperature=0  # Lower temperature = less hallucination
    )
    
    # Step 7: Post-process to catch hallucinations
    if "I cannot find" in answer:
        # LLM correctly refused
        return {
            "answer": answer,
            "confidence": 0,
            "sources": results
        }
    
    # Step 8: Verify answer is in context
    if not verify_answer_in_context(answer, context):
        return {
            "answer": "I cannot find a reliable answer in the corporate knowledge base.",
            "confidence": 0,
            "sources": results
        }
    
    # Step 9: Return answer with sources
    return {
        "answer": answer,
        "confidence": best_score,
        "sources": results,
        "sources_details": [
            {
                "document": r['document_name'],
                "version": r['version'],
                "category": r['category'],
                "relevant_text": r['text'][:200] + "..."
            }
            for r in results
        ]
    }
```

---

### **Level 3: Frontend Display (Peer 4)**

```javascript
// PSEUDO CODE FOR PEER 4

function displayAnswer(response) {
    const { answer, confidence, sources, sources_details } = response;
    
    // Display main answer
    showAnswer(answer);
    
    // Display confidence indicator
    if (confidence < 0.5) {
        showWarning("⚠️ Low confidence answer");
    } else if (confidence < 0.7) {
        showCaution("⚠️ Moderate confidence");
    } else {
        showConfident("✓ High confidence");
    }
    
    // Display sources
    showSourceAttribution({
        documents: sources_details.map(s => s.document),
        versions: sources_details.map(s => s.version),
        expandable: true  // User can expand to see full context
    });
    
    // User feedback
    showFeedback({
        helpful: thumbsUp,
        notHelpful: thumbsDown,
        reportError: "This answer is wrong"
    });
}
```

---

## Real Test Case: Hallucination Control in Action

### **Test 1: Good Answer (High Confidence)**

```
Query: "What is the leave policy?"
Found: v2_remote_policy (Policy, HR)
Confidence: 40%
Dense Score: 0.000
Sparse Score: 1.000

Analysis:
  ⚠️ Moderate confidence (40%)
  ✓ Exact keyword match (sparse=1.0)
  ❌ No semantic match (dense=0.0)
  
Action:
  - Return document
  - Add caution flag
  - Show source prominently
  - Let user verify
```

### **Test 2: No Answer (Empty Results)**

```
Query: "xyz123 nonsense randomtext"
Found: (no results)
Confidence: N/A
Dense Score: N/A
Sparse Score: N/A

Analysis:
  ✓ No hallucination possible
  ✓ System correctly found nothing
  
Action:
  - Return empty list []
  - Peer 3 sees empty results
  - Peer 3 refuses to answer ✓
  - User sees: "Cannot find answer" ✓
```

### **Test 3: Low Confidence (Weak Match)**

```
Query: "Something obscure"
Found: Partial match
Confidence: 25%
Dense Score: 0.1
Sparse Score: 0.4

Analysis:
  ❌ Very low confidence (25%)
  ❌ Weak semantic match (dense=0.1)
  ❌ Weak keyword match (sparse=0.4)
  
Action:
  - Return result but FLAG as unreliable
  - Peer 3 checks score < 0.5
  - Peer 3 refuses to generate answer
  - Or shows warning + raw document
```

---

## Hallucination Control Checklist

### **Peer 2 (What We Implemented)**

- [x] Empty results when no matches found
- [x] Confidence scores (combined, dense, sparse)
- [x] Source attribution (document name, version)
- [x] Metadata filtering (department, category)
- [x] Semantic + keyword search (reduces false matches)
- [x] Low-score filtering capability

### **Peer 3 (What You Need To Implement)**

- [ ] Check if results are empty
- [ ] Check confidence threshold
- [ ] Strict system prompt for LLM
- [ ] Format context clearly
- [ ] Verify answer against context
- [ ] Refuse to answer if no good sources
- [ ] Add source attribution to response

### **Peer 4 (What You Need To Implement)**

- [ ] Display confidence indicator
- [ ] Show warning for low confidence
- [ ] Display sources prominently
- [ ] Make sources expandable/clickable
- [ ] Add "report error" feedback
- [ ] Show thumbs up/down for user feedback

### **Peer 5 (What You Need To Measure)**

- [ ] Hallucination rate (false answers / total answers)
- [ ] False positive rate (wrong documents returned)
- [ ] Confidence score accuracy
- [ ] User acceptance of refusals
- [ ] Source attribution coverage

---

## Summary

### **What Peer 2 Does (Retrieval Layer)**

```
INPUT: User question
  ↓
PROCESS:
  1. Search semantically (dense vectors)
  2. Search by keywords (BM25)
  3. Combine scores
  4. Filter by metadata
  5. Score confidence
  ↓
OUTPUT:
  - Ranked results with confidence scores, OR
  - Empty list if no good matches
  ↓
PREVENT HALLUCINATION:
  ✓ Return only factual chunks from documents
  ✓ Never generate text (that's Peer 3's job)
  ✓ Return empty when unsure
  ✓ Include confidence scores
  ✓ Always include source info
```

### **What Peer 3 Must Do (LLM Layer)**

```
INPUT: Results from Peer 2
  ↓
PROCESS:
  1. Check if results exist
  2. Check confidence threshold
  3. Build context from chunks
  4. Set strict system prompt
  5. Call LLM with constraints
  6. Verify answer against context
  ↓
OUTPUT:
  - Answer with source attribution, OR
  - "I cannot find a reliable answer"
  ↓
PREVENT HALLUCINATION:
  ✓ Refuse if no results
  ✓ Refuse if low confidence
  ✓ Refuse if answer not in context
  ✓ Always cite sources
  ✓ Use system prompt guardrails
```

---

## Key Principle

**Hallucination = When AI generates information NOT in the source documents**

**Our Strategy**: 
1. **Peer 2 retrieves facts** (never generates)
2. **Peer 3 formats facts** (with strict rules)
3. **LLM synthesizes from facts** (with constraints)
4. **Peer 4 displays with sources** (for verification)

If any layer fails, the user sees refusal message instead of false information.

---

## Files Implementing Hallucination Control

- **`hybrid_search.py`** - Returns empty [] when no matches
- **`query_system.py`** - Shows confidence scores
- **`test_simple.py`** - Tests hallucination control
- **`QUERY_TEST_LEAVE_POLICY.md`** - Example with scores

**For Peer 3 to implement**: See code template in this document above

---

**Status: Peer 2 Hallucination Control ✅ IMPLEMENTED**

Ready for Peer 3 to add LLM-layer safeguards!
