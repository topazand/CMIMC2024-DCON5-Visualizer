import pygame
import math
import random
import time
import copy

# No memory, just ?sec/step

# Constants for the hexagon grid
GRID_RADIUS = 3 # Number of paths most distant node
HEX_SIZE = 40    # Size of each hexagon
WIDTH, HEIGHT = 800, 600  # Window dimensions
BACKGROUND_COLOR = (0, 255, 255)  # Aqua
ALL_NEIGHBOR = lambda x, y, z: ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)) # make this more efficient?
SELECT_VALID = lambda lis: [(x, y, z) for (x, y, z) in lis if 1 <= x + y + z <= 2 and -GRID_RADIUS + 1 <= x <= GRID_RADIUS and -GRID_RADIUS + 1 <= y <= GRID_RADIUS and -GRID_RADIUS + 1 <= z <= GRID_RADIUS] # keep those within-bound
TABLE = {1:0, 2:0, 3:1, 4:3, 5:0} # table of scores for each size connect component

# Function to calculate the position of the nodes
def hex_to_pixel(x, y, z):
    xc = HEX_SIZE * (x/2 + y/2 - z)
    yc = -HEX_SIZE * (x*math.sqrt(3)/2 - y*math.sqrt(3)/2)
    return xc + WIDTH / 2, yc + HEIGHT / 2

# Generate a list of node coordinates (vertices of hexagons)
node_coordinates = []
#for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
#    for y in range(max(-GRID_RADIUS, -x - GRID_RADIUS)+1, min(GRID_RADIUS, -x + GRID_RADIUS) + 1):
#        for z in range(max(-GRID_RADIUS, -x - y - GRID_RADIUS)+1, min(GRID_RADIUS, -x - y + GRID_RADIUS) + 1):
for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
    for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            # Check if node is valid
            if 1 <= x + y + z <= 2:
                node_coordinates.append((x, y, z))

#print(node_coordinates)

NEIGHBOR_LIST = dict(zip(node_coordinates, [SELECT_VALID(ALL_NEIGHBOR(*(node))) for node in node_coordinates]))
#print(node_coordinates)
free_coordinates = node_coordinates.copy()
# Initialize the game state
board = {}  # Dictionary to track the state of the board
players = ["white", "black", "red"]  # List of players
players2id = {"white":0, "black":1, "red":2} # Players to ID
current_player_idx = 0  # Index to keep track of the current player
longest_paths = {0:0 , 1:0, 2:0}  # Dictionary to store longest paths for each player

# Function to calculate the longest path on the hexagonal grid from one connected component - should be optimized for mcts
def get_diameter(board, start_node, visit): 
    # Time cost: 
    #   - connect component: n
    #   - 
    def neighbors(node):
        #return SELECT_VALID(ALL_NEIGHBOR(*(node)))
        return NEIGHBOR_LIST[node]
    def con(node): # Find connected component and respective degrees
        visit[node] = 1
        connected[node] = -1
        cnt = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player:
                cnt += 1
                if neighbor not in connected:
                    con(neighbor)
        connected[node] = cnt
    def dfs(node, visited = set()):
        visited.add(node)
        max_path_length = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player and neighbor not in visited:
                path_length = dfs(neighbor, visited.copy())
                max_path_length = max(max_path_length, path_length)
        return max_path_length + 1
    
    try:
        player = board[start_node]
    except Exception as exc:
        print("node empty?")
        print(exc)
        return 0

    connected = dict()
    con(start_node)
    #print(connected)
    if len(connected) <= 3: # must be a line
        return len(connected)
    if 4 <= len(connected) <= 5: # a star if we have a deg-3 node, a line otherwise
        if 3 in connected.values(): # It's a star!
            return len(connected) - 1
        return len(connected)
    if 6 == len(connected):
        three = list(connected.values())
        if 3 in connected.values():
            three.remove(3)
            if 3 in three:
                return 4 # this is a shape x - x - x - x
                         #                     x   x
        return 5 # diameter is 5 otherwise

    # For the larger(>6) ones, diameter must be larger than 5 so we just return 5
    return 5
    # maxl = 0

    # for node in connected:
    #     maxl = max(maxl, dfs(node))
    # return maxl

def score(board): # return current score for each player
    visit = {pos:0 for pos in node_coordinates}
    scores = {0:0 , 1:0, 2:0}
    for pos in board.keys():
        if not visit[pos]:
            d = get_diameter(board, pos, visit)
            if d:
                scores[board[pos]] += TABLE[d]
    return scores


