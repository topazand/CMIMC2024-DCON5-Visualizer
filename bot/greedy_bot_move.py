import random
from util import *

def greedy_bot_move(board_copy, player):
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
    if len(select)==0:
        return None
    return random.choice(select)