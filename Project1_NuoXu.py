import heapq
import copy
import time

# -------------------------------------- Node Structure --------------------------------------
# Represents a node in the search tree
class PuzzleNode:
    def __init__(self, state, parent = None, action = None, g_cost = 0, h_cost = 0):
        self.state = state # The current puzzle configuration
        self.parent = parent # The node that generate this node
        self.action = action # The action that lead to this state
        self.g_cost = g_cost # Cost from the initial state to this node
        self.h_cost = h_cost # Estimated cost from this node to the goal
        self.f_cost = g_cost + h_cost # Total estimated cost g + h

    # Comparison for priority queue
    # If f_costs are equal, use g_cost as a tie-breaker
    def __lt__(self, other):
        if self.f_cost == other.f_cost:
            return self.g_cost < other.g_cost
        return self.f_cost < other.f_cost
    
    # Equality check
    def __eq__(self, other):
        return isinstance(other, PuzzleNode) and self.state == other.state
    
# -------------------------------------- Function: Find blank tile --------------------------------------
def find_blank(state):
    for r in range(len(state)):
        for c in range(len(state)):
            if state[r][c] == 0:
                return r, c
    return None

# -------------------------------------- Function: List-of lists state to tuple --------------------------------------
def state_to_tuple(state):
    return tuple(map(tuple, state))

# -------------------------------------- Heuristic Functions --------------------------------------
# 1. Uniform Cost Search (h(n) = 0)
def no_heuristic(state, goal_state):
    return 0

# 2. A* with the Misplaced Tile heuristic
def misplaced_tile_heuristic(state, goal_state):
    # Calculate the num of misplaced tiles
    misplaced_count = 0
    for r in range(len(state)):
        for c in range(len(state)):
            if state[r][c] != 0 and state[r][c] != goal_state[r][c]:
                misplaced_count += 1
    return misplaced_count

# 3. A* with the Manhattan Distance heuristic.
# Pre-compute the goal pos
goal_pos = {}
def precompute_goal_pos(goal_state):
    global goal_pos
    goal_pos = {}
    for r in range(len(goal_state)):
        for c in range(len(goal_state)):
            goal_pos[goal_state[r][c]] = (r, c)
    
def manhattan_distance_heuristic(state,goal_state):
    # Calculate the sum of manhattan distance from all tiles to their goal pos
    total_manhattan_distance = 0
    
    for r in range(len(goal_state)):
        for c in range(len(goal_state)):
            tile = state[r][c]
            if tile != 0:
                goal_r, goal_c = goal_pos[tile]
                total_manhattan_distance += abs(r - goal_r) + abs(c - goal_c)
    return total_manhattan_distance

# -------------------------------------- Generate Successor Nodes --------------------------------------
def expand(node, goal_state, heuristic_func):
    # Generates successor nodes from the current node
    successors = []
    state = node.state
    blank_r, blank_c = find_blank(state)
    moves = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]

    for change_r, change_c, action in moves:
        new_r, new_c = blank_r + change_r, blank_c + change_c

        # Check if within the grid
        if 0 <= new_r < len(state) and 0 <= new_c < len(state):
            # Create a new state by swaping the blank tile
            new_state = copy.deepcopy(state) # prevent to modify the original state
            new_state[blank_r][blank_c], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[blank_r][blank_c]

            # Create the successor node
            new_g_cost = node.g_cost + 1
            new_h_cost = heuristic_func(new_state, goal_state)

            successor_node = PuzzleNode(
                state = new_state,
                parent = node,
                action = action,
                h_cost = new_h_cost,
                g_cost = new_g_cost,
            )

            successors.append(successor_node)
    return successors

# -------------------------------------- Check if it is the goal state --------------------------------------
def goal_test(state, goal_state):
    return state == goal_state

# -------------------------------------- General Search Algorithm --------------------------------------
def general_search(initial_state, goal_state, heuristic_func):
    # if using manhattan distance heuristic
    if heuristic_func == manhattan_distance_heuristic:
        precompute_goal_pos(goal_state)

    # Initialize the root node
    initial_h = heuristic_func(initial_state, goal_state)
    start_node = PuzzleNode(state=initial_state, g_cost=0, h_cost=initial_h)

    frontier = [start_node] # nodes waiting to be explored
    heapq.heapify(frontier) # transform the list into min-heap based on f_cost
    explored = set() # store tuples of states visited

    expanded_count = 0
    max_queue_size = 1

    print("\nStarting Search...")
    
    # search loop
    while frontier:
        max_queue_size = max(max_queue_size, len(frontier))

        # get the state with lowest f_cost
        current_node = heapq.heappop(frontier)

        # goal_check
        if goal_test(current_node.state, goal_state):
            print("Goal state reached!")
            return current_node, expanded_count, max_queue_size

        # add to explored state
        # convert state to tuple for hashing before adding to set
        current_state_tuple = state_to_tuple(current_node.state)
        if current_state_tuple in explored: # if it is explored
            continue

        explored.add(current_state_tuple)
        expanded_count += 1

        # print trace for every expanded node
        print(f"The best state to expand with a g(n) = {current_node.g_cost} and h(n) = {current_node.h_cost} is:")
        print_state(current_node.state)

        # expand the node
        successors = expand(current_node, goal_state, heuristic_func)

        # add successors into frontier
        for child_node in successors:
            child_state_tuple = state_to_tuple(child_node.state)
            if child_state_tuple not in explored:
                heapq.heappush(frontier, child_node)

    print("Search failed. Frontier is empty.")
    return None, expanded_count, max_queue_size

