<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Pathway-Framework-orange?style=for-the-badge" alt="Pathway">
  <img src="https://img.shields.io/badge/KDS-Hackathon-purple?style=for-the-badge" alt="Hackathon">
  <img src="https://img.shields.io/badge/Track-A-green?style=for-the-badge" alt="Track A">
</p>

<h1 align="center">🔍 Narrative Consistency Reasoning System</h1>

<p align="center">
  <strong>A deterministic, explainable AI system for verifying character backstory consistency against full-length novels</strong>
</p>

<p align="center">
  <em>Built for KDS Hackathon Track A — Interpretable Predictions with Evidence-Based Explanations</em>
</p>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [System Architecture](#-system-architecture)
- [Pipeline Workflow](#-pipeline-workflow)
- [Core Components](#-core-components)
- [Data Structures](#-data-structures)
- [Constraint Dimensions](#-constraint-dimensions)
- [Installation](#-installation)
- [Usage](#-usage)
- [How It Works](#-how-it-works)
- [Example Walkthrough](#-example-walkthrough)
- [Testing](#-testing)
- [Configuration Guide](#-configuration-guide)
- [Performance](#-performance)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Problem Statement

Given a **hypothetical backstory** and a **full novel**, determine if the backstory is **consistent** with the character's behavior throughout the narrative.

### Requirements

| Requirement | Description |
|-------------|-------------|
| **Deterministic** | Same inputs always produce identical outputs |
| **Explainable** | Clear, human-readable reasoning for all predictions |
| **Evidence-Based** | References specific text snippets from the novel |
| **Scalable** | Efficiently handles long-form narratives |

### The Challenge

```mermaid
flowchart LR
    subgraph Input
        A[📖 Full Novel] 
        B[📝 Backstory Claim]
    end
    
    subgraph System
        C{🔍 Consistency<br/>Analysis}
    end
    
    subgraph Output
        D[✅ Consistent]
        E[❌ Inconsistent]
        F[📋 Evidence & Reasoning]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
```

---

## 💡 Solution Overview

We model characters as **evolving constraint systems** where behavioral patterns are extracted from narrative experiences and compared against backstory claims.

### Key Innovations

```mermaid
mindmap
  root((Narrative<br/>Reasoning))
    Constraint Modeling
      Multi-dimensional analysis
      Polarity detection
      Strength accumulation
    Incremental Learning
      Experience extraction
      State evolution
      History tracking
    Explainability
      Evidence retrieval
      Conflict detection
      Decision justification
    Determinism
      Rule-based logic
      No randomness
      Reproducible results
```

### Feature Highlights

| Feature | Description |
|---------|-------------|
| 🔄 **End-to-End Pipeline** | Complete ingestion to results generation |
| 🎯 **Constraint-Based Modeling** | Characters as multi-dimensional constraint systems |
| 📈 **Incremental Learning** | Constraints evolve through narrative experiences |
| ⚖️ **Polarity Detection** | Positive/negative pattern classification |
| ⚠️ **Conflict Analysis** | Severity-based inconsistency detection |
| 📎 **Evidence Retrieval** | Snippet extraction for explainability |
| 📊 **CSV Outputs** | Structured results for evaluation |

---

## 🏗️ System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph Input Layer
        N[📖 Novel Text]
        B[📝 Backstory Text]
    end
    
    subgraph Processing Layer
        subgraph Narrative Processing
            C[Chunker]
            E[Experience Detector]
        end
        
        subgraph Constraint Engine
            U[Constraint Updater]
            P[Backstory Parser]
            CMP[Constraint Comparator]
        end
    end
    
    subgraph State Management
        CS[Character State]
        BS[Backstory State]
    end
    
    subgraph Output Layer
        R[Results Generator]
        CSV[📊 results.csv]
    end
    
    N --> C --> E --> U --> CS
    B --> P --> BS
    CS --> CMP
    BS --> CMP
    CMP --> R --> CSV
    
    style Input Layer fill:#e1f5fe
    style Processing Layer fill:#fff3e0
    style State Management fill:#f3e5f5
    style Output Layer fill:#e8f5e9
```

### Component Diagram

```mermaid
classDiagram
    class DataIngestion {
        +ingest_novel(path) str
        +ingest_backstory(path) str
    }
    
    class NarrativeChunker {
        +chunk_novel(text) List~str~
    }
    
    class ExperienceDetector {
        +dimension_keywords dict
        +extract_experiences(chunk, chapter_id) List~Experience~
        +detect_experiences(chunks) List~Experience~
    }
    
    class ConstraintUpdater {
        +dimension_keywords dict
        +negative_keywords list
        +positive_keywords list
        +update_state(experience, state) CharacterState
    }
    
    class BackstoryParser {
        +dimension_keywords dict
        +negatives list
        +positives list
        +parse_backstory(text) CharacterState
    }
    
    class ConstraintComparator {
        +compare(story_state, backstory_state) dict
    }
    
    class EvidenceRetriever {
        +retrieve(evidence_ids) List~str~
    }
    
    DataIngestion --> NarrativeChunker
    NarrativeChunker --> ExperienceDetector
    ExperienceDetector --> ConstraintUpdater
    ConstraintUpdater --> ConstraintComparator
    BackstoryParser --> ConstraintComparator
    ConstraintComparator --> EvidenceRetriever
```

---

## 🔄 Pipeline Workflow

### Main Processing Flow

```mermaid
flowchart TD
    subgraph Phase1[Phase 1: Ingestion]
        A1[Start] --> A2[Load Novel Text]
        A2 --> A3[Load Backstory Text]
    end
    
    subgraph Phase2[Phase 2: Narrative Processing]
        A3 --> B1[Split into Chunks]
        B1 --> B2[Detect Experiences]
        B2 --> B3{Experience Found?}
        B3 -->|Yes| B4[Extract Dimension & Polarity]
        B3 -->|No| B5[Skip Sentence]
        B4 --> B6[Create Experience Object]
        B5 --> B2
        B6 --> B7[More Chunks?]
        B7 -->|Yes| B2
        B7 -->|No| C1
    end
    
    subgraph Phase3[Phase 3: Constraint Evolution]
        C1[Initialize Empty CharacterState]
        C1 --> C2{Process Experience}
        C2 --> C3[Detect Dimension Keywords]
        C3 --> C4[Determine Polarity]
        C4 --> C5[Update Constraint Strength]
        C5 --> C6[Add Evidence ID]
        C6 --> C7{More Experiences?}
        C7 -->|Yes| C2
        C7 -->|No| D1
    end
    
    subgraph Phase4[Phase 4: Backstory Analysis]
        D1[Parse Backstory Sentences]
        D1 --> D2[Extract Dimension Keywords]
        D2 --> D3[Determine Polarity]
        D3 --> D4[Create Backstory Constraints]
    end
    
    subgraph Phase5[Phase 5: Comparison & Decision]
        D4 --> E1[Compare Story vs Backstory]
        E1 --> E2{Polarity Match?}
        E2 -->|Yes| E3[Mark Consistent]
        E2 -->|No| E4[Calculate Severity]
        E4 --> E5[Record Conflict]
        E3 --> E6[Generate Decision]
        E5 --> E6
    end
    
    subgraph Phase6[Phase 6: Output]
        E6 --> F1[Compile Results]
        F1 --> F2[Write CSV]
        F2 --> F3[End]
    end
    
    style Phase1 fill:#e3f2fd
    style Phase2 fill:#fff8e1
    style Phase3 fill:#fce4ec
    style Phase4 fill:#e8f5e9
    style Phase5 fill:#f3e5f5
    style Phase6 fill:#e0f2f1
```

### Decision Logic Flow

```mermaid
flowchart TD
    A[Story Constraints vs Backstory Constraints] --> B{Dimensions Overlap?}
    B -->|No| C[Mark as Consistent<br/>No comparison possible]
    B -->|Yes| D{Polarity Match?}
    D -->|Yes| E[No Conflict for Dimension]
    D -->|No| F[Calculate Severity]
    F --> G{Max Strength >= 0.5?}
    G -->|Yes| H[HIGH Severity Conflict]
    G -->|No| I[MEDIUM Severity Conflict]
    H --> J{Any Conflicts?}
    I --> J
    E --> J
    J -->|Yes| K[Prediction: 0<br/>Decision: INCONSISTENT]
    J -->|No| L[Prediction: 1<br/>Decision: CONSISTENT]
    K --> M[Generate Explanation]
    L --> M
    M --> N[Output Results]
```

---

## 🧩 Core Components

### 1. Data Ingestion (`pathway_pipeline/ingestion.py`)

Handles loading of novel and backstory texts from various formats.

```python
# Supports: .txt, .pdf formats
ingestion = DataIngestion()
novel_text = ingestion.ingest_novel("data/novels/novel.txt")
backstory_text = ingestion.ingest_backstory("data/backstories/backstory.txt")
```

### 2. Narrative Chunker (`narrative/chunker.py`)

Splits large novels into processable semantic chunks.

```mermaid
flowchart LR
    A[Full Novel Text] --> B[Chunker]
    B --> C[Chunk 1]
    B --> D[Chunk 2]
    B --> E[Chunk 3]
    B --> F[...]
    B --> G[Chunk N]
```

### 3. Experience Detector (`narrative/experience_detector.py`)

Extracts meaningful character experiences using keyword-based detection.

```mermaid
flowchart TD
    A[Text Chunk] --> B[Split into Sentences]
    B --> C{Contains Dimension Keywords?}
    C -->|violence, fight, attack...| D[Violence Experience]
    C -->|authority, leader, obey...| E[Authority Experience]
    C -->|trust, betray, rely...| F[Trust Experience]
    C -->|None| G[Skip Sentence]
    D --> H[Generate Experience ID]
    E --> H
    F --> H
    H --> I[Create Experience Object]
```

### 4. Constraint Updater (`constraints/updater.py`)

Evolves character state based on detected experiences.

```mermaid
stateDiagram-v2
    [*] --> EmptyState: Initialize
    EmptyState --> ProcessingExperience: New Experience
    ProcessingExperience --> DetectDimension: Keyword Match
    DetectDimension --> DeterminePolarity: Dimension Found
    DeterminePolarity --> UpdateConstraint: Polarity Set
    UpdateConstraint --> ProcessingExperience: More Experiences
    UpdateConstraint --> FinalState: No More
    FinalState --> [*]
    
    note right of DetectDimension
        violence, authority, trust
    end note
    
    note right of DeterminePolarity
        positive vs negative keywords
    end note
```

### 5. Backstory Parser (`backstory/parser.py`)

Converts backstory text into constraint representation.

### 6. Constraint Comparator (`constraints/comparator.py`)

Analyzes compatibility and detects conflicts between story and backstory constraints.

### 7. Evidence Retriever (`evidence/retriever.py`)

Extracts supporting text snippets for explainability.

---

## 📦 Data Structures

### Core Schema

```mermaid
erDiagram
    Experience ||--o{ Constraint : generates
    Constraint ||--o{ CharacterState : belongs_to
    CharacterState ||--|{ Experience : references
    
    Experience {
        string id PK
        int chapter_id
        string event_type
        list involved_entities
        string outcome
        string raw_text_reference
    }
    
    Constraint {
        string dimension PK
        string polarity
        float strength
        list evidence_ids
    }
    
    CharacterState {
        dict constraints
        list history
    }
```

### Constraint Structure

| Field | Type | Description |
|-------|------|-------------|
| `dimension` | string | Category (violence, trust, authority) |
| `polarity` | string | "positive" or "negative" |
| `strength` | float | Confidence level (0.0 - 1.0) |
| `evidence_ids` | list | References to supporting experiences |

---

## 🎚️ Constraint Dimensions

The system currently tracks three core behavioral dimensions:

```mermaid
pie title Constraint Dimensions
    "Violence" : 33
    "Authority" : 33
    "Trust" : 34
```

### Dimension Details

| Dimension | Keywords | Description |
|-----------|----------|-------------|
| **Violence** | `violence`, `fight`, `attack`, `conflict`, `battle` | Fighting, conflict, aggression patterns |
| **Authority** | `authority`, `leader`, `rule`, `obey`, `defy` | Leadership, obedience, defiance behaviors |
| **Trust** | `trust`, `betray`, `rely`, `bond`, `distrust` | Relationships, betrayal, reliance dynamics |

### Polarity Detection

```mermaid
flowchart LR
    subgraph Negative Indicators
        N1[avoided]
        N2[refused]
        N3[never]
        N4[distrusted]
        N5[defied]
    end
    
    subgraph Positive Indicators
        P1[enjoyed]
        P2[liked]
        P3[trusted]
        P4[followed]
        P5[respected]
    end
    
    N1 & N2 & N3 & N4 & N5 --> NEG[🔴 NEGATIVE Polarity]
    P1 & P2 & P3 & P4 & P5 --> POS[🟢 POSITIVE Polarity]
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)
- Virtual environment (recommended)

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/your-repo/kds-hackathon.git
cd kds-hackathon/project

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate        # Windows

# 4. Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `pathway` | Data processing framework |
| `pandas` | Results serialization |
| `pdfplumber` | PDF text extraction |
| `pytest` | Testing framework |
| `openai` | LLM extraction (optional) |

---

## 📖 Usage

### Basic Execution

```bash
# Run the full pipeline
python pathway_pipeline/orchestration.py
```

### Input Files

Place your input files in the `data/` directory:

```
data/
├── novels/
│   └── your_novel.txt          # Full novel text
└── backstories/
    └── your_backstory.txt      # Backstory claims
```

### Output Format

The system generates `results/results.csv`:

| Column | Description |
|--------|-------------|
| `prediction` | 0 (inconsistent) or 1 (consistent) |
| `decision` | "inconsistent" or "consistent" |
| `reason` | Human-readable explanation |
| `trigger_summary` | Summary of conflicts detected |
| `checked_dimensions` | Dimensions that were analyzed |
| `conflict_dimensions` | Dimensions with conflicts |
| `conflict_details` | Detailed constraint comparisons |

---

## ⚙️ How It Works

### Strength Accumulation

Each time evidence for a constraint is found, strength increases:

```mermaid
xychart-beta
    title "Constraint Strength Over Experiences"
    x-axis [Exp1, Exp2, Exp3, Exp4, Exp5, Exp6, Exp7, Exp8, Exp9, Exp10]
    y-axis "Strength" 0 --> 1
    line [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
```

### Conflict Severity Calculation

```mermaid
flowchart TD
    A[Polarity Mismatch Detected] --> B[Get Story Strength]
    A --> C[Get Backstory Strength]
    B --> D[Max Strength = max Story, Backstory]
    C --> D
    D --> E{Max >= 0.5?}
    E -->|Yes| F[HIGH Severity]
    E -->|No| G[MEDIUM Severity]
    F --> H[Flag as Major Conflict]
    G --> I[Flag as Minor Conflict]
```

---

## 📝 Example Walkthrough

### Sample Novel Text

```
He always avoided violence.
He refused to fight even when threatened.
He chose to walk away from conflicts.
```

### Sample Backstory

```
He grew up enjoying violence.
He believed fighting was the solution to problems.
```

### Processing Steps

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant N as NarrativeChunker
    participant E as ExperienceDetector
    participant U as ConstraintUpdater
    participant B as BackstoryParser
    participant C as Comparator
    
    O->>N: chunk_novel(novel_text)
    N-->>O: [chunks]
    
    O->>E: detect_experiences(chunks)
    E-->>O: [Experience: violence, negative]
    
    loop Each Experience
        O->>U: update_state(exp, state)
        U-->>O: Updated CharacterState
    end
    Note right of U: violence: negative, strength: 0.3
    
    O->>B: parse_backstory(backstory_text)
    B-->>O: BackstoryState
    Note right of B: violence: positive, strength: 0.6
    
    O->>C: compare(story_state, backstory_state)
    Note over C: Polarity mismatch detected!<br/>Story: negative vs Backstory: positive
    C-->>O: {prediction: 0, conflicts: [...]}
```

### Result

```csv
prediction,decision,reason,trigger_summary,checked_dimensions,conflict_dimensions,conflict_details
0,inconsistent,One or more constraint conflicts exceeded severity thresholds.,1 conflicts detected.,,violence,Story violence: negative (0.3) | Backstory violence: positive (0.6)
```

**Interpretation:** The backstory claims the character enjoyed violence, but the novel shows consistent avoidance of violence → **INCONSISTENT**

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_constraints.py -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

| Component | Tests |
|-----------|-------|
| Constraint Comparison | ✅ Polarity mismatch detection |
| Conflict Severity | ✅ Threshold calculations |
| Evidence Collection | ✅ Snippet retrieval |

---

## 🔧 Configuration Guide

### Adding New Dimensions

1. **Update dimension keywords** in `constraints/updater.py`:

```python
self.dimension_keywords = {
    "violence": ["violence", "fight", "attack"],
    "authority": ["authority", "leader", "rule"],
    "trust": ["trust", "betray", "rely"],
    "loyalty": ["loyal", "betrayal", "allegiance"]  # NEW
}
```

2. **Mirror changes** in `narrative/experience_detector.py` and `backstory/parser.py`

3. **Test** with sample texts

### Modifying Polarity Keywords

Edit keyword lists in `ConstraintUpdater`:

```python
self.negative_keywords = ['avoided', 'refused', 'never', ...]
self.positive_keywords = ['enjoyed', 'liked', 'trusted', ...]
```

---

## 📈 Performance

### Characteristics

| Metric | Value |
|--------|-------|
| **Determinism** | 100% (rule-based, no randomness) |
| **Complexity** | O(n) linear with text length |
| **Memory** | Sequential chunk processing |
| **Speed** | Sub-second for typical novels |

### Scalability

```mermaid
flowchart LR
    A[Small Novel<br/>~10K words] -->|< 100ms| B[✅ Instant]
    C[Medium Novel<br/>~50K words] -->|< 500ms| D[✅ Fast]
    E[Large Novel<br/>~100K+ words] -->|< 2s| F[✅ Efficient]
```

---

## 📁 Project Structure

```
project/
├── 📂 pathway_pipeline/           # Data ingestion & orchestration
│   ├── __init__.py
│   ├── ingestion.py              # File reading utilities
│   └── orchestration.py          # Main pipeline entry point
│
├── 📂 narrative/                  # Text processing & experience detection
│   ├── __init__.py
│   ├── chunker.py                # Novel text chunking
│   └── experience_detector.py    # Experience extraction
│
├── 📂 constraints/                # Core constraint logic
│   ├── __init__.py
│   ├── schema.py                 # Data structures (Experience, Constraint, CharacterState)
│   ├── updater.py                # Constraint evolution
│   └── comparator.py             # Conflict detection
│
├── 📂 backstory/                  # Backstory parsing
│   ├── __init__.py
│   └── parser.py                 # Convert backstory to constraints
│
├── 📂 evidence/                   # Snippet retrieval
│   ├── __init__.py
│   └── retriever.py              # Evidence extraction
│
├── 📂 tests/                      # Unit tests
│   ├── __init__.py
│   └── test_constraints.py       # Constraint tests
│
├── 📂 data/                       # Input texts
│   ├── novels/                   # Novel files
│   └── backstories/              # Backstory files
│
├── 📂 results/                    # Output CSVs
│   └── results.csv               # Pipeline output
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Ensure** all tests pass (`pytest tests/ -v`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where possible

---

## 📄 License

This project is developed for the **KDS Hackathon**. See repository license for details.

---

## 🙏 Acknowledgments

- Built for **Track A** of the KDS Hackathon
- Uses **Pathway** for data processing framework
- Inspired by constraint-based reasoning systems

---

<p align="center">
  <strong>Made with ❤️ for KDS Hackathon</strong>
</p>

<p align="center">
  <a href="#-table-of-contents">⬆️ Back to Top</a>
</p>
