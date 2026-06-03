# Full System Flow Diagram - Peer 2 Vector Search

**Complete end-to-end flow of what we built**

---

## 1. HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE RAG SYSTEM                         │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  PEER 1      │    │  PEER 2      │    │  PEER 3      │      │
│  │  Ingestion   │───▶│  Vector      │───▶│  Backend     │      │
│  │  Pipeline    │    │  Search      │    │  & LLM       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                    │              │
│                                                    ▼              │
│                                          ┌──────────────────┐   │
│                                          │  PEER 4          │   │
│                                          │  Frontend UI     │   │
│                                          └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. PEER 2 DETAILED FLOW

### Input Data (From Peer 1)
```
Raw Documents (PDFs, TXT)
    │
    ▼
┌─────────────────────────────────────────┐
│  PEER 1: Document Parser & Chunking     │
├─────────────────────────────────────────┤
│  - Parse PDFs/TXT files                 │
│  - Extract metadata                     │
│  - Split into chunks (fixed or semantic)│
│  - Output: JSON with chunks + metadata  │
└─────────────────────────────────────────┘
    │
    └──▶ output/ingestion_output_fixed.json
         output/ingestion_output_semantic.json
         
         Format:
         {
           "chunks": [
             {
               "text": "...",
               "chunk_id": "uuid",
               "document_name": "...",
               "department": "...",
               "category": "...",
               "version": "..."
             }
           ]
         }
```

---

## 3. PEER 2 VECTOR SEARCH PIPELINE

### Complete Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     PEER 2 PROCESSING                            │
└─────────────────────────────────────────────────────────────────┘

STEP 1: LOAD CHUNKS
═════════════════════════════════════════════════════════════════
    Input: output/ingestion_output_fixed.json
              │
              ▼
    ┌──────────────────────────────────────┐
    │ Load JSON Chunks                     │
    │ - 6 chunks loaded                    │
    │ - Extract text & metadata            │
    └──────────────────────────────────────┘
              │
              ▼
    chunks_cache = [
      {
        "text": "...",
        "department": "Engineering",
        "category": "Guide",
        ...
      },
      ...
    ]


STEP 2: EMBEDDING (Text → Numbers)
═════════════════════════════════════════════════════════════════
    Input: Text from each chunk
    Model: sentence-transformers/all-MiniLM-L6-v2
              │
              ▼
    ┌──────────────────────────────────────┐
    │ Embedding Service                    │
    │ - Load model (384 dimensions)        │
    │ - Convert text to vectors            │
    │ - Batch processing (efficient)       │
    └──────────────────────────────────────┘
              │
              ▼
    vectors = [
      [0.23, 0.15, 0.89, ..., 0.42],  # chunk 1
      [0.12, 0.34, 0.56, ..., 0.78],  # chunk 2
      ...
    ]


STEP 3: VECTOR DATABASE STORAGE
═════════════════════════════════════════════════════════════════
    Input: Vectors + Metadata
              │
              ▼
    ┌──────────────────────────────────────┐
    │ Qdrant Vector Database               │
    │ - Create collection                  │
    │ - Store 6 vectors (384-dim each)     │
    │ - Store metadata as payloads         │
    │ - Use Cosine similarity              │
    └──────────────────────────────────────┘
              │
              ▼
    ./qdrant_storage/
    └── collections/
        └── enterprise_chunks/
            ├── vectors.dat (6 × 384 floats)
            ├── payloads.dat (metadata)
            └── ...


STEP 4: BUILD BM25 LEXICAL INDEX
═════════════════════════════════════════════════════════════════
    Input: Text chunks
              │
              ▼
    ┌──────────────────────────────────────┐
    │ BM25 Algorithm                       │
    │ - Tokenize chunk text                │
    │ - Build term frequency index         │
    │ - Calculate BM25 scores              │
    └──────────────────────────────────────┘
              │
              ▼
    bm25_index = BM25Okapi([
      ["system", "requirements", ...],
      ["remote", "work", "policy", ...],
      ...
    ])
