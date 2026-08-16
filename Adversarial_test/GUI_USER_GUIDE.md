# Adversarial Test Framework - GUI User Guide

## 🎯 Overview

The Adversarial Test Framework GUI is a modern web-based interface built with Streamlit that makes it easy to configure, run, and analyze adversarial testing campaigns without using the command line.

**Access:** http://localhost:8501

## 🚀 Quick Start

### Option 1: Using the Startup Script
```bash
./start_gui.sh
```

### Option 2: Manual Launch
```bash
STREAMLIT_SERVER_HEADLESS=true streamlit run gui.py --logger.level=error
```

### Option 3: Using Python
```bash
python3 -m streamlit run gui.py
```

The GUI will be available at `http://localhost:8501` (and on your network IP for remote access).

## 📋 Interface Guide

### Left Sidebar - Configuration Panel

The sidebar contains all configuration options for your test:

#### **Detector Type** (Dropdown)
- **Mock:** Deterministic scoring (no external dependencies) - Good for testing
- **HF:** Hugging Face model endpoint (local or cloud)
- **OpenAI:** OpenAI Moderation API (requires API key)
- **Local:** Local Hugging Face model (requires downloaded model)

#### **Algorithm Parameters** (Sliders)

**Max Epochs:** 1-100 (default: 20)
- Number of iterations to run
- More epochs = longer test but potentially better results
- Start with 10-20 for initial testing

**Population Size:** 5-100 (default: 30)
- Number of texts per generation
- Larger population = more diversity but slower execution
- Good range: 20-50

**Mutation Rate:** 0.01-1.0 (default: 0.25)
- Probability of mutation applied to each text
- Higher = more aggressive mutations
- Start with 0.2-0.3

**Elite Ratio:** 0.1-0.9 (default: 0.5)
- Fraction of population kept as "elite"
- Higher = more conservative evolution
- Start with 0.3-0.5

#### **Text Generation** (Controls)

**Max Text Length:** 50-1000 (default: 500)
- Maximum character length for generated texts
- Shorter = faster, Longer = more complexity

**Use Categories:** Toggle
- If enabled, generates texts from specific categories
- Categories: account, security, transactions, general

#### **Detector-Specific Options**

