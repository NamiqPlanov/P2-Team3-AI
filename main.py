import random
import time
import tracemalloc
from collections import deque

def read_board(file_path):
    board = []
    with open(file_path, 'r') as f:
        for line in f:
            # Remove comments and spaces
            line = line.split('#')[0].strip()
            if line:
                # Add row's queen column to board
                board.append(int(line))
    return board

def print_board(queen_cols):
    n = len(queen_cols)
    for r in range(n):
        # Print 'Q' for queen, '.' for empty
        print(' '.join('Q' if queen_cols[r] == c else '.' for c in range(n)))
    print()

# Count conflicts for a queen at (row, col)
def conflicts(board, row, col):
    count = 0
    for r, c in enumerate(board):
        if r == row:
            continue
        # Check same column or diagonal conflict
        if c == col or abs(r-row) == abs(c-col):
            count += 1
    return count


def ac3(domains, n):
    # Create all variable pairs to check
    queue = deque((i, j) for i in range(n) for j in range(n) if i != j)
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                # No valid values left → failure
                return False
            for k in range(n):
                if k != xi:
                    # Re-check neighbors if domains changed
                    queue.append((k, xi))
    return True

# Domains for AC3
def revise(domains, xi, xj):
    revised = False
    to_remove = set()
    for vi in domains[xi]:
        supported = False
        for vj in domains[xj]:
            # Value is valid if no conflicts with neighbor
            if vj != vi and abs(xi - xj) != abs(vi - vj):
                supported = True
                break
        if not supported:
            to_remove.add(vi)
    if to_remove:
        # Remove unsupported values from domain
        domains[xi] -= to_remove
        revised = True
    return revised

# Minimum Remaining Values
def select_var_mrv(unassigned, domains):
    return min(unassigned, key=lambda r: (len(domains[r]), r))

# Least Constraining Value
def order_lcv(row, domains, assignment):
    def score(col):
        s = 0
        for r, c in enumerate(assignment):
            if c != -1:
                if c == col or abs(r-row) == abs(c-col):
                    s += 1
        return s
    # Sort values that constrain others the least
    return sorted(domains[row], key=score)

def backtracking_csp(n):
    # Start with all columns possible for each row
    domains = {i: set(range(n)) for i in range(n)}
    ac3(domains, n)  # Reduce domains before starting

    start = [-1]*n  # -1 means unassigned
    stack = [(start, domains)]
    steps = 0

    while stack:
        steps += 1
        assignment, doms = stack.pop()

        # Checking if all rows have a queen
        if all(v != -1 for v in assignment):
            if sum(conflicts(assignment, r, assignment[r]) for r in range(n)) == 0:
                return assignment, steps  # Found solution
            continue

        # Picking next row to assign
        unassigned = [r for r in range(n) if assignment[r] == -1]
        row = select_var_mrv(unassigned, doms)

        # Trying all valid columns, ordered by LCV
        for col in order_lcv(row, doms, assignment):
            new_assign = assignment[:]
            new_assign[row] = col

            # Copy domains and fix current assignment
            new_domains = {r: doms[r].copy() for r in range(n)}
            new_domains[row] = {col}

            # AC3 to reduce future conflicts
            if ac3(new_domains, n):
                stack.append((new_assign, new_domains))

    return None, steps  # No solution found

# For large n
def min_conflicts(n, max_steps=200000):
    # Start with random initial board
    board = list(range(n))
    random.shuffle(board)

    # Keep track of conflicts for fast lookup
    col_count = [0]*n
    diag1_count = [0]*(2*n)
    diag2_count = [0]*(2*n)

    for r in range(n):
        c = board[r]
        col_count[c] += 1
        diag1_count[r - c + n] += 1
        diag2_count[r + c] += 1

    def conflict_count(r, c):
        # Number of conflicts for (r, c)
        return (
            col_count[c] +
            diag1_count[r - c + n] +
            diag2_count[r + c] - 3  # remove self counts
        )

    steps = 0

    for _ in range(max_steps):
        steps += 1

        # Find all rows with conflicts
        conflicted = [r for r in range(n) if conflict_count(r, board[r]) > 0]
        if not conflicted:
            return board, steps  # solved

        # Pick a random conflicted queen
        row = random.choice(conflicted)

        # Remove old queen from counters
        old_col = board[row]
        col_count[old_col] -= 1
        diag1_count[row - old_col + n] -= 1
        diag2_count[row + old_col] -= 1

        # Find the best column with minimal conflicts
        min_conf = float('inf')
        best_cols = []

        for c in range(n):
            conf = (
                col_count[c] +
                diag1_count[row - c + n] +
                diag2_count[row + c]
            )
            if conf < min_conf:
                min_conf = conf
                best_cols = [c]
            elif conf == min_conf:
                best_cols.append(c)

        # Move queen to one of the best positions
        new_col = random.choice(best_cols)
        board[row] = new_col

        # Update counters
        col_count[new_col] += 1
        diag1_count[row - new_col + n] += 1
        diag2_count[row + new_col] += 1

    return None, steps  # No solution within max_steps


if __name__ == "__main__":

    try:
        initial = read_board("p2_n-queen.txt")
        n = len(initial)
    except FileNotFoundError:
        print("p2_n-queen.txt not found → using manual input")
        n = int(input("Number of lines (10-1000): "))

    if n < 10 or n > 1000:
        raise ValueError("n must be between 10 and 1000")

    print(f"\nSolving N-Queens for n = {n}")

    tracemalloc.start()  # Start memory tracking
    t0 = time.perf_counter()  # Start timer

    if n <= 50:
        solution, steps = backtracking_csp(n)
        alg_name = "CSP Backtracking"
        heuristics_used = "MRV + LCV + AC3"
    else:
        solution, steps = min_conflicts(n)
        alg_name = "Min-Conflicts"
        heuristics_used = "Iterative Repair + Random TieBreak"

    t1 = time.perf_counter()
    peak_mem = tracemalloc.get_traced_memory()[1] / 1024
    tracemalloc.stop()  # Stop memory tracking

    time_ms = (t1 - t0) * 1000

    if solution:
        total_conf = sum(conflicts(solution, r, solution[r]) for r in range(n)) // 2
    else:
        total_conf = "N/A"

    # Printing results
    header = f"{'Algorithm':<18} | {'Heuristics':<30} | {'Conflicts':<10} | {'Time(ms)':<10} | {'Mem(KB)':<10} | {'Solved':<6} | {'Steps'}"
    print("\n" + header)
    print("-"*len(header))

    print(f"{alg_name:<18} | {heuristics_used:<30} | {total_conf:<10} | {time_ms:<10.2f} | {peak_mem:<10.2f} | {'Yes' if solution else 'No'} | {steps}")

    if solution:
        print("\nSolution (column index per row):")
        print(solution)

        if n <= 50:
            print("\nBoard visualization:")
            print_board(solution)
        else:
            print("\nBoard not printed (n too large).")
    else:
        print("\nNo solution found.")
