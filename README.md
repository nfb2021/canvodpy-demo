# 🛰️ canvodpy Demonstrations

This directory contains interactive demonstrations of the canvodpy framework for GNSS Vegetation Optical Depth analysis.

## 📚 Demo Files

### 🎯 **gnss_vod_complete_demo.py** ⭐ START HERE

**The definitive demonstration** of canvodpy - polished, comprehensive, and production-ready.

**What it covers:**
- ✨ Three-level API (beginner → intermediate → advanced)
- 🚀 Complete processing workflow with real data
- 📊 Performance analysis and visualization
- 🎓 Educational progression with explanations
- 💡 Best practices and production patterns
- 📈 Before/after API comparisons
- 🔗 Next steps (VOD calculation, Airflow integration)

**Who it's for:**
- **New users** learning canvodpy
- **Researchers** wanting to understand the workflow
- **Presentations** and demonstrations
- **Documentation** examples

**Run it:**
```bash
cd ~/Developer/GNSS/canvodpy/demo
uv run marimo edit gnss_vod_complete_demo.py
```

---

### ⏱️ **timing_diagnostics.py**

Focuses on **performance profiling** and timing analysis of the processing pipeline.

**What it covers:**
- Detailed timing breakdowns per receiver
- Processing throughput metrics
- Resource usage analysis
- Parallel processing diagnostics

**Who it's for:**
- Performance optimization
- Debugging slow processing
- Comparing different configurations
- Benchmarking

**Run it:**
```bash
uv run marimo edit timing_diagnostics.py
```

---

### 🔬 **pipeline_demo.py**

**Low-level demonstration** using direct access to building blocks (Level 3 API).

**What it covers:**
- Direct use of canvod-* packages
- Detailed RINEX reading
- Auxiliary data handling
- Custom processing workflows

**Who it's for:**
- **Advanced users** needing full control
- **Framework developers**
- **Custom algorithm implementation**
- **Research prototyping**

**Run it:**
```bash
uv run marimo edit pipeline_demo.py
```

---

## 🎓 Learning Path

### 1. **Beginner**: Start with Complete Demo
```bash
uv run marimo edit gnss_vod_complete_demo.py
```
- Learn the high-level API
- Understand the workflow
- See real results

### 2. **Intermediate**: Explore Timing
```bash
uv run marimo edit timing_diagnostics.py
```
- Understand performance
- Optimize configurations
- Profile your setup

### 3. **Advanced**: Study Pipeline Demo
```bash
uv run marimo edit pipeline_demo.py
```
- Access low-level APIs
- Build custom workflows
- Extend the framework

---

## 📦 Data Requirements

All demos use data from the **Rosalia research site**:

- **Location**: Beech forest, Rosalia, Austria
- **Receivers**: 4 GNSS (2 canopy, 2 reference)
- **Demo Date**: 2025-01-01 (DOY 001)
- **Files**: ~96 RINEX files per receiver (15-min intervals)

**Data location**: `demo/data/01_Rosalia/`

---

## 🚀 Quick Start

### First Time Setup

```bash
# Navigate to demo directory
cd ~/Developer/GNSS/canvodpy/demo

# Install dependencies (if needed)
cd .. && uv sync && cd demo

# Run the complete demo
uv run marimo edit gnss_vod_complete_demo.py
```

### What to Expect

1. **Browser Opens**: Marimo launches in your browser
2. **Cells Execute**: Run cells sequentially (Shift+Enter)
3. **Interactive**: Modify code and see instant results
4. **Visualizations**: Charts and plots render inline

---

## 📊 Demo Comparison

| Feature           | Complete Demo | Timing       | Pipeline        |
| ----------------- | ------------- | ------------ | --------------- |
| **API Level**     | 2 (OOP)       | 2 (OOP)      | 3 (Direct)      |
| **Complexity**    | ⭐⭐ Easy       | ⭐⭐⭐ Medium   | ⭐⭐⭐⭐ Advanced   |
| **Focus**         | Learning      | Performance  | Internals       |
| **Best For**      | New users     | Optimization | Developers      |
| **Completeness**  | Full workflow | Diagnostics  | Building blocks |
| **Documentation** | Extensive     | Technical    | Minimal         |

---

## 🎯 Goals by Demo

