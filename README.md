# BFS & DFS Traversal Visualiser

BSD3513 Introduction to Artificial Intelligence – Lab Report 1
**Student:** Kavinyaa Sree A/P S.Ganesh (SD24049) · Section 01G

A Streamlit web app that runs **Breadth-First Search (BFS)** and **Depth-First Search (DFS)**
on the directed graph from Question 2, using alphabetical tie-breaking. It shows the
expansion order, BFS levels / DFS depths, a step-by-step queue/stack trace, and the
time/space complexity of each algorithm.

**Live app:** <paste your Streamlit Community Cloud URL here>

## Graph (directed edges)
A→B, A→D, B→C, B→E, B→G, C→A, D→C, E→H, G→F, H→F, H→G

## Expected results (start = A)
| Algorithm | Order | Levels / depths |
|---|---|---|
| BFS | A, B, D, C, E, G, H, F | L0: A · L1: B, D · L2: C, E, G · L3: H, F |
| DFS | A, B, C, E, H, F, G, D | A0, B1, C2, E2, H3, F4, G4, D1 |

## Run locally
```bash
pip install -r requirements.txt
streamlit run SD24049_Lab1.py
```

## Files
- `SD24049_Lab1.py` – algorithms + Streamlit UI
- `requirements.txt` – dependencies

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub (public).
2. Go to share.streamlit.io → New app → select the repo, branch `main`, main file `SD24049_Lab1.py`.
3. Copy the public URL into this README and into your PDF report.
