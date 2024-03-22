import os
import pickle

def load_game_data(filepath):
    filenames = os.listdir(filepath)
    game_data = []
    game_command = []
    for filename in filenames:
        with open(os.path.join(filepath, filename), 'rb') as file:
            saved_data = pickle.load(file)
            game_data.extend(saved_data['data'])
            game_command.extend(saved_data['x'])
    return game_data, game_command

# 讀取遊戲資料
game_data, game_command = load_game_data("log")

# 印出資料結構的大小
print("Number of data points:", len(game_data))
print("Example data point:\n", game_data[0])
print("Number of command points:", len(game_command))
print("Example data point:", game_command[0])