### Complete Demo Goals
1. ✅ Understand GNSS VOD concept
2. ✅ Learn canvodpy API (3 levels)
3. ✅ Process real data end-to-end
4. ✅ See production-quality code
5. ✅ Know next steps (VOD, Airflow)

### Timing Demo Goals
1. ✅ Profile processing performance
2. ✅ Identify bottlenecks
3. ✅ Optimize worker counts
4. ✅ Compare receiver throughput
5. ✅ Benchmark your system

### Pipeline Demo Goals
1. ✅ Access low-level APIs directly
2. ✅ Understand data flow internals
3. ✅ Build custom processors
4. ✅ Prototype new algorithms
5. ✅ Extend framework capabilities

---

## 💡 Tips for Best Experience

### Running Demos

1. **Use marimo editor** (not Python directly)
   ```bash
   uv run marimo edit filename.py
   ```

2. **Run cells in order** (top to bottom first time)

3. **Wait for each cell** (some take time, watch terminal)

4. **Experiment freely** (modify code, marimo auto-updates)

### Performance Tips

1. **First run slower** (downloads auxiliary data)
2. **Subsequent runs faster** (uses cached data)
3. **Adjust worker count** (N_WORKERS) to match your CPU
4. **Monitor RAM usage** (multiple datasets in memory)

### Troubleshooting

**Demo won't start:**
```bash
# Make sure you're in the right directory
cd ~/Developer/GNSS/canvodpy/demo

# Install marimo if needed
uv add marimo
```

**Import errors:**
```bash
# Sync dependencies
cd ~/Developer/GNSS/canvodpy
uv sync
```

**Data not found:**
```bash
# Check demo data exists
ls -la data/01_Rosalia/
```

**Network issues:**
- First run needs internet (downloads SP3/CLK files)
- Cached data stored in `.data/` for offline use

---

## 📚 Additional Resources

### Documentation
- **API Reference**: `../API_QUICK_REFERENCE.md`
- **Migration Guide**: `../CANVODPY_MIGRATION_GUIDE.md`
- **Quick Start**: `../QUICK_START.md`

### Examples
- **Airflow Integration**: `../canvodpy/src/canvodpy/workflows/AIRFLOW_COMPATIBILITY.py`
- **API Design**: `../API_DESIGN_GUIDE.md`

### Data
- **Demo Data Repo**: https://github.com/yourusername/canvodpy-demo
- **Test Data**: `../canvodpy-test-data/`

---

## 🔧 Advanced Usage

### Running Headless (No Browser)

```python
# In Python script or Jupyter
import marimo
app = marimo.App()
# ... app code ...
app.run()  # Run without marimo editor
```

### Exporting Results

```python
# Export to HTML
import marimo
app = marimo.App.from_file("gnss_vod_complete_demo.py")
app.export("demo_output.html")
```

### Custom Configurations

Edit configuration cells:
```python
# Change site
SITE_NAME = "YourSite"

# Change date
TARGET_DATE = "2025002"

# Adjust workers
N_WORKERS = 8  # Match your CPU cores
```

---

## 🎬 Demo Workflow

**Typical session:**

1. **Start demo** → Browser opens
2. **Read intro** → Understand GNSS VOD
3. **Run setup** → Import packages
4. **Initialize site** → Load configuration
5. **Create pipeline** → Set up processing
6. **Process data** → Watch progress (~2 min)
7. **Analyze results** → View metrics
8. **Visualize** → Interactive plots
9. **Next steps** → Learn VOD calculation
10. **Experiment** → Modify and re-run

**Duration**: 15-30 minutes (including reading)

---

## 🤝 Contributing

Found an issue or improvement?

1. **Issues**: Report problems or suggestions
2. **Pull Requests**: Submit improvements
3. **Discussions**: Ask questions or share ideas

---

## 📧 Contact

**Author**: Nicolas François Bader
**Institution**: TU Wien - CLIMERS
**Email**: your.email@tuwien.ac.at
**GitHub**: https://github.com/yourusername/canvodpy

---

## ⭐ Quick Command Reference

```bash
# Run the main demo
uv run marimo edit gnss_vod_complete_demo.py

# Run timing analysis
uv run marimo edit timing_diagnostics.py

# Run low-level demo
uv run marimo edit pipeline_demo.py

# View this README
cat README.md

# Check demo data
ls -lh data/01_Rosalia/
```

---

**Happy analyzing! 🛰️**
