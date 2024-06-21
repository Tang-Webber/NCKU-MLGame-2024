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

        self.last_score = 0
        self.last_action = ""
        self.action_to_index = {
            "FORWARD": 0,
            "BACKWARD" : 1,
            "TURN_LEFT" : 2,
            "TURN_RIGHT": 3
        }
        self.last_state = None

        self.front = 0
        self.back = 0
        self.right = 0
        self.left = 0
        
        resupply_file = "resupply.pickle"
        if os.path.isfile(resupply_file):
            with open(resupply_file, 'rb') as f:
                self.q_table = pickle.load(f)

    def preprocess(self, scene_info, x):
        # Get supply stations and car position
        if x == "oil":
            supplies = scene_info["oil_stations_info"]
        elif x == "bullet":
            supplies = scene_info["bullet_stations_info"]

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
        self.front = 0
        self.back = 0
        self.right = 0
        self.left = 0
        for wall in walls:
            """
            w_diff_x = wall["x"] - car_x
            w_diff_y = wall["y"] - car_y
            w_dist = math.sqrt(w_diff_x**2 + w_diff_y**2)
            w_angle = int(math.atan2(w_diff_y, w_diff_x) * 180 / math.pi)

            
            r_angle = (w_angle - c_angle + 360) % 360
            """
            w_diff_x = (wall["x"]- 25) / 50 - int(car_x / 25) / 2
            w_diff_y = (wall["y"]- 25) / 50 - int(car_y / 25) / 2
            c_angle = int((scene_info["angle"] + 180) % 360)
            c_angle = (360 - c_angle) % 360

            degree_0 = 0
            degree_45 = 0
            degree_90 = 0
            degree_135 = 0
            degree_180 = 0
            degree_225 = 0
            degree_270 = 0
            degree_315 = 0
            if abs(w_diff_x) <= 1.0 and abs(w_diff_y) <= 1.0:
                print(wall["x"], car_x)
                print(wall["y"] , car_y)
                print(w_diff_x, w_diff_y)
            if w_diff_x == 0 and -1.0 <= w_diff_y <= 0:
                print("上", end = " ")#up
                degree_270 = 1
            elif w_diff_x == 0 and 0 <= w_diff_y <= 1.0:
                print("下", end = " ")#down
                degree_90 = 1
            elif w_diff_y == 0 and -1.0 <= w_diff_x <= 0:
                print("左", end = " ")#left
                degree_180 = 1
            elif w_diff_y == 0 and 0 <= w_diff_x <= 1.0:
                print("右", end = " ")#right
                degree_0 = 1
            elif w_diff_x == 0.5 and w_diff_y == 0.5:
                print("右下", end = " ")
                degree_45 = 1
            elif w_diff_x == 0.5 and w_diff_y == -0.5:
                print("右上", end = " ")
                degree_315 = 1
            elif w_diff_x == -0.5 and w_diff_y == 0.5:
                print("左下", end = " ")
                degree_135 = 1
            elif w_diff_x == -0.5 and w_diff_y == -0.5:
                print("左上", end = " ")
                degree_225 = 1
                

            """
            if w_dist <= 35:
                
                if r_angle <= 30 or r_angle >= 330:
                    self.front = 1
                elif 150 <= r_angle <= 210:
                    self.back = 1
                if 60 <= r_angle <= 120:
                    self.right = 1
                elif 240 <= r_angle <= 300:
                    self.left = 1
            """
        self.front = self.back = self.left = self.right = 0

        for supply in sorted_supplies:
            dist, diff_x, diff_y = supply
            supply_x = car_x + diff_x

            car_angle = ((scene_info["angle"] + 180) % 360)
            car_angle = (360 - car_angle) % 360
            angle = math.atan2(diff_y, diff_x) * 180 / math.pi
            angle = int((angle + 360 ) % 360)
            angle = (angle - car_angle + 360) % 360

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
                #print(q_angle)
                return (q_angle, q_dist, self.front, self.back, self.left, self.right)
            
    def update(self, scene_info: dict, *args, **kwargs):

        #if scene_info["oil"] <= 30:
        if scene_info["oil"] >0:
            state = self.preprocess(scene_info, "oil")
            q_values = {a: self.q_table.get((state, a), 0) for a in ["FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"]}
            #print(q_values)
            action = max(q_values, key=q_values.get)
            #print(action)
            command = []
            command.append(action)
            return command
        elif scene_info["power"] <= 4:
            state = self.preprocess(scene_info, "bullet")
            q_values = {a: self.q_table.get((state, a), 0) for a in ["FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"]}
            action = max(q_values, key=q_values.get)
            command = []
            command.append(action)
            return command        
        else:
            #shoooooot!
            print("")    

    def reset(self):
        self.last_score = 0
