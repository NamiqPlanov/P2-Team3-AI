import random
import time
import tracemalloc
from collections import deque

# File Input
def read_board(file_path):
    board = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()
            if line:
                board.append(int(line))
    return board

# Board Printing
def print_board(queen_cols):
    n = len(queen_cols)
    for r in range(n):
        print(' '.join('Q' if queen_cols[r] == c else '.' for c in range(n)))
    print()


# Conflict Counter
def conflicts(board, row, col):
    count = 0
    for r, c in enumerate(board):
        if r == row:
            continue
        if c == col or abs(r-row) == abs(c-col):
            count += 1
    return count

# AC3 Constraint Propagation
def ac3(domains, n):
    queue = deque((i, j) for i in range(n) for j in range(n) if i != j)
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:
                return False
            for k in range(n):
                if k != xi:
                    queue.append((k, xi))
    return True


# edit: Correct arc-consistency logic
def revise(domains, xi, xj):
    revised = False
    if len(domains[xj]) == 1:
        vj = next(iter(domains[xj]))
        diff = abs(xi - xj)
        forbidden = {vj, vj + diff, vj - diff}
        to_remove = domains[xi] & forbidden
        if to_remove:
            domains[xi] -= to_remove
            revised = True
    return revised


# Heuristics
# MRV + tie break by row index
def select_var_mrv(unassigned, domains):
    return min(unassigned, key=lambda r: (len(domains[r]), r))

# LCV ordering
def order_lcv(row, domains, assignment):
    def score(col):
        s = 0
        for r, c in enumerate(assignment):
            if c != -1:
                if c == col or abs(r-row) == abs(c-col):
                    s += 1
        return s
    return sorted(domains[row], key=score)


# Backtracking CSP (Iterative)
def backtracking_csp(n):
    domains = {i: set(range(n)) for i in range(n)}
    ac3(domains, n)
    start = [-1]*n
    stack = [(start, domains)]
    steps = 0  # <-- step counter
    while stack:
        steps += 1
        assignment, doms = stack.pop()
        if all(v != -1 for v in assignment):
            if sum(conflicts(assignment, r, assignment[r]) for r in range(n)) == 0:
                return assignment, steps  # <-- return steps
            continue
        unassigned = [r for r in range(n) if assignment[r] == -1]
        row = select_var_mrv(unassigned, doms)
        for col in order_lcv(row, doms, assignment):
            new_assign = assignment[:]
            new_assign[row] = col
            new_domains = {r: doms[r].copy() for r in range(n)}
            new_domains[row] = {col}
            if ac3(new_domains, n):
                stack.append((new_assign, new_domains))

    return None, steps  # <-- also return steps if no solution


# Min-Conflicts (Iterative Search)
def min_conflicts(n, max_steps=200000):
    board = list(range(n))
    random.shuffle(board)
    steps = 0
    for _ in range(max_steps):
        steps += 1
        conflicted = [r for r in range(n) if conflicts(board, r, board[r]) > 0]
        if not conflicted:
            return board, steps
        row = random.choice(conflicted)

        # edit: random tie-breaking among best columns
        min_conf = min(conflicts(board, row, c) for c in range(n))
        best_cols = [c for c in range(n) if conflicts(board, row, c) == min_conf]
        board[row] = random.choice(best_cols)

    return None, steps


# Runner
if __name__ == "__main__":
    try:
        initial = read_board("2_n-queen.txt")
        n = len(initial)
    except FileNotFoundError:
        print("n-queen.txt not found → using random n")
        n = int(input('Number of lines:'))
        initial = [random.randint(0, n-1) for _ in range(n)]

    print("Initial board:")
    print_board(initial)

    tracemalloc.start()
    t0 = time.perf_counter()

    solution, steps = backtracking_csp(n)
    alg_name = "CSP Backtracking"
    heuristics_used = "MRV + LCV + TieBreak + AC3"

    t1 = time.perf_counter()
    peak_mem = tracemalloc.get_traced_memory()[1] / 1024
    tracemalloc.stop()

    time_ms = (t1 - t0) * 1000

    if solution:
        total_conf = sum(conflicts(solution, r, solution[r]) for r in range(n)) // 2
    else:
        total_conf = "N/A"

    header = f"{'Algorithm':<18} | {'Heuristics':<28} | {'Conflicts':<10} | {'Time(ms)':<10} | {'Mem(KB)':<10} | {'Solved':<6} | {'Steps'}"
    print("\n" + header)
    print("-"*len(header))

    print(f"{alg_name:<18} | {heuristics_used:<28} | {total_conf:<10} | {time_ms:<10.2f} | {peak_mem:<10.2f} | {'Yes' if solution else 'No'} | {steps}")
    if solution:
        print("\nSolved board:")
        print_board(solution)
    else:
        print("\nNo solution found.")
