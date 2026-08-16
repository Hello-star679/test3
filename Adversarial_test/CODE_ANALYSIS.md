# Adversarial Content Test Framework - Code Analysis

## Project Overview

This is a **GAN-style adversarial testing framework** for content classifiers. The system iteratively generates test texts and uses evolutionary algorithms to find edge cases and boundary conditions that might evade content moderation systems.

**Purpose:** Internal security/red-team testing framework to identify weaknesses in content classifiers

**Target Python:** 3.8+

---

## Architecture

```
┌─────────────────┐
│  ConfigurableGenerator    │  ← Creates test texts from templates
└──────┬──────────┘
       │ generates
       ▼
┌──────────────────┐
│  AdversarialLoop │  ← Orchestrates GAN-style evolution cycle
└──────┬───────────┘
       │ uses
       ▼
┌──────────────────┐
│  BaseDetector    │  ← Scores texts (multiple backends)
└──────────────────┘
       ▲
       │ implements
       ├─ MockDetector (test/fallback)
       ├─ HuggingFaceDetector (ML models)
       ├─ OpenAIDetector (OpenAI API)
       └─ LocalModelDetector (local models)
```

**Main Flow:**
1. Initialize population of random test texts
2. Score each text via detector (lower score = evaded better)
3. Select elite texts (lowest scores)
4. Generate offspring through mutations
5. Repeat N iterations
6. Save results and analysis

---

## Core Components

### 1. **SandboxConfig** (`config.py`)
**Purpose:** Centralized configuration management via environment variables

**Key Settings:**
- **Loop Parameters:** `max_iterations` (50), `population_size` (30), `mutation_rate` (0.25), `elite_ratio` (0.5)
- **Detector:** Type selection (mock/hf/openai/local), endpoint URLs, timeouts
- **Generator:** Template files, categories, text length limits
- **Security:** `sandbox_mode` (restrict API calls), `max_text_length` (500)
- **Output:** Log directory, verbosity, debug flags

**Strengths:**
✅ Comprehensive validation in `__post_init__`
✅ Sensible defaults with env var override capability
✅ Graceful fallback to mock mode if resources unavailable

**Issues:**
⚠️ **Typo in directory:** Framework looks for `src/` but workspace has `scr/` - this will cause import failures
⚠️ No type hints on container defaults (e.g., `template_categories` list handling)
⚠️ API keys stored in environment variables (standard practice, but ensure `.env` is in `.gitignore`)

---

### 2. **ConfigurableGenerator** (`generator.py`)
**Purpose:** Generate test texts from templates with controlled mutations

**Key Features:**
- Loads templates from category-specific files (account.txt, security.txt, etc.)
- Safe placeholder system: uses benign words like "verify", "account", "password"
- Mutation operations:
  - Character substitution (typos)
  - Word substitution
  - Word insertion/deletion
  - Case/punctuation changes

**Template System:**
```python
"Your {} needs {}." + ["user", "account"] → "Your account needs verification."
```

