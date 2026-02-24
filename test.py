import random
import time
import tracemalloc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from main import backtracking_csp, min_conflicts, conflicts, print_board

def validate_input(n):
    if not (10 <= n <= 1000):
        raise ValueError("n must satisfy 10 <= n <= 1000")

def generate_random_board(n):
    board = list(range(n))
    random.shuffle(board)
    return board

def run_algorithm(name, func, n):
    tracemalloc.start()
    t0 = time.perf_counter()

    result = func(n)

    t1 = time.perf_counter()
    peak_mem = tracemalloc.get_traced_memory()[1] / 1024
    tracemalloc.stop()

    time_ms = (t1 - t0) * 1000

    solution, steps = result  # works for both algorithms

    if solution:
        total_conf = sum(conflicts(solution, r, solution[r]) for r in range(n)) // 2
        solved = "Yes"
    else:
        total_conf = "N/A"
        solved = "No"

    return {
        "Algorithm": name,
        "Conflicts": total_conf,
        "Time": time_ms,
        "Memory": peak_mem,
        "Solved": solved,
        "Steps": steps
    }

if __name__ == "__main__":
    # --- Ask user for 4 different n values ---
    n_values = []
    print("Enter 4 different n values (10-1000):")
    while len(n_values) < 4:
        try:
            n = int(input(f"Enter n[{len(n_values)+1}]: "))
            validate_input(n)
            n_values.append(n)
        except ValueError as e:
            print(f"Invalid input: {e}")

    all_results = []

    # --- Run algorithms for each n ---
    for run_id, n in enumerate(n_values, start=1):
        print(f"\n--- Run {run_id}: n={n} ---")

        # Generate random board
        initial = generate_random_board(n)
        print("Initial Board (first 20 positions):", initial[:20], "..." if n>20 else "")

        # CSP Backtracking
        result_csp = run_algorithm("CSP Backtracking", backtracking_csp, n)
        result_csp["Run"] = run_id
        result_csp["n"] = n
        all_results.append(result_csp)

        # Min-Conflicts
        result_mc = run_algorithm("Min-Conflicts", min_conflicts, n)
        result_mc["Run"] = run_id
        result_mc["n"] = n
        all_results.append(result_mc)

    # --- Create DataFrame ---
    df = pd.DataFrame(all_results)

    # --- Print table ---
    header = f"{'Run':<5} | {'n':<5} | {'Algorithm':<18} | {'Conflicts':<10} | {'Time(ms)':<10} | {'Mem(KB)':<10} | {'Solved':<6} | {'Steps'}"
    print("\n" + header)
    print("-" * len(header))
    for _, r in df.iterrows():
        print(f"{r['Run']:<5} | {r['n']:<5} | {r['Algorithm']:<18} | "
              f"{r['Conflicts']:<10} | {r['Time']:<10.2f} | "
              f"{r['Memory']:<10.2f} | {r['Solved']:<6} | {r['Steps']}")

    # --- Separate bar plots for Time, Memory, Steps ---
    metrics = ["Time", "Memory", "Steps"]
    metric_labels = {"Time": "Time (ms)", "Memory": "Memory (KB)", "Steps": "Steps"}
    algorithms = df["Algorithm"].unique()
    NUM_RUNS = len(n_values)
    width = 0.35  # width of bars

    for metric in metrics:
        plt.figure(figsize=(10,5))
        x = np.arange(NUM_RUNS)  # positions for runs

        for i, algo in enumerate(algorithms):
            values = df[df["Algorithm"] == algo][metric].values
            bars = plt.bar(x + i*width, values, width=width, label=algo)

            # Add numbers on top of bars
            for bar in bars:
                height = bar.get_height()
                if metric == "Steps":
                    plt.text(bar.get_x() + bar.get_width()/2, height, f'{int(height)}', ha='center', va='bottom', fontsize=8)
                else:
                    plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=8)

        plt.xticks(x + width/2, [f"n={n}" for n in n_values])
        plt.ylabel(metric_labels[metric])
        plt.title(f"{metric_labels[metric]} Comparison for Different n Values")
        plt.legend()
        plt.tight_layout()
        plt.show()