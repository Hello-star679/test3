# Adversarial Content Test Framework

A GAN-style adversarial testing framework for evaluating and stress-testing content classifiers and moderation systems.

## 🎯 Features

- **Web-based GUI** - Interactive interface for easy testing (no command line needed)
- **Multiple Detector Backends** - Mock, Hugging Face, OpenAI Moderation, Local Models
- **Template-Based Generation** - Safe, pre-approved content templates with controlled mutations
- **Evolutionary Algorithm** - GAN-style population evolution with fitness-based selection
- **Real-time Monitoring** - Live progress tracking with interactive charts
- **Result Analysis** - Comprehensive logging, visualization, and export tools
- **Flexible Configuration** - Full environment variable and GUI configuration support
- **Sandbox Mode** - Restricted API access by default for safety

## 🚀 Features

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Using the GUI (Recommended) 🎨

The easiest way to use the framework is through the interactive web GUI:

```bash
# Start the GUI
./start_gui.sh

# Then open http://localhost:8501 in your browser
```

**GUI Features:**
- ✨ Interactive configuration with sliders and dropdowns
- 📊 Real-time progress monitoring and charts
- 💾 Results visualization and export (JSON/CSV)
- 📈 History tracking of all test runs
- 🎯 No command line knowledge required

See [GUI_USER_GUIDE.md](GUI_USER_GUIDE.md) for detailed instructions.

### Command Line Usage

```bash
# Run with mock detector (no external dependencies)
python3 scripts/run_test.py --mock --epochs 10 --population 30

# Run with custom configuration
export MAX_EPOCHS=50
export POPULATION_SIZE=30
export DETECTOR_TYPE=hf
python3 scripts/run_test.py

# See all options
python3 scripts/run_test.py --help
```

## Configuration

Configure via environment variables in `.env` file:

```env
# Loop parameters
MAX_EPOCHS=50
POPULATION_SIZE=30
MUTATION_RATE=0.25
ELITE_RATIO=0.5

# Detector configuration
DETECTOR_TYPE=mock  # mock, hf, openai, local
USE_MOCK=False

# Hugging Face settings
HF_LOCAL_URL=http://localhost:8080
HF_MODEL_NAME=default-model

# OpenAI settings
OPENAI_API_KEY=your_key_here
OPENAI_THRESHOLD=0.7

# Local model settings
LOCAL_MODEL_PATH=./models/classifier
LOCAL_MODEL_LABEL=malicious

# Output
LOG_DIR=logs
SAVE_RESULTS=True
VERBOSE=True

# Security
SANDBOX_MODE=True
MAX_TEXT_LENGTH=500
```

## 🛠️ Architecture

### GUI Stack (Recommended)
- **Framework:** Streamlit (Python web framework)
- **Charts:** Plotly (interactive visualizations)
- **Data:** Pandas (result analysis)
- **Backend:** Same core framework with GUI wrapper

### Core Components (Used by both GUI and CLI)

1. **ConfigurableGenerator** (`src/generator.py`)
   - Generates test texts from templates
   - Applies mutations (substitution, insertion, deletion, case changes)
   - Supports multiple categories

2. **Detectors** (`src/detectors.py`)
   - MockDetector: Deterministic scoring for testing
   - HuggingFaceDetector: Supports local and cloud HF models
   - OpenAIModerationDetector: Uses OpenAI's API
   - LocalMLDetector: Loads local Hugging Face models

3. **AdversarialLoop** (`src/loop.py`)
   - Main evolutionary algorithm
   - Elite selection + offspring generation
   - Population tracking and statistics

4. **SandboxConfig** (`src/config.py`)
   - Centralized configuration management
   - Environment variable loading with defaults
   - Validation and security checks

## Usage Examples

### Run with Hugging Face Local Model

```bash
# Start HF inference server
docker run -p 8080:80 ghcr.io/huggingface/text-classification-cpu

# Run tests
export HF_LOCAL_URL=http://localhost:8080
python3 scripts/run_test.py --epochs 20 --population 30
```

### Analyze Results

```bash
python3 scripts/analyze_results.py logs/adversarial_results_*.json
```

### Diagnose Classifier

```bash
python3 scripts/diagnose_classifier.py --texts "text1" "text2" "text3"
```

## Output

Results are saved to `logs/adversarial_results_TIMESTAMP.json` with:

- Configuration used
- Best evasive text and score
- Per-epoch statistics (best, average, median scores)
- Top 10 texts from each generation
- Full history for analysis

## Security Considerations

- **Sandbox Mode**: Enabled by default to restrict external API calls
- **Template-Based**: Only uses pre-approved benign templates
- **Placeholder System**: Safe word lists prevent malicious content injection
- **Text Length Limits**: Configurable maximum text length
- **Environment Variables**: API keys stored securely via environment

## Requirements

**Core:**
- Python 3.8+
- requests
- python-dotenv

**For GUI (Recommended):**
- streamlit
- plotly
- pandas

**Optional:**
- transformers + torch (for local models)
- openai (for OpenAI API)
- psutil (for memory monitoring)

## Entry Points

```
adversarial-test      → scripts/run_test.py
analyze-results       → scripts/analyze_results.py
diagnose-classifier   → scripts/diagnose_classifier.py
```

## License

Proprietary - Internal Use Only

## Support

For issues or questions, refer to the internal documentation or contact the security team.