# -------------------------------------- Reconstrcut Path --------------------------------------
def reconstruct_path(goal_node):
    #Traces back from the goal node to the start node
    path = []
    current = goal_node
    while current is not None:
        path.append(current.state)
        current = current.parent
    return path[::-1]

# -------------------------------------- Print State --------------------------------------
def print_state(state):
    for row in state:
        print(row)

# -------------------------------------- User Interface --------------------------------------
def get_user_puzzle():
    print("\nEnter your puzzle, using a zero (0) to represent the blank.")
    print("Enter the puzzle delimiting the numbers with a space (e.g., 1 2 3)")
    puzzle = []
    size = 3 # For 8-puzzle
    while len(puzzle) < size:
        row_num = len(puzzle) + 1
        while True:
            try: 
                row_str = input(f"Enter row {row_num}: ").strip()
                row = [int(x) for x in row_str.split()]
                if len(row) != size: # check there are 3 numbers
                    print(f"Error: Please enter {size} numbers for row {row_num}.")
                    continue
                if not all(0 <= x <= 8 for x in row): # check the input is 0 <= x <= 8
                     print("Error: Please use numbers between 0 and 8.")
                     continue
                puzzle.append(row)
                break    
            except ValueError:
                print("Error: Invalid input. Please enter numbers separated by spaces.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    # check 0-8 appears exactly once
    flat_puzzle = [item for sublist in puzzle for item in sublist]
    if sorted(flat_puzzle) != list(range(9)):
        print("\nError: Invalid puzzle configuration.")
        print("The puzzle must contain each number from 0 to 8 exactly once.")
        print("Your input:")
        print_state(puzzle)
        return None
    
    return puzzle

# -------------------------------------- Main --------------------------------------
if __name__ == "__main__":
    # goal state
    GOAL_STATE_8_PUZZLE = [[1, 2, 3],
                           [4, 5, 6],
                           [7, 8, 0]]
    
    initial_state = None
    print("Welcome to my 8-Puzzle Solver.")
    choice = input("Type '1' to use a default puzzle, or '2' to create your own: ").strip()
    if choice == '1':
        initial_state = [[1, 6, 7],
                         [5, 0, 3],
                         [4, 8, 2]]
        print("\nUsing default puzzle:")
        print_state(initial_state)
    elif choice == '2':
        initial_state = get_user_puzzle()
        if initial_state is None:
            exit()
        print("\nUsing custom puzzle:")
        print_state(initial_state)
    else:
        print("Invalid choice. Exiting.")
        exit()

    # Select Algorithm
    print("\nSelect algorithm:")
    print("(1) Uniform Cost Search")
    print("(2) A* with Misplaced Tile Heuristic")
    print("(3) A* with Manhattan Distance Heuristic")
    algo_choice = input("Enter choice (1, 2, or 3): ").strip()

    heuristic = None
    algo_name = ""
    if algo_choice == '1':
        heuristic = no_heuristic
        algo_name = "Uniform Cost Search"
    elif algo_choice == '2':
        heuristic = misplaced_tile_heuristic
        algo_name = "A* with Misplaced Tile Heuristic"
    elif algo_choice == '3':
        heuristic = manhattan_distance_heuristic
        algo_name = "A* with Manhattan Distance Heuristic"
    else:
        print("Invalid algorithm choice. Exiting.")
        exit()

    print(f"\nRunning {algo_name}...")

    start_time = time.time()
    solution_node, nodes_expanded, max_q_size = general_search(initial_state, GOAL_STATE_8_PUZZLE, heuristic)
    end_time = time.time()

    # Print Results
    print("\n--- Search Results ---")
    #print(f"Algorithm: {algo_name}")

    if solution_node:       
        print("Solution Found!")
        print(f"Solution depth was: {solution_node.g_cost}") # g_cost is the depth
        #path = reconstruct_path(solution_node)
        #print("Initial State:")
        #print_state(path[0])
        #print("Goal State:")
        #print_state(path[-1])

    else:
        print("No solution found.")

    print(f"Number of nodes expanded: {nodes_expanded}")
    print(f"Max queue size: {max_q_size}")
    print(f"Time Taken: {end_time - start_time:.4f} seconds")

