from hex_func import *
import importlib
import os
from os.path import abspath, dirname
import json
os.chdir(dirname(abspath(__file__)))

# Setting

WRITE = True
NGAME = 1
DEBUG = True

# file path

bot_path = "./bot"
bot_mod = "bot."
save_path = "./games"

# generate bot list
#bot_name = os.listdir(bot_path) 
#print(bot_name)
bot_list = {name:getattr(importlib.import_module(bot_mod + os.path.splitext(name)[0]), os.path.splitext(name)[0]) for name in os.listdir(bot_path) if os.path.isfile(os.path.join(bot_path, name))}
print(bot_list)
# Running

for n in range(NGAME):
    gameid = str(time.time())
    path = os.path.join(save_path, gameid + '.json')

    res = run_game(bot_list)
    res["id"] = gameid

    if WRITE:
        with open(path, "w") as writer:
            json.dump(res, writer)