# GUI Architecture & Features

## Overview

The Adversarial Test Framework includes a modern web-based GUI built with Streamlit. The GUI provides an easy-to-use interface for running adversarial tests without needing command-line knowledge.

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | Streamlit | Interactive Python web app |
| **Visualizations** | Plotly | Interactive charts and graphs |
| **Data Processing** | Pandas | Result analysis and export |
| **Backend** | Python 3.8+ | Core framework logic |
| **Storage** | JSON/CSV | Result persistence |

## Streamlit Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit GUI (gui.py)          │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Sidebar Configuration Panel    │   │
│  │ • Detector Type Selection       │   │
│  │ • Algorithm Parameters (sliders)│   │
│  │ • Detector-specific Options     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Main Content (4 Tabs)          │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Tab 1: Run Test         │    │   │
│  │  │ • Config Summary        │    │   │
│  │  │ • Start/Quick/Debug Btn │    │   │
│  │  │ • Real-time Progress    │    │   │
│  │  │ • Score Progression     │    │   │
│  │  └─────────────────────────┘    │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Tab 2: Results          │    │   │
│  │  │ • Summary Metrics       │    │   │
│  │  │ • Best Text Found       │    │   │
│  │  │ • History Table         │    │   │
│  │  │ • Export Buttons        │    │   │
│  │  └─────────────────────────┘    │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Tab 3: Analysis         │    │   │
│  │  │ • Statistics            │    │   │
│  │  │ • Score Distribution    │    │   │
│  │  │ • Top Texts Table       │    │   │
│  │  └─────────────────────────┘    │   │
│  │                                 │   │
│  │  ┌─────────────────────────┐    │   │
│  │  │ Tab 4: History          │    │   │
│  │  │ • Previous Runs Table   │    │   │
│  │  │ • Result Viewer         │    │   │
│  │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
        ↓ Uses ↓
┌─────────────────────────────────────────┐
│      Core Framework (src/)              │
│ • ConfigurableGenerator                 │
│ • BaseDetector & Implementations        │
│ • AdversarialLoop                       │
│ • SandboxConfig                         │
│ • Utils                                 │
└─────────────────────────────────────────┘
        ↓ Outputs ↓
┌─────────────────────────────────────────┐
│        Results Storage (logs/)          │
│ • JSON results files                    │
│ • Timestamped per run                   │
│ • Accessible from History tab           │
└─────────────────────────────────────────┘
```

## File Structure

```
Adversarial_test/
├── gui.py                    # Main Streamlit GUI application
├── start_gui.sh             # Startup script
├── gui_status.sh            # Status check script
├── GUI_USER_GUIDE.md        # Comprehensive user guide
├── src/
│   ├── config.py            # Configuration management
│   ├── generator.py         # Text generation & mutation
│   ├── detectors.py         # Detector implementations
│   ├── loop.py              # Evolutionary algorithm
│   └── utils.py             # Utility functions
├── scripts/
│   ├── run_test.py          # CLI entry point
│   ├── analyze_results.py   # Result analysis script
│   └── diagnose_classifier.py # Diagnostic tool
└── logs/                    # Results storage
    └── adversarial_results_*.json
```

## Key Features

### 1. Configuration Panel (Sidebar)

**Purpose:** Central location for all test parameters

**Features:**
- Detector type dropdown (mock, HF, OpenAI, local)
- Algorithm parameters with sliders:
  - Max epochs (1-100)
  - Population size (5-100)
  - Mutation rate (0.01-1.0)
  - Elite ratio (0.1-0.9)
- Text generation options:
  - Max text length
  - Category selection
- Detector-specific configuration

**Benefits:**
- Easy parameter tuning without code
- Real-time validation
- Sensible defaults
- Clear value ranges

### 2. Run Test Tab

**Purpose:** Execute adversarial testing campaigns

**Features:**
- Configuration summary table
- Three execution modes:
  - Full Test (custom settings)
  - Quick Test (3 epochs)
  - Debug Mode (2 epochs)
- Real-time progress tracking:
  - Progress bar
  - Status messages
  - Per-epoch metrics
  - Interactive score chart
  - Live updates

**User Experience:**
- Click button → immediate feedback
- Progress visible in real-time
- Can see results as they happen
- No need to check terminal

### 3. Results Tab

**Purpose:** View and analyze test outcomes

**Features:**
- Summary metrics (best score, epochs, population)
- Best text display
- Detailed epoch-by-epoch results table
- Interactive score progression chart
- Export buttons:
  - JSON (complete data)
  - CSV (spreadsheet-compatible)

**Visualizations:**
- Line chart with best and average scores
- Hover details with exact values
- Color-coded traces (red=best, blue=average)

### 4. Analysis Tab

**Purpose:** Deep dive into results

**Features:**
- Score statistics:
  - Best, worst, average
  - Improvement calculation
- Configuration summary table
- Score distribution chart:
  - Box plot by epoch
  - Shows population variance
- Top texts table:
  - Best 3 texts per epoch
  - Track evolution

**Insights:**
- Understand algorithm effectiveness
- Identify convergence patterns
- Compare scores across epochs
- Track best solutions

### 5. History Tab

**Purpose:** Manage and review all past runs

**Features:**
- Chronological table of all runs
- Sortable columns:
  - Timestamp
  - Detector type
  - Best score
  - Number of epochs
- Result viewer:
  - Select any previous run
  - View quick metrics
  - Expand full JSON
  - Download data

**Benefits:**
- Compare different runs
- Track improvements over time
- Reproduce results
- Archive all work

## Data Flow

```
┌─────────────────┐
│ GUI Input       │
│ (Configuration) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Validate Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Config   │
│ Object          │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Initialize:         │
│ • Generator         │
│ • Detector          │
│ • Loop              │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ For each epoch:     │
│ 1. Evaluate texts   │
│ 2. Update metrics   │
│ 3. Render progress  │
│ 4. Evolve pop.      │
└────────┬────────────┘
         │
         ▼
