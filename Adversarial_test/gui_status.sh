#!/bin/bash
# Quick status and access guide for Adversarial Test Framework GUI

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🔬 Adversarial Test Framework - GUI Access Guide              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Streamlit is running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ GUI Status: RUNNING"
    echo ""
    echo "📍 Access URLs:"
    echo "   • Local:   http://localhost:8501"
    echo "   • Network: http://$(hostname -I | awk '{print $1}'):8501"
    echo ""
    echo "💡 Quick Start Tips:"
    echo "   1. Open http://localhost:8501 in your browser"
    echo "   2. Configure parameters in the left sidebar"
    echo "   3. Click '▶️ Start Test' to run"
    echo "   4. View results in the 'Results' tab"
    echo ""
else
    echo "❌ GUI Status: NOT RUNNING"
    echo ""
    echo "🚀 To start the GUI, run:"
    echo "   ./start_gui.sh"
    echo ""
    echo "   OR manually:"
    echo "   streamlit run gui.py"
    echo ""
fi

echo "📚 Documentation:"
echo "   • GUI Guide:    GUI_USER_GUIDE.md"
echo "   • README:       README.md"
echo "   • Code Analysis: CODE_ANALYSIS.md"
echo "   • Fixes Applied: FIXES_APPLIED.md"
echo ""

echo "🛑 To stop the GUI:"
echo "   pkill -f 'streamlit run gui.py'"
echo ""
