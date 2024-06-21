import os
import pickle
import random

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        print("Initial ml script")
        self.last_score = 0 
        self.last_direction = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}
        self.last_action = ""
        self.action_to_index = {"UP": 0, "DOWN": 1, "LEFT": 2, "RIGHT": 3}

        self.last_state = None
        
        self.alpha = 0.06       # Learning rate
        self.gamma = 0.9        # Future Discount factor
        self.lambda_val = 0.7   #Reward_B Discount factor
        self.epsilon = 0.99     #Exploration rate

        model_file = "model.pickle"
        if os.path.isfile(model_file):
            with open(model_file, 'rb') as f:
                self.q_table = pickle.load(f)
        else:
            self.q_table = {}
            
            for state0 in range(8):
                for state1 in range(8):
                    for state2 in range(8):
                        for state3 in range(8):
                            state = (state0, state1, state2, state3)
                            for action in ["UP", "DOWN", "LEFT", "RIGHT"]:
                                self.q_table[(state, action)] = 0 
            self.q_table[(None, '')] = 0

    def preprocess(self, scene_info):
        # Calculate the distance between each object and the squid, categorize them into four directions (UP, DOWN, LEFT, RIGHT) based on their coordinate differences.
        objects = scene_info["foods"]  # Information of all objects
        squid_x, squid_y = scene_info["self_x"], scene_info["self_y"]  # Squid's coordinates
        distances = []
        scores = []
        for obj in objects:
            scores.append(obj["score"])
            diff_x = obj["x"] - squid_x
            diff_y = obj["y"] - squid_y
            distances.append((diff_x, diff_y))

        sorted_objects = sorted(zip(distances, scores), key=lambda x: abs(x[0][0]) + abs(x[0][1]))
        selected_objects = sorted_objects[:25]  # Select the N closest objects
        selected_distances, selected_scores = zip(*selected_objects)

        # Calculate the sum of scores for each direction
        scores_sum = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}
        for (diff_x, diff_y), score in zip(selected_distances, selected_scores):
            if diff_x > 0 and abs(diff_x) * 1 >= abs(diff_y):
                scores_sum["RIGHT"] += score
            if diff_x < 0 and abs(diff_x) * 1 < abs(diff_y):
                scores_sum["LEFT"] += score
            if diff_y < 0 and abs(diff_y) * 1 > abs(diff_x):
                scores_sum["UP"] += score
            if  diff_y > 0 and abs(diff_y) * 1 > abs(diff_x):
                scores_sum["DOWN"] += score

        return scores_sum

    def simplify_features(self, scene_info):
        # Sum up object scores in each direction to simplify features
        scores = self.preprocess(scene_info)
        
        # Quantize the scores to the range of 0 to 7
        quantized_scores = {}
        for direction, score_sum in scores.items():
            if score_sum < -9:
                quantized_scores[direction] = 1
            elif -9 <= score_sum < -5:
                quantized_scores[direction] = 2
            elif -5 <= score_sum < 0:
                quantized_scores[direction] = 3
            elif 0 <= score_sum < 1:
                quantized_scores[direction] = 0
            elif 1 <= score_sum < 4:
                quantized_scores[direction] = 4
            elif 4 <= score_sum < 9:
                quantized_scores[direction] = 5
            elif 9 <= score_sum < 13:
                quantized_scores[direction] = 6
            else:
                quantized_scores[direction] = 7
        #print(quantized_scores)
        #print(scores)
        #state = tuple(quantized_scores.items())
        #return state
        state_tuple = (
            quantized_scores.get("UP", 0),
            quantized_scores.get("DOWN", 0),
            quantized_scores.get("LEFT", 0),
            quantized_scores.get("RIGHT", 0)
        )
        return state_tuple

    def reward_scheme(self, scene_info):
        # Calculate rewards
        current_score = scene_info["score"]
        reward_a = 0  # Reward a, based on score change
        reward_b = 0  # Reward b, based on the movement direction
        #directions = self.simplify_features(scene_info)
        
        reward_a = current_score - self.last_score
        if reward_a > 0:
            reward_a += 2

        if self.last_action != "":
            #rank = sorted(self.last_direction, key=lambda x: self.last_direction.count(x), reverse=True).index(self.last_action) + 1
            #rank = sorted_scores.index((self.last_action, self.last_direction[self.last_action])) + 1
            #rank = [i for i, (key, _) in enumerate(sorted_scores) if key == self.last_action][0]
            index = self.action_to_index[self.last_action]
            last_score = self.last_state[index]

            rank = 5
            for key in self.last_state:
                #print(last_score, "   ",  key)
                if last_score >= key:
                    rank -= 1

            #print("index = ", index)
            #print("rank = ", rank)

            if rank == 1:
                reward_b += 5  # Highest reward for choosing the largest score
            elif rank == 2:
                reward_b += 3
            elif rank == 3:
                reward_b -= 3
            elif rank == 4:
                reward_b -= 5

        total_reward =  reward_a + self.lambda_val * reward_b 
        self.last_score = current_score

        return total_reward
        
    def update_q_table(self, state, action, reward, next_state):
        # Update Q Table
        #current_q_value = self.q_table.get((state, action), 0)
        current_q_value = self.q_table[(state, action)]
        max_next_q_value = max([self.q_table.get((next_state, a), 0) for a in ["UP", "DOWN", "LEFT", "RIGHT"]])
        new_q_value = (1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * max_next_q_value)
        self.q_table[(state, action)] = new_q_value
        #print(self.q_table[(state, action)] - current_q_value)
        
    def update(self, scene_info: dict, *args, **kwargs):
        # print("AI received data from game :", scene_info)
        #simplified_features = self.simplify_features(scene_info)
        state = self.simplify_features(scene_info)
        #state = tuple(simplified_features.values())  # Convert simplified features to tuple as the state
        
        total_reward = self.reward_scheme(scene_info)
        # Update Q Table
        if(self.epsilon >= 0.05):
            self.update_q_table(self.last_state, self.last_action, total_reward, state)

        q_values = {a: self.q_table.get((state, a), 0) for a in ["UP", "DOWN", "LEFT", "RIGHT"]}        
        if random.random() < self.epsilon: 
            actions = ["UP", "DOWN", "LEFT", "RIGHT"]
            action = random.sample(actions, 1)
        else:
            action = []
            action.append(max(q_values, key=q_values.get))

        #print("State:", state)
        #print("Total Reward:", total_reward)
        #print("Chosen Action:", action)      

        self.last_action = action[0]
        self.last_state = state        
        return action

    def reset(self):
        """
        Reset the status
        """
        #print("reset ml script")
        self.last_score = 0
        with open("model.pickle", 'wb') as f:
            pickle.dump(self.q_table, f)  

        if(self.epsilon >= 0.05):
            self.epsilon -= 0.0025
            print(self.epsilon)

        pass