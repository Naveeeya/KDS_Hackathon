# KDSH 2026 - Narrative Consistency Analysis

## Setup Instructions

### 1. Install Dependencies
```bash
cd project
pip install -r requirements.txt
```

### 2. Run Batch Processing
```bash
python3 run_kdsh.py
```

Results will be saved to `results/results.csv`

## Approach

This project uses a **Constraint-Based Reasoning System** enhanced with **Pathway Vector Store**.

1.  **Pathway Integration**: Uses Pathway for efficient semantic retrieval of relevant novel passages.
2.  **Constraint Logic**: Extracts character constraints (values, behaviors) from separate backstories and compares them against the novel's narrative evidence.
3.  **Conflict Detection**: Identifies mismatches in 6 dimensions: violence, authority, trust, courage, loyalty, morality.

## Project Structure

See `project/README.md` for detailed documentation.

## Hackathon Submission

- **Track**: A (Systems Reasoning)
- **Approach**: Constraint-based reasoning + Pathway vector store
- **Novel Contribution**: Detailed constraint evolution modeling with semantic retrieval
