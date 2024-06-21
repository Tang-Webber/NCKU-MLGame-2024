import os
import pickle
import random
import math

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor

        @param ai_name A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = ai_name
        print(f"Initial Game {ai_name} ml script")
        self.time = 0

        self.alpha = 0.07       # Learning rate
        self.gamma = 0.8         # Future Discount factor
        self.lambda_val = 1.1     # Reward_B Discount factor
        self.epsilon = 0.99     # Exploration rate

        self.last_score = 0
        self.last_action = ""
        self.action_to_index = {
            "FORWARD": 0,
            "BACKWARD" : 1,
            "TURN_LEFT" : 2,
            "TURN_RIGHT": 3
        }
        self.last_state = None

        self.last_distance = 1600
        self.current_distance = 0
        self.last_angle = 0
        self.current_angle = 0
        self.front = 0
        self.back = 0
        self.right = 0
        self.left = 0
        
        model_file = "resupply.pickle"
        
        if os.path.isfile(model_file):
            with open(model_file, 'rb') as f:
                self.q_table = pickle.load(f)
        else:
            self.q_table = {}
            for state0 in range(8):
                for state1 in range(8):
                    for state2 in range(3):
                        for state3 in range(3):   
                            for state4 in range(3):     
                                for state5 in range(3): 
                                    state = (state0, state1, state2, state3, state4, state5)
                                    for action in ["FORWARD", "TURN_LEFT", "TURN_RIGHT", "BACKWARD"]:
                                        self.q_table[(state, action)] = 0 
            self.q_table[(None, '')] = 0

    def preprocess(self, scene_info):
        # Get supply stations and car position
        supplies = scene_info["oil_stations_info"]
        car_x, car_y = scene_info["x"], scene_info["y"]

        distances = []
        for supply in supplies:
            diff_x = supply["x"] - car_x
            diff_y = supply["y"] - car_y
            distance = abs(diff_x) + abs(diff_y)
            distances.append((distance, diff_x, diff_y))

        # Sort supplies by distance and select the closest three
        sorted_supplies = sorted(distances)[:]

        #Choose the best destination 
        walls = scene_info["walls_info"]
        degree = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for wall in walls:
            #w_diff_x = (wall["x"]- 25) / 50 - int(car_x / 25) / 2
            #w_diff_y = (wall["y"]- 25) / 50 - int(car_y / 25) / 2

            w_diff_x = wall["x"] - car_x 
            w_diff_y = wall["y"] - car_y       
            #print(wall["x"]- 25 - car_x, wall["y"]- 25 - car_y)

            c_angle = int((scene_info["angle"] + 180) % 360)
            c_angle = ((360 - c_angle) % 360)

            if c_angle >= 337.5 or c_angle < 22.5:
                f_angle = 0
            elif c_angle >= 22.5 and c_angle < 67.5:
                f_angle = 1
            elif c_angle >= 67.5 and c_angle < 112.5:
                f_angle = 2
            elif c_angle >= 112.5 and c_angle < 157.5:
                f_angle = 3
            elif c_angle >= 157.5 and c_angle < 202.5:
                f_angle = 4
            elif c_angle >= 202.5 and c_angle < 247.5:
                f_angle = 5
            elif c_angle >= 247.5 and c_angle < 292.5:
                f_angle = 6
            elif c_angle >= 292.5 and c_angle < 337.5:
                f_angle = 7            

            #if abs(w_diff_x) <= 40 and abs(w_diff_y) <= 40:
            #    print(w_diff_x, w_diff_y)

            if abs(w_diff_x) <= 12.5 and -40 <= w_diff_y <= 0:
                degree[6] = 1
            elif abs(w_diff_x) <= 12.5 and 0 <= w_diff_y <= 40.0:
                degree[2] = 1
            elif abs(w_diff_y) <= 12.5 and -40.0 <= w_diff_x <= 0:
                degree[4] = 1
            elif abs(w_diff_y) <= 12.5 and 0 <= w_diff_x <= 40.0:
                degree[0] = 1
            elif 0 <= w_diff_x <= 40 and 0 <= w_diff_y <= 40:
                degree[1] = 1
            elif 0 <= w_diff_x <= 40 and w_diff_y >= -40 and w_diff_y <= 0:
                degree[7] = 1
            elif w_diff_x >= -40 and 0 <= w_diff_y <= 40 and w_diff_x <= 0:
                degree[3] = 1
            elif w_diff_x >= -40 and w_diff_y >= -40 and w_diff_x <= 0 and w_diff_y <= 0:                
                degree[5] = 1

            if abs(w_diff_x) <= 12.5 and -80 <= w_diff_y <= 0:
                degree[14] = 1
            elif abs(w_diff_x) <= 12.5 and 0 <= w_diff_y <= 80.0:
                degree[10] = 1
            elif abs(w_diff_y) <= 12.5 and -80.0 <= w_diff_x <= 0:
                degree[12] = 1
            elif abs(w_diff_y) <= 12.5 and 0 <= w_diff_x <= 80.0:
                degree[8] = 1
            elif 0 <= w_diff_x <= 80 and 0 <= w_diff_y <= 80:
                degree[9] = 1
            elif 0 <= w_diff_x <= 80 and w_diff_y >= -80 and w_diff_y <= 0:
                degree[15] = 1
            elif w_diff_x >= -80 and 0 <= w_diff_y <= 80 and w_diff_x <= 0:
                degree[11] = 1
            elif w_diff_x >= -80 and w_diff_y >= -80 and w_diff_x <= 0 and w_diff_y <= 0:                
                degree[13] = 1    
                            
        self.front = degree[f_angle] + degree[f_angle+ 8] 
        self.right = degree[(f_angle + 2) % 8] + degree[(f_angle + 2) % 8 + 8]
        self.back = degree[(f_angle + 4) % 8] + degree[(f_angle + 4) % 8 + 8]
        self.left = degree[(f_angle + 6) % 8] + degree[(f_angle + 6) % 8 + 8]

        #print(self.front, self.back, self.left, self.right)
        for supply in sorted_supplies:
            dist, diff_x, diff_y = supply
            supply_x = car_x + diff_x
            supply_y = car_y + diff_y

            car_angle = ((scene_info["angle"] + 180) % 360)
            car_angle = (360 - car_angle) % 360
            #print(scene_info["angle"], end = " ")
            #print(car_angle, end = " ")
            angle = math.atan2(diff_y, diff_x) * 180 / math.pi
            angle = int((angle + 360 ) % 360)
            #print(angle)
            angle = (angle - car_angle + 360) % 360
        
            #print(angle, end = " ")

            if angle >= 337.5 or angle < 22.5:
                q_angle = 0
            elif angle >= 22.5 and angle < 67.5:
                q_angle = 1
            elif angle >= 67.5 and angle < 112.5:
                q_angle = 2
            elif angle >= 112.5 and angle < 157.5:
                q_angle = 3
            elif angle >= 157.5 and angle < 202.5:
                q_angle = 4
            elif angle >= 202.5 and angle < 247.5:
                q_angle = 5
            elif angle >= 247.5 and angle < 292.5:
                q_angle = 6
            elif angle >= 292.5 and angle < 337.5:
                q_angle = 7

            #print(q_angle)

            if dist <= 50:
                q_dist = 0
            elif dist <= 100:
                q_dist = 1  
            elif dist <= 150:
                q_dist = 2  
            elif dist <= 200:
                q_dist = 3  
            elif dist <= 300:
                q_dist = 4  
            elif dist <= 400:
                q_dist = 5  
            elif dist <= 600:
                q_dist = 6  
            else:
                q_dist = 7  

            if (500 - car_x ) * (500 - supply_x) >= 0:
                self.current_distance = int(math.sqrt(diff_x**2 + diff_y**2))
                self.current_angle = q_angle
                return (q_angle, q_dist, self.front, self.back, self.left, self.right)

    def reward_scheme(self, scene_info, state):
        current_score = scene_info["oil"]
        reward_a = 0
        if current_score > self.last_score + 1:
            reward_a = 20
        
        reward_b = 0     
        if self.last_action == "TURN_LEFT" or self.last_action == "TURN_RIGHT":
            reward_b -= 1
            if self.current_angle % 4 == 2 and self.left == 0 and self.right == 0:
                reward_b -= 5
        elif self.last_action == "FORWARD":
            if self.current_angle > 6 or self.current_angle < 2 :
                reward_b += 6               
            else:
                reward_b -= 6                   
        elif self.last_action == "BACKWARD":
            if 3 <= self.current_angle <= 5 :
                reward_b += 6               
            else:
                reward_b -= 6   
        
        if self.front >= 1:
            if self.last_action == "FORWARD":
                reward_b -= 4 * self.front
            elif self.last_action == "TURN_LEFT":
                reward_b += 3 * self.front
            #else:
            #    reward_b += 2
        if self.back >= 1:
            if self.last_action == "BACKWARD":
                reward_b -= 4 * self.back
            elif self.last_action == "TURN_RIGHT":
                reward_b += 3 * self.back
            #else:
            #    reward_b += 2 
        if self.left >= 1:
            if self.last_action == "FORWARD":
                reward_b += 4 * self.left
            elif self.last_action == "TURN_LEFT":
                reward_b -= 3 * self.right
            #else:
            #    reward_b += 4
        if self.right >= 1:
            if self.last_action == "FORWARD":
                reward_b += 4 * self.right
            elif self.last_action == "TURN_RIGHT":
                reward_b -= 3 * self.right
            #else:
            #    reward_b += 4

        #if scene_info["x"] > 930 or scene_info["x"] < 80 or scene_info["y"] > 530 or scene_info["y"] < 80:
        #    reward_b -= 5
        #print(scene_info["x"])
        total_reward = round(reward_a + self.lambda_val * reward_b, 2)
        self.last_score = current_score

        return total_reward

    def update_q_table(self, state, action, reward, next_state):
        current_q_value = self.q_table[(state, action)]
        max_next_q_value = max([self.q_table.get((next_state, a), 0) for a in ["FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"]])
        new_q_value = round((1 - self.alpha) * current_q_value + self.alpha * (reward + self.gamma * max_next_q_value), 2)
        self.q_table[(state, action)] = new_q_value
        print(state, action, reward, self.q_table[(state, action)])
        #print([self.q_table.get((next_state, a), 0) for a in ["FORWARD",  "TURN_LEFT", "TURN_RIGHT"]])
    def update(self, scene_info: dict, *args, **kwargs):
        state = self.preprocess(scene_info)
        #print(state)
        total_reward = self.reward_scheme(scene_info, state)

        if self.epsilon >= 0.05:
            self.update_q_table(self.last_state, self.last_action, total_reward, state)
        q_values = {a: self.q_table.get((state, a), 0) for a in ["FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"]}
        
        if random.random() < self.epsilon:
            action = random.choice(["FORWARD", "FORWARD", "FORWARD", "FORWARD", "TURN_LEFT", "TURN_RIGHT", "TURN_LEFT", "TURN_RIGHT", "BACKWARD"])
            #action = random.choice(["TURN_RIGHT"])
        else:
            action = max(q_values, key=q_values.get)
        command = []
        command.append(action)

        self.last_action = action
        self.last_state = state
        self.last_distance = self.current_distance
        self.last_angle = self.current_angle
        return command

    def reset(self):
        self.last_score = 0
        with open("resupply.pickle", 'wb') as f:
            pickle.dump(self.q_table, f)

        if self.epsilon >= 0.05:
            self.epsilon -= 0.008
        print(self.epsilon)
