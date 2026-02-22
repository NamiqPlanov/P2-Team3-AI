
# CSP: N-Queens

**Contributors:** Namig Planov and Laman Khudadatzada  

---

## Introduction

This project implements a **Constraint Satisfaction Problem (CSP)** solution for the N-Queens problem on an `n x n` chessboard. 

The goal is to place `n` queens on the board such that no two queens attack each other.

The program reads an initial board from a file or generates a random one if the file is not found. It uses iterative CSP search algorithms with heuristics and constraint propagation.

---

## Installation and Usage

1. Python 3.8+
2. Clone the repository:

```bash
git clone https://github.com/NamiqPlanov/P2-Team3-AI.git
cd P2-Team3-AI
```
3. Run the program:

```bash
python main.py
```
4. If no input file is found, the program will ask for `n` and generate a random board.

5. The program prints the initial board, solves the problem using either **CSP Backtracking** for `n <= 30` or **Min-Conflicts** for larger `n`.

---
## Algorithms

### Min-Conflicts (Iterative Search)

- Randomly initializes queens on the board
- Iteratively selects conflicted queens
- and moves them to minimize conflicts,
- Effective for large boards like `n > 30`.

---

## Example Output (will be added)

```
```
---