**Strengths:**
✅ Modular placeholder dictionary (easy to customize)
✅ Fallback templates if files don't load
✅ Category-based organization
✅ Comment support in template files (#)

**Issues:**
⚠️ **Incomplete mutation function** - Code cuts off at line 150, missing critical mutation logic
⚠️ **Placeholder safety** - No validation that generated text remains "benign" after mutations
⚠️ Mutation rate not properly controlled (random selection vs. probability-based)
⚠️ No length validation before returning mutated text

---

### 3. **BaseDetector & Implementations** (`detectors.py`)

#### **MockDetector**
- Deterministic scoring based on: text length, character uniqueness, presence of keywords
- Uses MD5 hash for reproducible "randomness"
- Good for testing without external dependencies

#### **HuggingFaceDetector**
- Supports local and cloud endpoints
- **Smart response parsing:** Auto-detects multiple HF model output formats:
  - Format A: `[{"label": "malicious", "score": 0.95}, ...]`
  - Format B: `{"prediction": 0.89, ...}`
- Configurable authentication & timeouts
- Batch scoring support

**Strengths:**
✅ Flexible response format handling
✅ Timeout protection
✅ Support for both local/cloud

**Issues:**
⚠️ **Code incomplete** - Cuts off during response format handling
⚠️ No retry logic for timeouts
⚠️ No error handling for malformed JSON responses

---

### 4. **AdversarialLoop** (`loop.py`)
**Purpose:** Main evolutionary algorithm orchestrator

**Key Algorithm:**
1. Initialize population of `population_size` random texts
2. Evaluate all texts (score via detector)
3. Select elite texts (top `elite_ratio` %)
4. Generate offspring via mutation
5. Replace population and iterate

**Strengths:**
✅ Duplicate detection (`seen_texts` set)
✅ Multi-category support in initialization
✅ Tracks best text/score across all generations

**Issues:**
⚠️ **Code incomplete** - `_select_parent()` cuts off mid-function
⚠️ Elite selection weights inversely by score - works but could be optimized
⚠️ No convergence detection (continues even if population stagnates)
⚠️ No metric tracking (diversity, average score progression, etc.)

---

### 5. **Utilities** (`utils.py`)
Standard helper functions:
- `create_timestamp()` - Filename generation
- `load_json()` / `save_json()` - Persistent storage
- `progress_bar()` - Terminal UI
- `get_memory_usage()` - System monitoring (requires `psutil`)

**Status:** ✅ Complete and functional

---

## Entry Point: `run_test.py`
- Parses CLI arguments (`--mock`, `--epochs`, `--population`, etc.)
- Loads `SandboxConfig`
- Creates generator and detector instances
- Runs main adversarial loop

**Status:** ⚠️ Incomplete (cuts off at line 80)

---

## Critical Issues Summary

| Issue | Severity | Location | Impact |
|-------|----------|----------|--------|
| Directory naming: `scr/` vs `src/` | **CRITICAL** | Workspace root | Framework won't import |
| Incomplete `generator.mutate()` | **HIGH** | `generator.py` line 150+ | Mutations won't work |
| Incomplete `detectors.py` | **HIGH** | `detectors.py` line 150+ | HF/OpenAI detection broken |
| Incomplete `loop.py` | **HIGH** | `loop.py` line 150+ | Parent selection broken |
| Incomplete `run_test.py` | **HIGH** | `run_test.py` line 80+ | Entry point non-functional |
| No convergence detection | **MEDIUM** | `loop.py` | Algorithm inefficient |
| Limited error handling | **MEDIUM** | `detectors.py` | Fragile on API failures |
| Mutation rate not enforced | **MEDIUM** | `generator.py` | Unpredictable mutations |

---

## Dependencies & Extras

**Core (Required):**
- `requests` - HTTP calls to detector APIs
- `python-dotenv` - Environment configuration

**Optional:**
- `transformers` + `torch` - Local HF models
- `openai` - OpenAI API integration
- `psutil` - Memory monitoring
- `tqdm` - Progress bars

---

## Security Considerations

✅ **Good:**
- Sandbox mode restricts external API calls by default
- Placeholder words are pre-approved (no dynamic injection)
- Text length limits enforced
- API keys via environment variables

⚠️ **Concerns:**
- Template files loaded from user-controlled paths (potential arbitrary file read)
- No input validation on detector endpoints
- Mock detector produces somewhat predictable scores (hash-based)

---

## Recommendations

### Immediate Fixes (CRITICAL)
1. **Fix directory naming:** Rename `scr/` → `src/` or update imports everywhere
2. **Complete truncated functions:** Finish `mutate()`, detector implementations, `_select_parent()`, `run_test.py`
3. **Add error handling:** Wrap all API calls in try/except with proper logging

### Enhancements (MEDIUM)
4. **Convergence detection:** Stop early if population fitness plateaus
5. **Metrics tracking:** Log average score, diversity, top-N texts per generation
6. **Batch scoring:** Use detector batch APIs for 10-100x speedup
7. **Genetic diversity:** Implement fitness-proportional selection or crossover
8. **Result export:** Add CSV/JSON output with per-generation statistics

### Code Quality (LOW)
9. Add comprehensive docstrings to all functions
10. Add type hints throughout
11. Add unit tests for detector backends
12. Configure CI/CD for linting (`black`, `flake8`)

---

## Testing Strategy

```bash
# Test with mock detector (no external dependencies)
python -m scripts.run_test --mock --epochs 5 --population 10

# Test with Hugging Face local model
HF_LOCAL_URL=http://localhost:8080 python -m scripts.run_test --epochs 20

# Debug mode with verbose output
python -m scripts.run_test --debug --verbose
```

---

## Files & Ownership

| File | Lines | Status | Comments |
|------|-------|--------|----------|
| `config.py` | ~100 | ✅ Complete | Well-designed config management |
| `generator.py` | ~200+ | ⚠️ Incomplete | Mutation logic truncated |
| `detectors.py` | ~250+ | ⚠️ Incomplete | OpenAI/LocalModel missing |
| `loop.py` | ~180+ | ⚠️ Incomplete | Evolution algorithm incomplete |
| `utils.py` | ~50 | ✅ Complete | Helper functions OK |
| `run_test.py` | ~80+ | ⚠️ Incomplete | Entry point not functional |
| `setup.py` | 40 | ✅ Complete | Package config proper |
| `requirements.txt` | 15 | ✅ Complete | Dependency pinning good |

---

## Conclusion

This is a **well-architected framework** with a clear separation of concerns (config/generation/detection/evolution). The design supports multiple detector backends and flexible text generation. However, **the codebase is incomplete** - several critical functions are truncated, and there's a directory naming issue that prevents execution.

**Priority:** Fix the incomplete functions and directory structure first, then address error handling and performance optimizations.

