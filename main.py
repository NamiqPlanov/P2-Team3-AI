import random
import time
import tracemalloc
from collections import deque

# Input
def read_board(file_path):
    """
    Reads an initial board configuration from a text file.
    Each line in the file represents a queen's column position in its row.
    Lines starting with '#' are treated as comments.
    """
    board = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.split('#')[0].strip()  # remove comments and whitespace
            if line:  # ignore empty lines
                board.append(int(line))
    return board

# Board Printing
def print_board(queen_cols):
    """
    Prints the N-Queens board in a human-readable format.
    'Q' represents a queen, '.' is an empty square.
    """
    n = len(queen_cols)
    for r in range(n):
        print(' '.join('Q' if queen_cols[r] == c else '.' for c in range(n)))
    print()  # extra line for spacing

# Conflict Counter
def conflicts(board, row, col):
    """
    Counts how many queens are attacking the position (row, col).
    Checks for same column and diagonals conflicts.
    """
    count = 0
    for r, c in enumerate(board):
        if r == row:  # skip the queen itself
            continue
        if c == col or abs(r - row) == abs(c - col):  # same column or diagonal
            count += 1
    return count

# AC3 Constraint Propagation
def ac3(domains, n):
    """
    Implements the AC-3 (Arc Consistency) algorithm to reduce the domains of unassigned queens.
    Removes impossible values early to prune the search space.
    """
    queue = deque((i, j) for i in range(n) for j in range(n) if i != j)  # all pairs of rows
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if not domains[xi]:  # if a domain becomes empty, no solution possible
                return False
            for k in range(n):
                if k != xi:
                    queue.append((k, xi))
    return True

def revise(domains, xi, xj):
    """
    Revise the domain of xi based on the domain of xj.
    Remove values from xi that conflict with a single value in xj.
    """
    revised = False
    if len(domains[xj]) == 1:  # only one value in xj
        vj = next(iter(domains[xj]))
        diff = abs(xi - xj)
        forbidden = {vj, vj + diff, vj - diff}  # column + diagonals
        to_remove = domains[xi] & forbidden
        if to_remove:
            domains[xi] -= to_remove
            revised = True
    return revised

# Heuristics
def select_var_mrv(unassigned, domains):
    """
    Select the next row (variable) using MRV (Minimum Remaining Values) heuristic.
    Chooses the row with the fewest legal values left.
    """
    return min(unassigned, key=lambda r: (len(domains[r]), r))

def order_lcv(row, domains, assignment):
    """
    Order columns in a row using LCV (Least Constraining Value) heuristic.
    Prefers values that eliminate the fewest options for other unassigned rows.
    """
    def score(col):
        s = 0
        for r, c in enumerate(assignment):
            if c != -1:
                if c == col or abs(r - row) == abs(c - col):
                    s += 1
        return s
    return sorted(domains[row], key=score)

# Backtracking CSP (Iterative)
def backtracking_csp(n):
    """
    Solves N-Queens using an iterative backtracking algorithm with CSP heuristics:
    - MRV (Minimum Remaining Values)
    - LCV (Least Constraining Value)
    - AC3 (Arc Consistency)
    """
    domains = {i: set(range(n)) for i in range(n)}  # all columns available initially
    ac3(domains, n)  # initial constraint propagation
    start = [-1] * n  # -1 indicates unassigned
    stack = [(start, domains)]
    steps = 0
    while stack:
        steps += 1
        assignment, doms = stack.pop()
        if all(v != -1 for v in assignment):
            # check if solution is conflict-free
            if sum(conflicts(assignment, r, assignment[r]) for r in range(n)) == 0:
                return assignment, steps
            continue
        # select next row to assign
        unassigned = [r for r in range(n) if assignment[r] == -1]
        row = select_var_mrv(unassigned, doms)
        for col in order_lcv(row, doms, assignment):
            new_assign = assignment[:]
            new_assign[row] = col
            new_domains = {r: doms[r].copy() for r in range(n)}
            new_domains[row] = {col}
            if ac3(new_domains, n):
                stack.append((new_assign, new_domains))
    return None, steps  # no solution found

# Min-Conflicts (Iterative Search)
def min_conflicts(n, max_steps=200000):
    """
    Solves N-Queens using the Min-Conflicts heuristic search algorithm.
    Suitable for large N (e.g., N > 50).
    Starts with a random board and iteratively repairs conflicts.
    """
    board = list(range(n))
    random.shuffle(board)
    steps = 0
    for _ in range(max_steps):
        steps += 1
        # find all queens that are in conflict
        conflicted = [r for r in range(n) if conflicts(board, r, board[r]) > 0]
        if not conflicted:
            return board, steps  # solved
        # randomly pick one conflicted queen
        row = random.choice(conflicted)
        # choose a column with minimum conflicts
        min_conf = min(conflicts(board, row, c) for c in range(n))
        best_cols = [c for c in range(n) if conflicts(board, row, c) == min_conf]
        board[row] = random.choice(best_cols)
    return None, steps  # failed to find solution within max_steps

# Runner 
if __name__ == "__main__":
    # Try reading board from file
    try:
        initial = read_board("2_n-queen.txt")
        n = len(initial)
    except FileNotFoundError:
        print("n-queen.txt not found → using manual input")
        n = int(input("Number of queens (10–1000): "))
        initial = [random.randint(0, n - 1) for _ in range(n)]
    print("\nInitial board:")
    print_board(initial)

    tracemalloc.start()  # start memory tracking
    t0 = time.perf_counter()  # start timer

    # Algorithm selection based on size
    if n <= 50:
        solution, steps = backtracking_csp(n)
        alg_name = "CSP Backtracking"
        heuristics_used = "MRV + LCV + AC3"
    else:
        solution, steps = min_conflicts(n)
        alg_name = "Min-Conflicts"
        heuristics_used = "Random Init + Greedy Repair"

    t1 = time.perf_counter()
    peak_mem = tracemalloc.get_traced_memory()[1] / 1024  # peak memory in KB
    tracemalloc.stop()
    time_ms = (t1 - t0) * 1000  # time in milliseconds
    # calculate total conflicts (should be zero if solved)
    if solution:
        total_conf = sum(conflicts(solution, r, solution[r]) for r in range(n)) // 2
    else:
        total_conf = "N/A"
    # print results in a table
    header = f"{'Algorithm':<18} | {'Heuristics':<28} | {'Conflicts':<10} | {'Time(ms)':<10} | {'Mem(KB)':<10} | {'Solved':<6} | {'Steps'}"
    print("\n" + header)
    print("-" * len(header))
    print(f"{alg_name:<18} | {heuristics_used:<28} | {total_conf:<10} | {time_ms:<10.2f} | {peak_mem:<10.2f} | {'Yes' if solution else 'No'} | {steps}")
    # show solved board if found
    if solution:
        print("\nSolved board:")
        print_board(solution)
    else:
        print("\nNo solution found.")