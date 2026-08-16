"""
Streamlit GUI for Adversarial Content Test Framework
Interactive web interface for running and analyzing adversarial tests
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SandboxConfig
from src.detectors import create_detector
from src.generator import ConfigurableGenerator
from src.loop import AdversarialLoop
from src.utils import load_json

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Adversarial Test Framework",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# STYLING
# ============================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.5em;
        color: #ff6b6b;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .subtitle {
        font-size: 1.1em;
        color: #666;
        margin-bottom: 1em;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1em;
        border-radius: 0.5em;
        margin: 0.5em 0;
    }
    .success-box {
        background-color: #d1e7dd;
        padding: 1em;
        border-radius: 0.5em;
        margin: 0.5em 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1em;
        border-radius: 0.5em;
        margin: 0.5em 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">🔬 Adversarial Test Framework</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interactive GUI for red-team content classifier testing</div>', unsafe_allow_html=True)

with col2:
    st.info("🔒 Sandbox Mode: Enabled")

# ============================================
# SIDEBAR - CONFIGURATION
# ============================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Detector type
    detector_type = st.selectbox(
        "Detector Type",
        options=["mock", "hf", "openai", "local"],
        help="Select the detector backend to use",
        index=0
    )
    
    st.divider()
    
    # Loop parameters
    st.subheader("Algorithm Parameters")
    
    max_epochs = st.slider(
        "Max Epochs",
        min_value=1,
        max_value=100,
        value=20,
        help="Number of iterations to run"
    )
    
    population_size = st.slider(
        "Population Size",
        min_value=5,
        max_value=100,
        value=30,
        help="Number of texts per generation"
    )
    
    mutation_rate = st.slider(
        "Mutation Rate",
        min_value=0.01,
        max_value=1.0,
        value=0.25,
        step=0.05,
        help="Probability of mutation per text"
    )
    
    elite_ratio = st.slider(
        "Elite Ratio",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.1,
        help="Fraction of population kept as elite"
    )
    
    st.divider()
    
    # Text parameters
    st.subheader("Text Generation")
    
    max_text_length = st.slider(
        "Max Text Length",
        min_value=50,
        max_value=1000,
        value=500,
        help="Maximum length of generated texts"
    )
    
    use_categories = st.checkbox(
        "Use Categories",
        value=False,
        help="Use category-specific templates"
    )
    
    if use_categories:
        categories = st.multiselect(
            "Categories",
            options=["account", "security", "transactions", "general"],
            default=["account", "security", "transactions", "general"]
        )
    else:
        categories = ["general"]
    
    st.divider()
    
    # Detector-specific options
    if detector_type == "hf":
        st.subheader("🤗 Hugging Face Options")
        hf_url = st.text_input(
            "HF Local URL",
            value="http://localhost:8080",
            help="URL of local HF inference server"
        )
    elif detector_type == "openai":
        st.subheader("🤖 OpenAI Options")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key"
        )
    elif detector_type == "local":
        st.subheader("📦 Local Model Options")
        model_path = st.text_input(
            "Model Path",
            value="./models/classifier",
            help="Path to local model directory"
        )

# ============================================
# MAIN CONTENT
# ============================================

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Run Test", "Results", "Analysis", "History"])

# ============================================
# TAB 1: RUN TEST
# ============================================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Test Configuration Summary")
        
        summary_data = {
            "Detector Type": detector_type.upper(),
            "Max Epochs": max_epochs,
            "Population Size": population_size,
            "Mutation Rate": f"{mutation_rate:.2f}",
            "Elite Ratio": f"{elite_ratio:.2f}",
            "Max Text Length": max_text_length,
            "Categories": ", ".join(categories) if use_categories else "General",
        }
        
        summary_df = pd.DataFrame(list(summary_data.items()), columns=["Parameter", "Value"])
        st.table(summary_df)
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("▶️ Start Test", key="run_button", use_container_width=True):
            st.session_state.run_test = True
        
        if st.button("⚡ Quick Test (3 epochs)", key="quick_test", use_container_width=True):
            st.session_state.quick_test = True
        
        if st.button("🧪 Debug Mode", key="debug_test", use_container_width=True):
            st.session_state.debug_mode = True
    
    st.divider()
    
    # Run test if button was clicked
    if st.session_state.get("run_test") or st.session_state.get("quick_test") or st.session_state.get("debug_mode"):
        
        # Set epochs based on button clicked
        if st.session_state.get("quick_test"):
            epochs_to_run = 3
            test_name = "Quick Test"
        elif st.session_state.get("debug_mode"):
            epochs_to_run = 2
            test_name = "Debug Mode"
        else:
            epochs_to_run = max_epochs
            test_name = "Full Test"
        
        st.subheader(f"🚀 Running {test_name}...")
        
        # Progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        epoch_metrics = st.empty()
        history_plot = st.empty()
        
        try:
            # Create config object
            config = SandboxConfig()
            config.max_iterations = epochs_to_run
            config.population_size = population_size
            config.mutation_rate = mutation_rate
            config.elite_ratio = elite_ratio
            config.max_text_length = max_text_length
            config.detector_type = detector_type
            config.use_mock = (detector_type == "mock")
            config.use_categories = use_categories
            config.template_categories = categories
            
            # Override detector settings if provided
            if detector_type == "hf" and 'hf_url' in locals():
                config.hf_local_url = hf_url
            elif detector_type == "openai" and 'openai_key' in locals():
                config.openai_api_key = openai_key
            elif detector_type == "local" and 'model_path' in locals():
                config.local_model_path = model_path
            
            # Create components
            templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
            
            if use_categories:
                generator = ConfigurableGenerator(
                    template_file="",
                    categories=categories,
                    use_categories=True,
                    templates_dir=templates_dir
                )
            else:
                template_file = os.path.join(os.path.dirname(__file__), "..", config.template_file)
                generator = ConfigurableGenerator(
                    template_file=template_file,
                    use_categories=False
                )
            
            detector = create_detector(config)
            loop = AdversarialLoop(generator, detector, config)
            
            # Initialize population
            loop.initialize_population()
            status_text.info("✓ Population initialized")
            
            # Main loop with progress tracking
            history_data = []
            
            for epoch in range(epochs_to_run):
                # Update progress
                progress = (epoch) / epochs_to_run
                progress_bar.progress(progress, text=f"Running epoch {epoch + 1}/{epochs_to_run}")
                
                # Evaluate population
                scored = loop.evaluate_population()
                best_text, best_score = scored[0]
                avg_score = sum(s for _, s in scored) / len(scored)
                
                # Track history
                history_data.append({
                    "Epoch": epoch + 1,
                    "Best Score": best_score,
                    "Avg Score": avg_score,
                    "Best Text": best_text[:40] + "..." if len(best_text) > 40 else best_text
                })
                
                # Display metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Epoch", f"{epoch + 1}/{epochs_to_run}")
                with col_b:
                    st.metric("Best Score", f"{best_score:.4f}")
                with col_c:
                    st.metric("Avg Score", f"{avg_score:.4f}")
                with col_d:
                    st.metric("Population", len(scored))
                
                # Create history dataframe and plot
                if history_data:
                    history_df = pd.DataFrame(history_data)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=history_df["Epoch"],
                        y=history_df["Best Score"],
                        name="Best Score",
                        mode="lines+markers",
                        line=dict(color="red", width=2)
                    ))
                    fig.add_trace(go.Scatter(
                        x=history_df["Epoch"],
                        y=history_df["Avg Score"],
                        name="Avg Score",
                        mode="lines+markers",
                        line=dict(color="blue", width=2)
                    ))
                    fig.update_layout(
                        title="Score Progression",
                        xaxis_title="Epoch",
                        yaxis_title="Score",
                        hovermode="x unified",
                        height=400
                    )
                    history_plot.plotly_chart(fig, use_container_width=True)
                
                # Evolve for next generation
                if epoch < epochs_to_run - 1:
                    loop.population = loop.evolve_population(scored)
                
                st.write("---")
            
            # Final results
            progress_bar.progress(1.0, text="✓ Test complete!")
            
            st.success("✅ Test completed successfully!")
            
            # Save results
            best_overall_score = min(h["Best Score"] for h in history_data)
            best_overall_text = [h["Best Text"] for h in history_data if h["Best Score"] == best_overall_score][0]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"logs/adversarial_results_{timestamp}.json"
            
            results = {
                "timestamp": timestamp,
                "config": config.to_dict(),
                "best_score": best_overall_score,
                "best_text": best_overall_text,
                "history": history_data,
                "stats": dict(loop.stats)
            }
            
            os.makedirs("logs", exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            st.session_state.last_results = results
            st.session_state.last_results_file = results_file
            
        except Exception as e:
            st.error(f"❌ Test failed: {str(e)}")
            st.exception(e)
        
        finally:
            st.session_state.run_test = False
            st.session_state.quick_test = False
            st.session_state.debug_mode = False

# ============================================
# TAB 2: RESULTS
# ============================================
with tab2:
    st.subheader("Latest Test Results")
    
    if "last_results" in st.session_state:
        results = st.session_state.last_results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Best Score", f"{results['best_score']:.4f}", delta="Lower is better")
        
        with col2:
            config_info = results['config']
            st.metric("Epochs Run", config_info.get('max_iterations', 'N/A'))
        
        with col3:
            st.metric("Population", config_info.get('population_size', 'N/A'))
        
        with col4:
            st.metric("Total Evaluations", results['stats'].get('total_evaluations', 0))
        
        st.divider()
        
        # Best text found
        st.subheader("Best Evasive Text Found")
        st.info(f"📝 {results['best_text']}")
        
        st.divider()
        
        # History table
        st.subheader("Epoch-by-Epoch Results")
        history_df = pd.DataFrame(results['history'])
        st.dataframe(history_df, use_container_width=True)
        
        st.divider()
        
        # Score progression chart
        st.subheader("Score Progression Chart")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=history_df["Epoch"],
            y=history_df["Best Score"],
            name="Best Score",
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color="red", width=3)
        ))
        fig.add_trace(go.Scatter(
            x=history_df["Epoch"],
            y=history_df["Avg Score"],
            name="Avg Score",
            mode="lines+markers",
            line=dict(color="blue", width=2)
        ))
        fig.update_layout(
            title="Score Evolution Across Epochs",
            xaxis_title="Epoch",
            yaxis_title="Score (Lower = Better)",
            hovermode="x unified",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Download results
        st.subheader("Export Results")
        
        json_str = json.dumps(results, indent=2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"adversarial_results_{results['timestamp']}.json",
                mime="application/json"
            )
        
        with col2:
            csv_data = history_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"adversarial_results_{results['timestamp']}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("💡 Run a test first to see results here!")

# ============================================
# TAB 3: ANALYSIS
# ============================================
with tab3:
    st.subheader("Results Analysis")
    
    if "last_results" in st.session_state:
        results = st.session_state.last_results
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Score Statistics")
            history_df = pd.DataFrame(results['history'])
            
            stats_dict = {
                "Best Score": f"{history_df['Best Score'].min():.4f}",
                "Worst Score": f"{history_df['Best Score'].max():.4f}",
                "Avg Score": f"{history_df['Avg Score'].mean():.4f}",
                "Score Improvement": f"{(history_df['Best Score'].iloc[0] - history_df['Best Score'].iloc[-1]):.4f}",
                "Total Epochs": len(history_df),
            }
            
            for key, value in stats_dict.items():
                st.metric(key, value)
        
        with col2:
            st.subheader("Configuration Summary")
            config = results['config']
            
            config_info = {
                "Detector": config.get('detector_type', 'Unknown').upper(),
                "Population Size": config.get('population_size', 'N/A'),
                "Mutation Rate": config.get('mutation_rate', 'N/A'),
                "Elite Ratio": config.get('elite_ratio', 'N/A'),
                "Template": config.get('template_file', 'N/A'),
            }
            
            for key, value in config_info.items():
                st.write(f"**{key}:** {value}")
        
        st.divider()
        
        # Score distribution
        st.subheader("Score Distribution by Epoch")
        
        all_scores = []
        all_epochs = []
        for epoch_data in results['history']:
            epoch = epoch_data['epoch']
            scores = epoch_data.get('all_scores', [])
            for score in scores:
                all_scores.append(score)
                all_epochs.append(epoch)
        
        if all_scores:
            distribution_df = pd.DataFrame({
                "Epoch": all_epochs,
                "Score": all_scores
            })
            
            fig = px.box(
                distribution_df,
                x="Epoch",
                y="Score",
                title="Score Distribution Across Epochs",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Top texts
        st.subheader("Best Texts Per Epoch")
        
        top_texts_data = []
        for epoch_data in results['history']:
            top_texts = epoch_data.get('all_texts', [])[:3]
            for i, text in enumerate(top_texts, 1):
                top_texts_data.append({
                    "Epoch": epoch_data['epoch'],
                    "Rank": i,
                    "Text": text[:60] + "..." if len(text) > 60 else text
                })
        
        if top_texts_data:
            top_texts_df = pd.DataFrame(top_texts_data)
            st.dataframe(top_texts_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("💡 Run a test first to see analysis here!")

# ============================================
# TAB 4: HISTORY
# ============================================
with tab4:
    st.subheader("Previous Test Runs")
    
    # Scan logs directory
    log_dir = Path("logs")
    if log_dir.exists():
        result_files = sorted(log_dir.glob("adversarial_results_*.json"), reverse=True)
        
        if result_files:
            # Create a table of previous runs
            runs_data = []
            for file in result_files[:20]:  # Show last 20 runs
                try:
                    data = load_json(str(file))
                    runs_data.append({
                        "Timestamp": data.get('timestamp', 'Unknown'),
                        "Detector": data.get('config', {}).get('detector_type', 'Unknown').upper(),
                        "Best Score": f"{data.get('best_score', 0):.4f}",
                        "Epochs": data.get('config', {}).get('max_iterations', 0),
                        "File": file.name,
                    })
                except:
                    pass
            
            if runs_data:
                runs_df = pd.DataFrame(runs_data)
                st.dataframe(runs_df, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Load and view a specific result
                st.subheader("View Results")
                selected_file = st.selectbox(
                    "Select a result file to view",
                    options=[run["File"] for run in runs_data],
                    format_func=lambda x: f"{x.split('_')[3]} - {x.split('_')[4].split('.')[0]}"
                )
                
                if selected_file:
                    result_path = log_dir / selected_file
                    result_data = load_json(str(result_path))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Best Score", f"{result_data['best_score']:.4f}")
                    with col2:
                        st.metric("Epochs", result_data['config']['max_iterations'])
                    
                    st.info(f"📝 {result_data['best_text']}")
                    
                    # Show JSON
                    with st.expander("View Full JSON"):
                        st.json(result_data)
            else:
                st.info("📊 No results found yet")
        else:
            st.info("📊 No results found yet")
    else:
        st.info("📊 Create a 'logs' directory or run a test to see history")

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8em;">
    <p>🔬 Adversarial Content Test Framework v1.0 | For internal red-team testing only</p>
    <p>📚 <a href="https://github.com">GitHub</a> • 📖 <a href="README.md">Documentation</a></p>
</div>
""", unsafe_allow_html=True)
