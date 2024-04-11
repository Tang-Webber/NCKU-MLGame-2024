import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.multioutput import MultiOutputRegressor

def load_game_data(filepath):
    filenames = os.listdir(filepath)
    game_data = []
    record_list = []

    for filename in filenames:
        with open(os.path.join(filepath, filename), 'rb') as file:
            saved_data = pickle.load(file)
            game_data.extend(saved_data['data'])
            record_list.extend(saved_data['record'])

    return game_data, record_list

def prepare_data(game_data, record_list):
    features = []
    labels = []
    for data_point, record in zip(game_data, record_list):
        f_sensor_list = data_point["F_sensor"]
        l_sensor_list = data_point["L_sensor"]
        r_sensor_list = data_point["R_sensor"]
        l_t_sensor_list = data_point["L_T_sensor"]
        r_t_sensor_list = data_point["R_T_sensor"]
        end_x = data_point["end_x"]
        end_y = data_point["end_y"]
        #features.append[data_point["F_sensor"], data_point["L_sensor"], data_point["L_T_sensor"], data_point["R_sensor"], data_point["R_T_sensor"], data_point["end_x"], data_point["end_y"]]
        features.append([f_sensor_list, l_sensor_list, l_t_sensor_list, r_sensor_list, r_t_sensor_list, end_x, end_y])
        #labels.append([record["left_PWM"], record["right_PWM"]])
        if record == "UP":
            labels.append(0)
        elif record == "DOWN":
            labels.append(1)
        elif record == "RIGHT":
            labels.append(2)
        elif record == "LEFT":
            labels.append(3)
        elif record == "NONE":
            labels.append(4)

    return features, labels
    #return np.array(features), labels

game_data, record_list = load_game_data("log")

features, labels = prepare_data(game_data, record_list)

accuracy = 0
#while accuracy <= 0.7:
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.1)
decision_tree_regressor = DecisionTreeRegressor(max_depth=40)
#multi_output_regressor = MultiOutputRegressor(decision_tree_regressor)
#multi_output_regressor.fit(X_train, y_train)
decision_tree_regressor.fit(X_train, y_train)

#accuracy = multi_output_regressor.score(X_test, y_test)
accuracy = decision_tree_regressor.score(X_test, y_test)
print("PWM Accuracy:", accuracy)

#with open("model.pickle", 'rb') as file:
#    model = pickle.load(file)
#print(model)
#decision_tree_model = model.estimators_[0]
#decision_tree_model.partial_fit(X_train, y_train)

#model.estimators_[0] = decision_tree_model

with open("multi_output_decision_tree_model.pickle", 'wb') as file:
    #pickle.dump(multi_output_regressor, file)
    pickle.dump(decision_tree_regressor, file)