```

---

## 4. QUERY PROCESSING FLOW

### When User Asks a Question

```
USER INPUT
═════════════════════════════════════════════════════════════════
    "What is the leave policy?"
    
    ▼

STEP 1: PARSE QUERY & FILTERS
═════════════════════════════════════════════════════════════════
    query = "What is the leave policy?"
    filters = {
      "category": "Policy"  # (optional)
    }
    search_type = "hybrid"
    top_k = 5
    
    ▼

STEP 2: HYBRID SEARCH
═════════════════════════════════════════════════════════════════

    ┌─────────────────────────────────────────────┐
    │ PATH A: DENSE VECTOR SEARCH                 │
    ├─────────────────────────────────────────────┤
    │  1. Embed user query (384 dimensions)      │
    │  2. Search Qdrant with embedding           │
    │  3. Calculate cosine similarity            │
    │  4. Get top-k results by similarity        │
    └─────────────────────────────────────────────┘
              │
              ▼
    dense_results = [
      {chunk_id: "abc", dense_score: 0.88},
      {chunk_id: "def", dense_score: 0.75},
      ...
    ]

    ┌─────────────────────────────────────────────┐
    │ PATH B: SPARSE BM25 SEARCH                  │
    ├─────────────────────────────────────────────┤
    │  1. Tokenize user query                    │
    │  2. Query BM25 index                       │
    │  3. Calculate BM25 scores                  │
    │  4. Get top-k results by score             │
    └─────────────────────────────────────────────┘
              │
              ▼
    sparse_results = [
      {chunk_id: "abc", bm25_score: 1.0},
      {chunk_id: "ghi", bm25_score: 0.66},
      ...
    ]


STEP 3: APPLY METADATA FILTERS
═════════════════════════════════════════════════════════════════
    For each chunk in dense_results:
      IF filter exists:
        IF chunk.category != "Policy":
          SKIP chunk
        ELSE:
          KEEP chunk
          
    After filtering:
    filtered_results = [
      {chunk_id: "abc", ...},  ✓ matches filter
      {chunk_id: "def", ...},  ✓ matches filter
    ]


STEP 4: COMBINE SCORES
═════════════════════════════════════════════════════════════════
    For each matching chunk:
      combined_score = (dense_score × 0.6) + (bm25_score × 0.4)
    
    Example:
      chunk_abc:
        dense_score = 0.88
        bm25_score = 1.0
        combined = (0.88 × 0.6) + (1.0 × 0.4) = 0.528 + 0.4 = 0.928
      
      chunk_def:
        dense_score = 0.75
        bm25_score = 0.66
        combined = (0.75 × 0.6) + (0.66 × 0.4) = 0.45 + 0.264 = 0.714


STEP 5: RANK & RETURN RESULTS
═════════════════════════════════════════════════════════════════
    Sort by combined_score (descending):
    
    top_results = [
      {
        rank: 1,
        chunk_id: "abc",
        document_name: "v2_remote_policy",
        text: "...",
        combined_score: 0.928,
        dense_score: 0.88,
        sparse_score: 1.0,
        department: "HR",
        category: "Policy",
        version: "2"
      },
      {
        rank: 2,
        chunk_id: "def",
        ...
        combined_score: 0.714,
        ...
      }
    ]
    
    ▼

RESULTS RETURNED TO USER
═════════════════════════════════════════════════════════════════
    - Source: v2_remote_policy (v2)
    - Confidence: 92.8%
    - Text: [full chunk content]
    - Metadata: HR, Policy, v2
```

---

## 5. SYSTEM COMPONENTS & INTERACTION

```
┌──────────────────────────────────────────────────────────────────┐
│                    PEER 2 COMPONENTS                              │
└──────────────────────────────────────────────────────────────────┘

User Query
    │
    ├─────────────────────────────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