**For Hugging Face:**
- HF Local URL: URL of your HF inference server (default: http://localhost:8080)

**For OpenAI:**
- OpenAI API Key: Your API key (masked, sent only to OpenAI)

**For Local Model:**
- Model Path: Path to your Hugging Face model directory

### Main Content - Tabs

#### **Tab 1: Run Test**

**Configuration Summary Table**
- Shows all current settings
- Review before running

**Quick Action Buttons**

1. **▶️ Start Test** - Run with full configuration (can take minutes)
2. **⚡ Quick Test** - Run 3 epochs (useful for validation)
3. **🧪 Debug Mode** - Run 2 epochs with minimal output

**Real-Time Progress During Test**
- Progress bar showing completion percentage
- Status messages
- Per-epoch metrics (best score, average score, population size)
- Interactive score progression chart
- Updates every epoch

#### **Tab 2: Results**

After running a test, view:

**Summary Metrics**
- Best Score achieved (lower is better)
- Number of epochs run
- Population size used
- Total evaluations performed

**Best Text Found**
- The most evasive text discovered

**Results Table**
- Epoch-by-epoch breakdown
- Best score per epoch
- Average score per epoch
- Best text found in each epoch

**Score Progression Chart**
- Interactive line chart
- Shows best score and average score trends
- Hover for exact values

**Export Buttons**
- Download results as JSON (full data)
- Download results as CSV (for spreadsheet analysis)

#### **Tab 3: Analysis**

**Score Statistics**
- Best, worst, average scores
- Score improvement (first epoch vs last)
- Total epochs run

**Configuration Summary**
- Detector type used
- Population size, mutation rate, elite ratio
- Template configuration

**Score Distribution Chart**
- Box plot showing score spread by epoch
- Visualize population variance

**Top Texts Table**
- Best 3 texts from each epoch
- Track how texts evolve

#### **Tab 4: History**

**Previous Runs Table**
- Shows all past test results
- Timestamp, detector, best score, epochs
- Last 20 runs

**View Results**
- Select any previous result
- View quick metrics
- Expand full JSON details
- Download data

## 💡 Usage Scenarios

### Scenario 1: Quick Validation
1. Set **Max Epochs** = 5
2. Set **Population Size** = 10
3. Select **Mock** detector
4. Click **⚡ Quick Test**
- Time: ~30 seconds
- Purpose: Verify configuration

### Scenario 2: Standard Testing
1. Set **Max Epochs** = 20
2. Set **Population Size** = 30
3. Select **HF** detector
4. Configure HF URL if using local model
5. Click **▶️ Start Test**
- Time: 5-10 minutes
- Purpose: Find evasive texts

### Scenario 3: Intensive Analysis
1. Set **Max Epochs** = 50
2. Set **Population Size** = 50
3. Lower **Mutation Rate** to 0.15
4. Select your detector
5. Click **▶️ Start Test**
- Time: 20-30 minutes
- Purpose: Deep evolutionary search

### Scenario 4: Category-Based Testing
1. Toggle **Use Categories** = ON
2. Select specific categories (e.g., "account", "security")
3. Configure other parameters
4. Click **▶️ Start Test**
- Purpose: Test specific types of content

## 📊 Understanding Results

### Score Interpretation
- **Score Range:** 0.0 (safe) to 1.0 (malicious)
- **Goal:** Find texts with LOW scores (evade detection)
- **Lower is better** for adversarial testing

### Graphs Interpretation

**Score Progression Chart**
- Red line (Best Score): Should trend downward ⬇️
- Blue line (Avg Score): Follows similar pattern
- Steady downward trend = good evolution

**Score Distribution Chart**
- Wide box = diverse population ✓
- Narrow box = converging population
- Downward shift = population improving

### Quality Indicators

✅ **Good Test Results:**
- Best score < 0.3
- Steady score improvement
- Diverse population (wide distribution)
- Improvement visible across epochs

❌ **Poor Test Results:**
- Scores stuck above 0.7
- No improvement across epochs
- Very narrow score distribution
- Same texts appearing repeatedly

## 🔧 Tips & Tricks

### Performance Tips
1. **Start with smaller populations** (20-30) for initial testing
2. **Use Quick Test** (3 epochs) to verify detector is working
3. **Increase population size gradually** as you get comfortable
4. **Mock detector is fastest** for parameter tuning

### Quality Tips
1. **Mutation rate 0.2-0.3** works best for most cases
2. **Elite ratio 0.3-0.5** balances exploration and exploitation
3. **30-50 epoch runs** usually show good convergence
4. **50+ population size** improves solution quality

### Detector Tips
- **Mock:** No setup needed, good for testing
- **HF:** Requires running inference server locally
- **OpenAI:** Requires API key, uses up credits
- **Local:** Requires downloading ~500MB model first

### Result Analysis Tips
1. Compare multiple runs (Tab 4: History)
2. Export to CSV for further analysis in Excel/Sheets
3. Look for patterns in best texts (Tab 3: Top Texts)
4. Check score distribution to assess population health

## ⚙️ Configuration Files

### Environment Variables
If running from command line, use `.env` file:
```bash
MAX_EPOCHS=50
POPULATION_SIZE=30
MUTATION_RATE=0.25
DETECTOR_TYPE=mock
USE_CATEGORIES=False
```

GUI overrides these settings, so configure in the sidebar instead.

## 🐛 Troubleshooting

### "Detector not responding"
- If using HF: Ensure Hugging Face server is running on configured URL
- Check `HF_LOCAL_URL` setting in sidebar
- Try Quick Test with Mock detector first

### "API Key not working"
- If using OpenAI: Verify API key is correct and has credits
- Check key hasn't been revoked

### "Model not found"
- If using Local: Verify model path is correct
- Model should be a Hugging Face model directory
- Ensure sufficient disk space for model (~500MB)

### GUI won't start
- Ensure Python 3.8+ is installed
- Check dependencies: `pip install streamlit plotly pandas`
- Try: `STREAMLIT_SERVER_HEADLESS=true streamlit run gui.py`

### Slow performance
- Reduce population size
- Use Mock detector instead
- Reduce number of epochs
- Check system RAM usage

## 📈 Advanced Features

### Batch Testing
1. Run multiple tests with different configurations
2. Use Tab 4 (History) to compare results
3. Export all results as CSV for comparison

### Custom Analysis
1. Download JSON results
2. Process with pandas/Python for custom analysis
3. Create your own visualizations

### Integration
- Save results for integration with reporting tools
- Export CSV for spreadsheet analysis
- JSON format for programmatic access

## 🔒 Security Notes

- **Sandbox Mode:** Always ON by default (restricts API access)
- **Local Processing:** All data stays on your machine
- **API Keys:** Never logged, only sent to respective services
- **Results:** Saved locally in `logs/` directory

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review README.md for architecture details
3. Check FIXES_APPLIED.md for known issues
4. Review configuration in sidebar

## ✨ Features

✅ Real-time progress monitoring
✅ Interactive score charts (Plotly)
✅ Multiple detector backends
✅ History tracking
✅ Export to JSON/CSV
✅ No command line needed
✅ Full configuration GUI
✅ Result analysis tools
✅ Mobile-responsive design
✅ Sandbox mode by default

---

**Version:** 1.0.0  
**Framework:** Streamlit  
**Last Updated:** August 2026