# Bot player logic (Random bot - give a random valid move)
def random_bot_move(board_copy, player):
    node_coordinates = []
    for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
                # Check if node is valid
                if 1 <= x + y + z <= 2:
                    node_coordinates.append((x, y, z))
    empty_nodes = [node for node in node_coordinates if node not in board_copy]
    if len(empty_nodes)==0:
        return None
    return random.choice(empty_nodes)

# Bot player logic (Simple AI - avoids bad moves that "create a 5")
def simple_bot_move(board_copy, player):
    def get_diameter(board, start_node, player): # make sure to pass copy
        # Time cost: 
        #   - connect component: n
        #   - 
        def neighbors(node):
            #return SELECT_VALID(ALL_NEIGHBOR(*(node)))
            return NEIGHBOR_LIST[node]
        def con(node): # Find connected component and respective degrees
            connected[node] = -1
            cnt = 0
            for neighbor in neighbors(node):
                if neighbor in board and board[neighbor] == player:
                    cnt += 1
                    if neighbor not in connected:
                        con(neighbor)
            connected[node] = cnt
        def dfs(node, visited = set()):
            visited.add(node)
            max_path_length = 0
            for neighbor in neighbors(node):
                if neighbor in board and board[neighbor] == player and neighbor not in visited:
                    path_length = dfs(neighbor, visited.copy())
                    max_path_length = max(max_path_length, path_length)
            return max_path_length + 1
        
        board[start_node] = player
        
        try:
            player = board[start_node]
        except Exception as exc:
            print("node empty?")
            print(exc)
            return 0

        connected = dict()
        con(start_node)
        #print(connected)
        if len(connected) <= 3: # must be a line
            return len(connected)
        if 4 <= len(connected) <= 5: # a star if we have a deg-3 node, a line otherwise
            if 3 in connected.values(): # It's a star!
                return len(connected) - 1
            return len(connected)
        if 6 == len(connected):
            three = list(connected.values())
            if 3 in connected.values():
                three.remove(3)
                if 3 in connected.values():
                    return 4 # this is a shape x - x - x - x
                            #                     x   x
            return 5 # diameter is 5 otherwise

        # For the larger(>6) ones, diameter must be larger than 5 so we just return 5
        return 5
        # maxl = 0

    node_coordinates = []
    for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
                # Check if node is valid
                if 1 <= x + y + z <= 2:
                    node_coordinates.append((x, y, z))
    
    # Find handicaps
    empty_nodes = [node for node in node_coordinates if node not in board_copy and get_diameter(board_copy.copy(), node, player) < 5]

    if len(empty_nodes)==0:
        return None
    # Choose a random move
    return random.choice(empty_nodes)

# Bot player logic (Greedy AI - maximize score this turn)

def greedy_bot_move(board_copy, player):
    def get_diameter(board, start_node, visit): 
    # Time cost: 
    #   - connect component: n
    #   - 
        def neighbors(node):
            #return SELECT_VALID(ALL_NEIGHBOR(*(node)))
            return NEIGHBOR_LIST[node]
        def con(node): # Find connected component and respective degrees
            visit[node] = 1
            connected[node] = -1
            cnt = 0
            for neighbor in neighbors(node):
                if neighbor in board and board[neighbor] == player:
                    cnt += 1
                    if neighbor not in connected:
                        con(neighbor)
            connected[node] = cnt
        def dfs(node, visited = set()):
            visited.add(node)
            max_path_length = 0
            for neighbor in neighbors(node):
                if neighbor in board and board[neighbor] == player and neighbor not in visited:
                    path_length = dfs(neighbor, visited.copy())
                    max_path_length = max(max_path_length, path_length)
            return max_path_length + 1
        
        try:
            player = board[start_node]
        except Exception as exc:
            print("node empty?")
            print(exc)
            return 0

        connected = dict()
        con(start_node)
        #print(connected)
        if len(connected) <= 3: # must be a line
            return len(connected)
        if 4 <= len(connected) <= 5: # a star if we have a deg-3 node, a line otherwise
            if 3 in connected.values(): # It's a star!
                return len(connected) - 1
            return len(connected)
        if 6 == len(connected):
            three = list(connected.values())
            if 3 in connected.values():
                three.remove(3)
                if 3 in connected.values():
                    return 4 # this is a shape x - x - x - x
                            #                     x   x
            return 5 # diameter is 5 otherwise

        # For the larger(>6) ones, diameter must be larger than 5 so we just return 5
        return 5
        # maxl = 0

        # for node in connected:
        #     maxl = max(maxl, dfs(node))
        # return maxl
    def score(board): # return current score for each player
        visit = {pos:0 for pos in node_coordinates}
        scores = {0:0 , 1:0, 2:0}
        for pos in board.keys():
            if not visit[pos]:
                d = get_diameter(board, pos, visit)
                if d:
                    scores[board[pos]] += TABLE[d]
        return scores
    
    node_coordinates = []
    for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
                # Check if node is valid
                if 1 <= x + y + z <= 2:
                    node_coordinates.append((x, y, z))

    maxscore = 0
    select = []

    for node in node_coordinates:
        if node not in board_copy:
            board_new = board_copy.copy()
            board_new[node] = player
            s = score(board_new)
            if s[player] > maxscore:
                select = [node]
                maxscore = s[player]
            elif s[player] == maxscore:
                select.append(node)

    #print(maxscore)
    #print(select)
    if len(select)==0:
        return None
    return random.choice(select)


