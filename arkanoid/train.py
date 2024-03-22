import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

def load_game_data(filepath):
    filenames = os.listdir(filepath)
    game_data = []
    game_command = []
    mapping = {"MOVE_LEFT": -1, "NONE": 0, "MOVE_RIGHT": 1}

    for filename in filenames:
        with open(os.path.join(filepath, filename), 'rb') as file:
            saved_data = pickle.load(file)
            game_data.extend(saved_data['data'])
            saved_data['x'] = [mapping[action] for action in saved_data['x']]
            game_command.extend(saved_data['x'])

    return game_data, game_command

def prepare_data(game_data):
    features = []
    for data_point in game_data:
        ball_position = data_point["ball"]
        platform_position = data_point["platform"]
        bricks_remaining = len(data_point["bricks"])
        features.append([ball_position[0], ball_position[1], platform_position[0], bricks_remaining])

    return features

game_data, game_command = load_game_data("log")

features = prepare_data(game_data)

labels = game_command

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.01)

#knn_classifier = KNeighborsClassifier()
knn_classifier = KNeighborsClassifier(n_neighbors=1)

knn_classifier.fit(X_train, y_train)

accuracy = knn_classifier.score(X_test, y_test)
print("Accuracy:", accuracy)

with open("knn_classifier_model.pickle", 'wb') as file:
    pickle.dump(knn_classifier, file)
