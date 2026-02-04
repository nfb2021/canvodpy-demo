# canVODpy API Redesign: Marimo Notebooks

Interactive notebooks demonstrating the redesigned canVODpy API (v0.2.0).

## 📚 Notebooks

### 1. Factory Basics (`01_factory_basics.py`)
Learn the factory pattern for creating components.

**Topics:**
- List available components
- Create grids, readers, VOD calculators
- Pass parameters to components
- Interactive grid visualization

**Run:** `marimo edit 01_factory_basics.py`

---

### 2. VODWorkflow Usage (`02_workflow_usage.py`)
Use the stateful VODWorkflow class for complete pipelines.

**Topics:**
- Initialize workflow with site config
- Process RINEX data
- Calculate VOD
- Structured logging with context

**Run:** `marimo edit 02_workflow_usage.py`

---

### 3. Functional API (`03_functional_api.py`)
Pure functions for composable, stateless processing.

**Topics:**
- Data-returning functions for notebooks
- Path-returning functions for Airflow
- Complete Airflow DAG example
- Functional composition patterns

**Run:** `marimo edit 03_functional_api.py`

---

### 4. Custom Components (`04_custom_components.py`)
Extend canVODpy with your own implementations.

**Topics:**
- Implement custom grid builder
- Register with factory
- Use in workflows
- Best practices for contributions
- Publishing extensions

**Run:** `marimo edit 04_custom_components.py`

---

## 🚀 Quick Start

```bash
# Install marimo if not already installed
pip install marimo

# Run a notebook
cd /Users/work/Developer/GNSS/canvodpy/demo
marimo edit 01_factory_basics.py
```

## 📖 Documentation

Full API documentation: [`docs/guides/API_REDESIGN.md`](../docs/guides/API_REDESIGN.md)

## 🎯 Learning Path

1. **Start here:** `01_factory_basics.py` - Core concepts
2. **Then:** `02_workflow_usage.py` - Stateful workflows
3. **Next:** `03_functional_api.py` - Pure functions
4. **Finally:** `04_custom_components.py` - Extend the API

## 🏗️ Architecture

### Three-Layer Design

```
┌─────────────────────────────────────┐
│  Layer 3: Functional API            │  Pure functions
│  read_rinex(), create_grid(), ...   │  (+ Airflow versions)
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Layer 2: VODWorkflow               │  Stateful orchestration
│  process_date(), calculate_vod()    │  + structured logging
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Layer 1: Factories                 │  Component creation
│  ReaderFactory, GridFactory, ...    │  + ABC enforcement
└─────────────────────────────────────┘
```

## ✨ Key Features

- **🏭 Factory Pattern** - Clean component creation with validation
- **📊 Structured Logging** - JSON logs for LLM-assisted debugging
- **🔧 Type Safe** - Modern Python 3.12+ type hints
- **🔌 Extensible** - Easy to add custom components
- **⚡ Airflow Ready** - Path-returning functions for DAGs
- **📦 ABC Enforced** - All components validated at registration

## 🤝 Contributing

Found an issue? Have an idea? 

1. Check existing issues
2. Create a new issue with details
3. Or submit a PR!

## 📜 License

BSD-3-Clause (same as canVODpy)

---

**Questions?** See the main [API_REDESIGN.md](../docs/guides/API_REDESIGN.md) guide.
