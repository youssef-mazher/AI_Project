# Project 23 — Faculty AI Timetable Scheduler

This repository is a **starter structure only**. The Python files contain
section comments and TODO markers; the team will implement the actual code.

## Project files

- `app.py`: Streamlit entry point and user interface.
- `models.py`: Shared configuration constants and data classes.
- `data_loader.py`: Converts GUI input into model objects and generates time slots.
- `algorithms.py`: Fitness Engine, Pure GA, Memetic Local Search, and optimization pipeline.
- `evaluation.py`: Metrics and GA-vs-MA comparison formatting.
- `requirements.txt`: Python dependencies.

## Suggested implementation order

1. `models.py`
2. `data_loader.py`
3. Fitness Engine section in `algorithms.py`
4. Pure GA section in `algorithms.py`
5. Memetic Local Search section in `algorithms.py`
6. Optimization Pipeline section in `algorithms.py`
7. `evaluation.py`
8. `app.py`

## Install and run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Module connection overview

`app.py` -> `data_loader.py` -> `models.py`

`app.py` -> `algorithms.py` -> `models.py`

`app.py` -> `evaluation.py`

The arrows show the intended dependency/flow. The team should add the actual
Python imports when implementing each file.