child_values = {}

def monte_carlo_tree_bot_move(board_copy, player):
    SIMULATIONS = 100000
    class State:
        def __init__(self, board, player):
            self.state = board
            self.freec = set(node_coordinates).difference(set(board.keys()))
            self.player = player
        
        def get_legal_moves(self):
            if len(self.state) == 0:
                #print("Returning initial strategy...")
                return self.get_initial_strategy()
            legal = set()
            boarditem = self.state.keys()
            for node in self.state.keys():
                legal = legal.union(set(SELECT_VALID(ALL_NEIGHBOR(*(node)))).difference(boarditem))
                #print(SELECT_VALID(ALL_NEIGHBOR(*(node))))
            return list(legal)
        def get_random_moves(self):
            return list(self.freec)
        def get_current_player(self):
            return self.player
        def get_board(self):
            return self.state
        def move_to(self, move): # move itself
            self.state[move] = self.player
            self.player = (self.player + 1)%3
            #print(self.freec)
            #print(move)
            self.freec.remove(move)
            return self.state
        def make_move(self, move): # create new state
            newstate = self.state.copy()
            newstate[move] = self.player
            return State(newstate, (self.player + 1)%3)
        def get_initial_strategy(self):
            return [(1, 0, 0),(0,1,0),(0,0,1)]
    class Node:
        def __init__(self, state, move=None, parent=None, leaf = None):
            self.state = state  # Game state
            self.move = move  # Move that led to this state
            self.parent = parent
            self.children = []
            self.visits = 0
            self.value = 0
            self.leaf = leaf
            moves = self.state.get_random_moves()
            self.RAVEvisits = dict(zip(moves,[0]*len(moves)))
            self.RAVEvalues = dict(zip(moves,[0]*len(moves)))
            self.move2child = {}

        def is_fully_expanded(self):
            #return len(self.children) == len(self.state.get_legal_moves())
            return len(self.children) == len(self.state.get_random_moves())
        
        def minmse_schedule(self, move):
            return self.RAVEvisits[move]/(self.visits + self.RAVEvisits[move] + 4*self.visits*self.RAVEvisits[move]*RAVE_BIAS*RAVE_BIAS)
        def hand_schedule(self):
            return math.sqrt(k/(k + 3*self.visits))
        def best_child(self,b = None, exploration_weight=1.41): # b - RAVE weight
            if not self.children:
                return None

            best_child = None
            best_ucb1_rave = -float('inf')

            


            for child in self.children:
                if child.visits == 0:
                    return child  # Choose unvisited node

                if not b:
                    #beta = self.minmse_schedule(child.move)
                    beta = self.hand_schedule()
                    #print(beta)
                else:
                    beta = b
                ucb1_rave = beta*self.RAVEvalues[child.move] / self.RAVEvisits[child.move] +  (1-beta)*child.value / child.visits + exploration_weight * math.sqrt(math.log(self.visits) / child.visits)
                if ucb1_rave > best_ucb1_rave:
                    best_ucb1_rave = ucb1_rave
                    best_child = child
                if exploration_weight == 0 and b == 0:
                    child_values[child.move] = child.value / child.visits
                    print(f"{players[self.state.get_current_player()]}: moving at {child.move} gives {child.value} wins and has {child.visits} visits.")

            return best_child

        def expand(self):
            if self.state.state == {(0, 0, 1): 0, (2, -1, 1): 1, (1, 1, -1): 2, (0, 1, 1): 0, (2, -1, 0): 1, (2, 1, -1): 2, (0, 0, 2): 0, (2, -2, 1): 1, (2, 0, -1): 2, (0, -1, 2): 0, (3, -1, 0): 1, (1, 1, 0): 2, (1, -1, 2): 0}:
                print("WTF???")
                print(self.leaf)
            #legal_moves = self.state.get_legal_moves()
            legal_moves = self.state.get_random_moves()
            untried_moves = [move for move in legal_moves if move not in [child.move for child in self.children]]
            #print(untried_moves)
            if untried_moves:
                #print("Adding new child...")
                if self.leaf:
                    print("Why expand here?")
                random_move = random.choice(untried_moves)
                new_state = self.state.make_move(random_move)
                leaf = self.leaf
                if len(new_state.get_random_moves()) == 0: # no valid move remaining
                    leaf = -1
                elif calculate_longest_path(new_state.get_board(), random_move, self.state.get_current_player()) >= 5:
                    leaf = self.state.get_current_player()
                    #print(f"Wow! Player {players[leaf]} wins!!")

                new_node = Node(new_state, move=random_move, parent=self, leaf = leaf)
                self.children.append(new_node)
                self.move2child[random_move] = new_node
                return new_node
            return None

        def simulate(self):

            # Simulate a game starting from this node
            

            current_player = self.state.get_current_player()
            initial_player = current_player
            step = 0
            #print(f"Starting simulation at ")
            tmp_state = State(self.state.state.copy(), self.state.player)
            all_moves = [[],[],[]]
            while True:
                step = step + 1
                #legal_moves = tmp_state.get_legal_moves()
                legal_moves = tmp_state.get_random_moves()# just do random moves?
                #print(f"legal moves:{legal_moves}")
                if len(legal_moves) == 0:
                    #print(f"After {step} steps draw")
                    return -1, all_moves  # The game ended in a draw - draw is NOT favorable

                # Implement a policy to select a move (you can use a random policy for simplicity)
                selected_move = random.choice(list(legal_moves))
                tmp_state.move_to(selected_move)

                # Save result for RAVE
                all_moves[current_player].append(selected_move)

                # Check if the current player wins
                #print(f"selected move {selected_move}")

                if calculate_longest_path(tmp_state.get_board(), selected_move, current_player) >= 5:
                    #print(f"After {step} steps player {players[current_player]} wins")
                    return current_player, all_moves

                current_player = tmp_state.get_current_player()

        def backpropagate(self, winner, moves):
            #if self.state.state == {(0, 0, 1): 0, (2, -1, 1): 1, (1, 1, -1): 2, (0, 1, 1): 0, (2, -1, 0): 1, (2, 1, -1): 2, (0, 0, 2): 0, (2, -2, 1): 1, (2, 0, -1): 2, (0, -1, 2): 0, (3, -1, 0): 1, (1, 1, 0): 2, (0, -1, 3): 0}:
                #print(f"Winner: {winner}, move: {moves}")
            curplayer = self.state.get_current_player()
            for move in moves[curplayer]:
                if winner == curplayer:
                    self.RAVEvisits[move] += 1
                    self.RAVEvalues[move] += 1
                else:
                    self.RAVEvisits[move] += 1

            if self.parent:
                if winner == self.parent.state.get_current_player():
                    self.visits += 1
                    self.value += 1
                else:
                    self.visits += 1
                self.parent.backpropagate(winner, moves)
            else:
                if winner == (curplayer - 1)%3:
                    self.visits += 1
                    self.value += 1
                else:
                    self.visits += 1

            


            
    RAVE_BIAS = 0.05 # b parameter
    k = 5000 # number of steps when weight should be equal

    child_values.clear()

    root = Node(State(copy.deepcopy(board_copy), player))
    for nsim in range(SIMULATIONS):
        node = root

        # Selection phase
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        if node.leaf is not None:
            node.backpropagate(node.leaf,[[],[],[]])
            continue
        # Backpropagate now if the game already has winner

        if not node.is_fully_expanded():
            # Expansion phase
            new_node = node.expand()
            if new_node:
                node = new_node

        # Simulation phase
        result, moves = node.simulate()
        moves[(node.state.get_current_player() - 1)%3].append(node.move) # don't forget the first step
        # Backpropagation phase
        node.backpropagate(result, moves)

    # Choose the best move based on the root's children visits
    best_child = root.best_child(b = 0,exploration_weight=0)  # Set exploration_weight to 0 for pure exploitation
    #print(f"children:{root.children}")
    print(f"best_child:{best_child.state.get_board()}")
    print(f"best_child move:{best_child.move}")
    return root
