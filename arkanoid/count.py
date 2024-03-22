import os
import pickle

filepath = "log"
filename = "count.pickle"
with open(os.path.join(filepath, filename), 'rb') as file:
    saved_data = pickle.load(file)
    print(saved_data)