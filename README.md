# KDSH 2026 - Narrative Consistency Analysis

## Setup Instructions

### 1. Install Dependencies
```bash
cd project
pip install -r requirements.txt
```

### 2. Configure API Key (Required for LLM mode)
```bash
# Copy the example file
cp ../.env.example ../.env

# Edit .env and add your OpenAI API key
# Get a free key from: https://platform.openai.com/api-keys
```

### 3. Run Batch Processing
```bash
python3 run_kdsh.py
```

Results will be saved to `results/results.csv`

## API Usage

This project uses **OpenAI's free tier API** (gpt-4o-mini model) for enhanced accuracy.
- Free tier includes $5 credit
- Model is configurable via `.env` file
- Fallback to constraint-only mode if API key not provided

## Project Structure

See `project/README.md` for detailed documentation.

## Hackathon Submission

- **Track**: A (Systems Reasoning with NLP and Generative AI)
- **Approach**: Constraint-based reasoning + Pathway vector store + LLM verification
- **Novel Contribution**: Hybrid constraint evolution with semantic retrieval