# scary monte carlo!

bot_list = [greedy_bot_move, random_bot_move, simple_bot_move]

# Main game loop
def is_node_clicked(mouse_pos):
    for node in node_coordinates:
        node_x, node_y, node_z = node
        node_center_x, node_center_y = hex_to_pixel(node_x, node_y, node_z)
        distance = math.sqrt((node_center_x - mouse_pos[0]) ** 2 + (node_center_y - mouse_pos[1]) ** 2)
        if distance < 15:  # Adjust the radius for clicking sensitivity
            return node
    return None
#

running = True

lastmoves = []

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hexagonal Grid")
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
#             clicked_node = lastmoves[-1]
#             del lastmoves[-1]
#             current_player = players[current_player_idx]
#             del board[clicked_node]
#             # Check for win?
#             #longest_paths[current_player] = max(longest_paths[current_player], calculate_longest_path(board, clicked_node, current_player))
#             current_player_idx = (current_player_idx -1) % len(players)
#         elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#             mouse_pos = pygame.mouse.get_pos()
#             clicked_node = is_node_clicked(mouse_pos)
#             if clicked_node and not board.get(clicked_node):
#                 current_player = players[current_player_idx]
#                 board[clicked_node] = current_player
#                 # Check for win?
#                 #longest_paths[current_player] = max(longest_paths[current_player], calculate_longest_path(board, clicked_node, current_player))
#                 current_player_idx = (current_player_idx + 1) % len(players)
#                 lastmoves.append(clicked_node)
play = False
coord = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            #if current_player_idx == 0:
            print(free_coordinates)
            if len(free_coordinates)==0:
                print("Game ends: No valid move")
                scores = score(board)
                for idx, player in enumerate(players):
                    print(f"{player.capitalize()}: {scores[players2id[player]]}")
                running = False
                break
            if play:
            #runs += 1
        #elif runs > 0:
            #runs -= 1
                #print("Bot moves")
                board_copy = copy.deepcopy(board)
                curfunc = bot_list[current_player_idx]
                bot_move = curfunc(board_copy, current_player_idx)
                if bot_move and bot_move in free_coordinates:
                    #print(f"bot {current_player_idx} moves at {bot_move}")
                    board[bot_move] = current_player_idx
                    free_coordinates.remove(bot_move);
                    
                else:

                    print(f"{players[current_player_idx]} is not making a valid move!")
                    #if len(free_coordinates) != 0:
                    #    bot_move = random.choice(free_coordinates); # Use random move
                    #    board[bot_move] = current_player_idx
                    #    free_coordinates.remove(bot_move);
                    #else:
                    #    running = False
                #print(board)
                current_player_idx = (current_player_idx + 1) % len(players)
            else:
                mouse_pos = pygame.mouse.get_pos()
                clicked_node = is_node_clicked(mouse_pos)
                if clicked_node and not board.get(clicked_node):
                    print("Node clicked:{clicked_node}")
                    current_player = players[current_player_idx]
                    board[clicked_node] = current_player_idx
                    free_coordinates.remove(clicked_node);
                    # Check for win?
                    # longest_paths[current_player_idx] = max(longest_paths[current_player_idx], calculate_longest_path(board, clicked_node, current_player_idx))
                    current_player_idx = (current_player_idx + 1) % len(players)
                    #lastmoves.append(clicked_node)

    # Clear the screen
    screen.fill(BACKGROUND_COLOR)

    #print(node_coordinates)
    # Draw the nodes (vertices of hexagons)
    font = pygame.font.Font(None, 16)
    for x, y, z in node_coordinates:
        xc, yc = hex_to_pixel(x, y, z)
        pygame.draw.circle(screen, (0, 0, 0), (int(xc), int(yc)), 3)  # Black nodes
    # Coordinate?
        if coord:
            text = font.render(str((x,y,z)), True, "blue")
            screen.blit(text, (xc-25, yc))

    
    # Draw the pieces
    for node, player in board.items():
        x, y, z = node
        xc, yc = hex_to_pixel(x, y, z)
        if player == 0:
            pygame.draw.circle(screen, (255, 255, 255), (int(xc), int(yc)), 15)  # White piece
        elif player == 1:
            pygame.draw.circle(screen, (0, 0, 0), (int(xc), int(yc)), 15)  # Black piece
        elif player == 2:
            pygame.draw.circle(screen, (255, 0, 0), (int(xc), int(yc)), 15)  # Red piece

    # Draw the longest path counters
    font = pygame.font.Font(None, 36)
    scores = score(board)
    for idx, player in enumerate(players):
        text = font.render(f"{player.capitalize()}: {scores[players2id[player]]}", True, (0, 0, 0))
        screen.blit(text, (WIDTH - 200, 20 + idx * 40))

    pygame.display.flip()

# Quit Pygame
pygame.quit()