┌─────────────────────────┐          ┌──────────────────────────┐
│  QUERY PARSER           │          │  EMBEDDING SERVICE       │
│  - Parse question       │          │  - Load model            │
│  - Extract filters      │          │  - Embed query (384-dim) │
│  - Set parameters       │          │  - Cache embeddings      │
└─────────────────────────┘          └──────────────────────────┘
    │                                          │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────┐
        │  HYBRID SEARCH ENGINE                │
        │  ┌────────────────────────────────┐  │
        │  │ Dense Search Module            │  │
        │  │  - Query Qdrant vector DB      │  │
        │  │  - Cosine similarity scoring   │  │
        │  └────────────────────────────────┘  │
        │  ┌────────────────────────────────┐  │
        │  │ Sparse Search Module           │  │
        │  │  - Query BM25 index            │  │
        │  │  - Keyword matching            │  │
        │  └────────────────────────────────┘  │
        │  ┌────────────────────────────────┐  │
        │  │ Metadata Filter Module         │  │
        │  │  - Check department/category   │  │
        │  │  - Hard filtering (AND logic)  │  │
        │  └────────────────────────────────┘  │
        │  ┌────────────────────────────────┐  │
        │  │ Score Combiner Module          │  │
        │  │  - Weighted combination        │  │
        │  │  - 60% dense + 40% sparse      │  │
        │  └────────────────────────────────┘  │
        └──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────┐
        │  QDRANT DATABASE                     │
        │  - 6 vectors (384-dim)               │
        │  - Metadata payloads                 │
        │  - Local disk storage                │
        └──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────┐
        │  BM25 INDEX                          │
        │  - Tokenized chunks                  │
        │  - Term frequency scores             │
        │  - In-memory index                   │
        └──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────┐
        │  RESULT FORMATTER                    │
        │  - Rank by combined score            │
        │  - Add source attribution            │
        │  - Include confidence scores         │
        │  - Return metadata                   │
        └──────────────────────────────────────┘
                   │
                   ▼
            Results (Top-K)
```

---

## 6. DATA TRANSFORMATION FLOW

```
INPUT                          TRANSFORMATION                  OUTPUT
═════════════════════════════════════════════════════════════════════

Raw Text                      Embedding Service              Vector (384-dim)
"What are system             ─────────────────────────────▶  [0.23, 0.15, ...]
 requirements?"               all-MiniLM-L6-v2


Raw Text                      Tokenization                   Tokens
"system requirements"         ─────────────────────────────▶  ["system", 
                              (word split)                     "requirements"]


Raw Text                      BM25 Algorithm                 BM25 Score
"setup Python PostgreSQL"     ─────────────────────────────▶  1.23


Vector 1: [0.88, ...]         Dense Score + Sparse Score     Combined Score
BM25 Score: 1.0               ─────────────────────────────▶  (0.88×0.6) + 
                              Weighted Combination           (1.0×0.4) = 0.928


Multiple Results              Ranking & Filtering            Final Results
{chunk_1, score: 0.93}        ─────────────────────────────▶  [{
{chunk_2, score: 0.71}        - Apply metadata filters         rank: 1,
{chunk_3, score: 0.45}        - Sort by score                  score: 0.93,
                              - Limit to top-k                chunk_id: "...",
                                                               text: "...",
                                                               metadata: {...}
                                                             }]
```

---

## 7. FILE STRUCTURE & FLOW

```
INPUT FILES (From Peer 1)
├── output/ingestion_output_fixed.json     ◄── Chunks (6 docs)
└── output/ingestion_output_semantic.json  ◄── Alternative chunks

                    │
                    ▼

PROCESSING (Peer 2)
├── vector_db_init.py          ◄── Orchestration script
├── embedding_service.py       ◄── Text → Vector conversion
├── qdrant_setup.py            ◄── Database management
└── hybrid_search.py           ◄── Main search engine

                    │
                    ▼

