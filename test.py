import random
import time
import tracemalloc
from main import backtracking_csp, min_conflicts, conflicts, print_board, read_board


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

    # --- ALWAYS UNPACK solution and steps ---
    solution, steps = result  # works for BOTH algorithms now

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
    try:
        initial = read_board("p2n-queen.txt")
        n = len(initial)
    except FileNotFoundError:
        print("n-queen.txt not found → using random input")
        n = int(input("Enter n (10-1000): "))
        initial = generate_random_board(n)

    validate_input(n)

    print("\nInitial Board:")
    print_board(initial)

    print("\nRunning Algorithms...\n")

    results = []

    # CSP Backtracking
    results.append(run_algorithm("CSP Backtracking", backtracking_csp, n))

    # Iterative Search (Min-Conflicts)
    results.append(run_algorithm("Min-Conflicts", min_conflicts, n))

    # Print comparison table
    header = f"{'Algorithm':<18} | {'Conflicts':<10} | {'Time(ms)':<10} | {'Mem(KB)':<10} | {'Solved':<6} | {'Steps'}"
    print(header)
    print("-" * len(header))

    for r in results:
        print(f"{r['Algorithm']:<18} | "
              f"{r['Conflicts']:<10} | "
              f"{r['Time']:<10.2f} | "
              f"{r['Memory']:<10.2f} | "
              f"{r['Solved']:<6} | "
              f"{r['Steps']}")