┌─────────────────┐
│ Save Results    │
│ (JSON)          │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Display Summary     │
│ & Charts            │
└─────────────────────┘
```

## Session State Management

Streamlit uses session state to maintain data between interactions:

```python
st.session_state.run_test         # Flag to start test
st.session_state.quick_test       # Flag for quick run
st.session_state.debug_mode       # Flag for debug run
st.session_state.last_results     # Cached results dict
st.session_state.last_results_file # Path to results file
```

**Benefits:**
- Results persist across page refreshes
- Can view results after test completes
- No data loss during interaction
- Efficient re-rendering

## Performance Considerations

### GUI Rendering
- Streamlit reruns entire script on interaction
- Session state caches expensive computations
- Charts rendered with Plotly (client-side)

### Test Execution
- Runs in main thread (blocks GUI during test)
- Progress updates visible in real-time
- No background processing (intentional for safety)

### Results Storage
- JSON files in `logs/` directory
- One file per test run (timestamped)
- Minimal storage overhead (~1-5KB per run)

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Full support |
| Firefox | 88+ | ✅ Full support |
| Safari | 14+ | ✅ Full support |
| Edge | 90+ | ✅ Full support |
| Mobile Safari | 14+ | ✅ Responsive |
| Chrome Mobile | 90+ | ✅ Responsive |

## Security Considerations

### Input Validation
- All numeric inputs bounded by sliders
- Detector type restricted to dropdown
- File paths validated before use

### Data Privacy
- Results stored locally in `logs/`
- No cloud upload (unless configured)
- API keys never logged (except to respective services)
- Sandbox mode prevents unauthorized API calls

### Secrets Management
- API keys input via password fields
- Never echoed or logged
- Session state doesn't persist secrets
- Each fresh load requires re-entry

## Customization Options

### Custom Detector
Add to `gui.py` detector selection:
```python
elif detector_type == "custom":
    from src.detectors import CustomDetector
    detector = CustomDetector(...)
```

### Custom Charts
Replace Plotly charts with your visualization:
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
# ... custom visualization
st.pyplot(fig)
```

### Custom Analysis
Add new analysis tab:
```python
with st.tabs([..., "Custom Analysis"]):
    # Your analysis code
    st.write(custom_result)
```

## Deployment

### Local Development
```bash
streamlit run gui.py
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "gui.py"]
```

### Remote Access
- GUI accessible via network URL
- Default: `http://<your-ip>:8501`
- Proxy required for internet access (HTTPS)

## Future Enhancements

- [ ] Real-time batch testing queue
- [ ] Comparison view for multiple runs
- [ ] Custom metrics and scoring
- [ ] Model training from results
- [ ] Automated report generation
- [ ] Authentication for multi-user
- [ ] Database backend for results
- [ ] API integration (results → external systems)
- [ ] Mobile app (React Native)
- [ ] Result sharing (encrypted links)

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow charts | Many data points | Reduce epochs/population |
| Missing results | Not saved | Check `logs/` directory |
| Browser won't connect | Port 8501 in use | `pkill -f streamlit` |
| Memory leak | Long session | Restart Streamlit |
| Detector fails | Config mismatch | Verify detector settings |

## Version History

### v1.0.0 (Current)
- Initial GUI release
- 4 main tabs (Run, Results, Analysis, History)
- Real-time progress tracking
- Interactive Plotly charts
- Result export (JSON/CSV)
- Configuration dashboard

### Future
- v1.1: Batch testing
- v1.2: Advanced analytics
- v2.0: Multi-user support

---

**Last Updated:** August 2026