STORAGE (Local Disk)
├── ./qdrant_storage/          ◄── Vector database (6 vectors)
│   ├── collections/
│   │   └── enterprise_chunks/
│   │       ├── vectors.dat
│   │       ├── payloads.dat
│   │       └── metadata.json
│   └── snapshots/

                    │
                    ▼

QUERY INTERFACE (Peer 2 Output)
├── query_system.py            ◄── Python API
├── ask_questions.py           ◄── Interactive CLI
└── retrieve_relevant_chunks() ◄── Main function for Peer 3

                    │
                    ▼

TO PEER 3
[Results with scores & metadata]
```

---

## 8. FILTERING FLOW

```
USER QUERY WITH FILTERS
═════════════════════════════════════════════════════════════════

Input:
  query = "deployment process"
  filters = {
    "department": "Engineering",
    "category": "Guide"
  }

Step 1: Search all documents
  ├─ engineering_guide (matches both filters) ✓
  ├─ hr_policy (doesn't match department)    ✗
  ├─ ops_guide (doesn't match department)    ✗
  └─ eng_policy (doesn't match category)     ✗

Step 2: Apply filters
  Dense Search                  Sparse Search
  ┌─────────────────┐          ┌─────────────────┐
  │ Only check docs │          │ Only check docs │
  │ matching       │          │ matching       │
  │ Engineering    │          │ Engineering    │
  │ + Guide        │          │ + Guide        │
  └─────────────────┘          └─────────────────┘
           │                           │
           └────────────┬─────────────┘
                        │
                        ▼
                  eng_guide (rank 1)

Output: Only documents that match ALL filters
```

---

## 9. CONFIDENCE SCORING BREAKDOWN

```
QUERY: "What is the leave policy?"

Dense Search (Semantic Understanding)
════════════════════════════════════════════════════════════════
  Query Embedding: [0.12, 0.34, 0.56, ...]
  
  Compare with: v2_remote_policy embedding
  Cosine Similarity: 0.000 (no semantic match)
  Dense Score: 0.000
  
BM25 Sparse Search (Keyword Matching)
════════════════════════════════════════════════════════════════
  Query Tokens: ["leave", "policy"]
  
  v2_remote_policy contains: "policy" (exact match)
  BM25 Algorithm calculates importance
  BM25 Score: 1.000 (perfect match)
  
Combining Scores (Hybrid)
════════════════════════════════════════════════════════════════
  combined = (dense × 0.6) + (sparse × 0.4)
  combined = (0.000 × 0.6) + (1.000 × 0.4)
  combined = 0.000 + 0.400
  combined = 0.400 = 40% confidence
  
Interpretation:
  ✓ Document matches keywords perfectly (BM25)
  ✗ Semantic understanding is weak (Dense)
  → Result is shown because keyword match is strong
```

---

## 10. COMPLETE USER JOURNEY

```
USER STARTS
    │
    ▼
"What is the leave policy?"
    │
    ├──────────────────────────────────┐
    │  System Processing                │
    │  1. Parse query                   │
    │  2. Embed with model              │
    │  3. Dense search in Qdrant        │
    │  4. Sparse search in BM25         │
    │  5. Apply filters                 │
    │  6. Combine scores                │
    │  7. Rank results                  │
    │  8. Format output                 │
    └──────────────────────────────────┘
    │
    ▼
RESULTS DISPLAYED
    ┌─────────────────────────────────────┐
    │ 1. v2_remote_policy (v2)            │
    │    Category: Policy | Department: HR│
    │    Confidence: 40%                  │
    │                                     │
    │    Remote work policy...            │
    │    (text preview)                   │
    │                                     │
    │    Scores:                          │
    │    - Combined: 0.400                │
    │    - Dense: 0.000                   │
    │    - Sparse: 1.000                  │
    └─────────────────────────────────────┘
    │
    ▼
SENT TO PEER 3
    │
    ├─ Document name: v2_remote_policy
    ├─ Full text
    ├─ Metadata (HR, Policy, v2)
    ├─ Confidence score: 0.40
    └─ Original text chunks
    │
    ▼
PEER 3 USES FOR LLM
    │
    ├─ Formats as context
    ├─ Passes to LLM
    ├─ LLM generates answer
    └─ Includes source attribution
    │
    ▼
SENT TO PEER 4 (Frontend)
    │
    ├─ Display answer
    ├─ Show source
    ├─ Display confidence
    └─ Show full document option
    │
    ▼
USER SEES ANSWER
```

---

## 11. ERROR HANDLING & HALLUCINATION CONTROL

```
QUERY PROCESSING
    │
    ├─ Search executed
    │
    ▼
RESULTS FOUND?
    │
    ├─ YES: results > 0
    │  └──▶ Check confidence score
    │       │
    │       ├─ High (> 0.5): Return results
    │       │
    │       └─ Low (< 0.5): Can return but flag
    │
    └─ NO: results == 0
       │
       └──▶ HALLUCINATION CONTROL TRIGGERED
           │
           └──▶ Return empty list []
               │
               └──▶ Peer 3 sees no results
                   │
                   └──▶ Returns: "Cannot find reliable answer"
                       │
                       └──▶ User gets NO false information ✓
```

---

## 12. INTEGRATION WITH OTHER PEERS

```
PEER 1 INPUT                PEER 2 PROCESSING              PEER 3 OUTPUT
═════════════════════════════════════════════════════════════════════════════

Documents              Store & Index                  Query API
├─ PDFs          ──────────────────────────────────▶  retrieve_relevant_chunks()
├─ Text files          (6 vectors, 384-dim)           │
└─ Markdown            (BM25 index)                    │
                       (Metadata)                      ▼
Chunks                                           Format for LLM
├─ Text                                          ├─ Add context
├─ Metadata            Hybrid Search              ├─ Add sources
└─ IDs                 (Dense + Sparse)           ├─ Format prompt
                       + Filters                  └─ Call LLM
                       + Ranking                       │
                                                       ▼
                                                  PEER 4
                                                  ├─ Display results
                                                  ├─ Show sources
                                                  └─ Show confidence


PEER 5 EVALUATION
│
├─ Test with fixed chunks
├─ Test with semantic chunks
├─ Compare dense vs hybrid
├─ Measure precision/recall
└─ Calculate hallucination rate
```

---

## Summary: Complete System in One Image

```
┌────────────┐         ┌─────────────────────┐         ┌─────────┐
│  PEER 1    │         │     PEER 2          │         │ PEER 3  │
│ Documents  │  JSON   │ Vector Search       │ Results │ Backend │
│ Chunking   │────────▶│ - Dense (semantic)  │────────▶│ & LLM   │
│            │Chunks   │ - Sparse (keywords) │Ranked   │         │
└────────────┘         │ - Filters           │Chunks   └────┬────┘
                       │ - Ranking           │              │
                       │                     │              ▼
                       │  Storage:           │         ┌─────────┐
                       │ - Qdrant (vectors)  │         │ PEER 4  │
                       │ - BM25 (keywords)   │         │Frontend │
                       │ - Metadata          │         └─────────┘
                       └─────────────────────┘
                               △
                               │
                               │ Test & Evaluate
                               │
                       ┌───────┴───────┐
                       │   PEER 5      │
                       │ Evaluation    │
                       │ & Comparison  │
                       └───────────────┘
```

---

## Key Takeaway

**What We Built (Peer 2)**:
1. ✓ Takes chunks from Peer 1
2. ✓ Converts text to vectors (embedding)
3. ✓ Stores in Qdrant database
4. ✓ Creates BM25 index for keywords
5. ✓ Searches using hybrid method (dense + sparse)
6. ✓ Applies metadata filters
7. ✓ Ranks results by combined score
8. ✓ Returns results with sources
9. ✓ Controls hallucination (returns empty if no match)
10. ✓ Passes results to Peer 3

**Complete, Flexible, Production-Ready!** ✅
