"""
The template of the main script of the machine learning process
"""
import random
import pygame
import math, pickle, os, numpy

from src.env import IS_DEBUG


class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        self.side = ai_name
        self.time = 0

        self.reward = 0
        self.prev_qvalues = []
        self.prev_action = 0
        self.prev_target = []
        self.c_target_t = ""
        self.c_target = []

        self.sum = []
        self.playtotal = 20
        self.playcount = 1
        self.qtable_move = numpy.zeros((8, 8, 4)) # target direction(8), current angle(8), output(4) 
        filepath = "log/"
        filename = "qtable20.pickle"
        filename = os.path.join(filepath, filename)
        with open(filename, "rb") as f:   
            print(os.path.abspath(filename))
            self.qtable = pickle.load(f)
            print(os.path.join(filepath, filename))

    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        if scene_info["status"] != "GAME_ALIVE":
            # print(scene_info)
            return "RESET"
        degree = (scene_info["angle"] + 180) % 360
        degree_tankG = (scene_info["gun_angle"] + 180) % 360
        command = []
        objective, objective_t = self.find_objective(scene_info)
        target, target_t = self.find_target(scene_info)

        if target_t == "wall":
            aim_range = 300
        elif target_t == "foe":
            aim_range = 320

        # tank_gun_adjustment = self.angle_adjust(scene_info, target, degree_tankG)
        
        if target[0] == scene_info["x"]:
            target_angle = 360 - degree_tankG if target[1] < scene_info["y"] else (540 - degree_tankG) % 360
        else:
            target_angle = (math.degrees(math.atan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) - degree_tankG + 360) % 360
        if 180 >= target_angle > 22.5:
            tank_gun_adjustment = "LEFT"
        elif 337.5 > target_angle >= 180 :
            tank_gun_adjustment = "RIGHT"
        elif 22.5 >= target_angle >= 0 or 360 >= target_angle >= 337.5 :
            tank_gun_adjustment = "Perfect?"

        if objective_t == "ammo" or objective_t == "gas":
            if objective[0] == scene_info["x"]:
                relative_angle = 0 if objective[1] < scene_info["y"] else 180
            else:
                relative_angle = (math.degrees(math.atan((objective[1] - scene_info["y"]) / (objective[0] - scene_info["x"]))) + 360) % 360 
            qvalues = self.qtable_move[int(relative_angle % 360 / 45)]
            qvalues = qvalues[int(degree % 360 / 45)]
            action = self.get_action(qvalues)
            command.append(action)
            if len(self.prev_qvalues) != 0:
                self.prev_qvalues[self.prev_action] = 0.9 * self.prev_qvalues[self.prev_action] + 0.1 * (1 * self.reward + 0 * numpy.max(qvalues))
            self.reward = self.calculate_reward(scene_info, objective, action, degree)
            self.prev_action = self.action_to_index(action)
            self.prev_qvalues = qvalues
        elif self.get_dist(target, [scene_info["x"], scene_info["y"]]) <= aim_range and tank_gun_adjustment != "Perfect?":
            command.append("AIM_" + tank_gun_adjustment)
        elif scene_info["cooldown"] == 0 and self.get_dist(target, [scene_info["x"], scene_info["y"]]) <= aim_range - 40 and \
              tank_gun_adjustment == "Perfect?" and self.not_on_path(scene_info, degree_tankG):
            command.append("SHOOT")
        elif objective_t == "charge":
            if objective[0] == scene_info["x"]:
                relative_angle = 0 if objective[1] < scene_info["y"] else 180
            else:
                relative_angle = (math.degrees(math.atan((objective[1] - scene_info["y"]) / (objective[0] - scene_info["x"]))) + 360) % 360 
            qvalues = self.qtable_move[int(relative_angle % 360 / 45)]
            qvalues = qvalues[int(degree % 360 / 45)]
            action = self.get_action(qvalues)
            command.append(action)
            if len(self.prev_qvalues) != 0:
                self.prev_qvalues[self.prev_action] = 0.8 * self.prev_qvalues[self.prev_action] + 0.2 * (self.reward + 0.4 * numpy.max(qvalues))
            self.reward = self.calculate_reward(scene_info, objective, action, degree)
            self.prev_action = self.action_to_index(action)
            self.prev_qvalues = qvalues
        else:
            if target[0] == scene_info["x"]:
                relative_angle = 0 if target[1] < scene_info["y"] else 180
            else:
                relative_angle = (math.degrees(math.atan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360 
            qvalues = self.qtable_move[int(relative_angle % 360 / 45)]
            qvalues = qvalues[int(degree / 45)]
            action = self.get_action(qvalues)
            command.append(action)
            if len(self.prev_qvalues) != 0:
                self.prev_qvalues[self.prev_action] = 0.8 * self.prev_qvalues[self.prev_action] + 0.2 * (self.reward + 0.4 * numpy.max(qvalues))
            self.reward = self.calculate_reward(scene_info, target, action, degree)
            self.prev_action = self.action_to_index(action)
            self.prev_qvalues = qvalues

        if not command:
            command.append("NONE")
        
        return command

    def reset(self):
        self.playcount += 1
        if(self.playcount > self.playtotal):
            filepath = "log/"
            filename = "qtable" + str(self.playtotal) + ".pickle"
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            with open(os.path.join(filepath, filename), "wb") as f:   
                pickle.dump(self.qtable_move, f)    # 將savefile.pickle存至./log/中

    def find_objective(self, scene_info):
        self_x = scene_info["x"]
        self_y = scene_info["y"]
        if scene_info["oil"] < 40:
            a = self.find_least_dist(self_x, self_y, scene_info["oil_stations_info"])
            return a, "gas"
        elif scene_info["power"] == 0:
            a = self.find_least_dist(self_x, self_y, scene_info["bullet_stations_info"])
            return a, "ammo"
        else:
            nearest_foe = self.find_least_dist(self_x, self_y, scene_info["competitor_info"])
            if self.get_dist(nearest_foe, [self_x, self_y]) > 350:
                return nearest_foe, "charge"
            else:
                return nearest_foe, "retreat"

    def get_action(self, qvalues):
        n = 0
        identical = []
        if random.randint(1, 40) > 39:
            n = random.randint(0, 3)
        else:
            n = numpy.argmax(qvalues)
            for i in range(4):
                if qvalues[i] == qvalues[n]:
                    identical.append(i)
            if len(identical) > 1:
                n = identical[random.randint(0, len(identical) - 1 > 0)]
        if n == 0:
            return "FORWARD"
        elif n == 1:
            return "BACKWARD"
        elif n == 2:
            return "TURN_RIGHT"
        elif n == 3 :
            return "TURN_LEFT"
        else:
            return "NONE"   
    def action_to_index(self, action):
        if action == "FORWARD":
            return 0
        elif action == "BACKWARD":
            return 1
        elif action == "TURN_RIGHT":
            return 2
        elif action == "TURN_LEFT":
            return 3
        else:
            return 4
    def calculate_reward(self, scene_info, objective, action, current_degree):
        if action == "FORWARD":
            if (objective[1] - scene_info["y"] > 0 and 180 >= current_degree >= 0) or \
            (objective[1] - scene_info["y"] <= 0 and 360 >= current_degree >= 180) or \
            (objective[0] - scene_info["x"] > 0 and (90 >= current_degree >= 0 or 360 >= current_degree >= 270)) or \
            (objective[0] - scene_info["x"] <= 0 and 270 >= current_degree >= 90):
                return 1
            else:
                return -1
        elif action == "BACKWARD":
            if (objective[1] - scene_info["y"] > 0 and 360 >= current_degree >= 180) or \
            (objective[1] - scene_info["y"] <= 0 and 180 >= current_degree >= 0) or \
            (objective[0] - scene_info["x"] > 0 and 270 >= current_degree >= 90) or \
            (objective[0] - scene_info["x"] <= 0 and (90 >= current_degree >= 0 or 360 >= current_degree >= 270)):
                return 1 
            else:
                return -1
        if scene_info["x"] + 10 > objective[0] > scene_info["x"] - 10:
                return -1
        relative_angle = (math.degrees(math.atan((objective[1] - scene_info["y"]) / (objective[0] - scene_info["x"]))) - current_degree + 360) % 360
        if action == "TURN_LEFT":
            return 1 if 90 >= relative_angle >= 22.5 or 270 >= relative_angle > 202.5 else -1
        elif action == "TURN_RIGHT":
            return 1 if 157.5 >= relative_angle >= 90 or 337.5 >= relative_angle >= 270 else -1
        return -1


    def find_target(self, scene_info):
        self_x = scene_info["x"]
        self_y = scene_info["y"]
        nearest_foe = self.find_least_dist(self_x, self_y, scene_info["competitor_info"])
        if self.get_dist(nearest_foe, [self_x, self_y]) < 400:
            return nearest_foe, "foe"
        else:
            nearest_wall = self.find_least_dist(self_x, self_y, scene_info["walls_info"])
            return nearest_wall, "wall"

    def find_least_dist(self, self_x, self_y, dictionary):
        least = [dictionary[0]["x"], dictionary[0]["y"]]
        least_d = self.get_dist([dictionary[0]["x"], dictionary[0]["y"]], [self_x, self_y])
        for obj in dictionary:
            dist = self.get_dist([obj["x"], obj["y"]], [self_x, self_y])
            if dist < least_d:
                least_d = dist
                least = [obj["x"], obj["y"]]
        return least
    
    def get_dist(self, coordinate, self_coor):
        x = coordinate[0] - self_coor[0]
        y = coordinate[1] - self_coor[1]
        return (x ** 2 + y ** 2) ** 0.5
    
    def angle_adjust(self, scene_info, target, current_degree):
        if target[0] != 0 and target[1] != 0:
            if scene_info["x"] == target[0] :
                if target[1] > scene_info["y"]: # 180 degrees -> at left
                    if 360 > current_degree > 206.5:
                        return "RIGHT"
                    elif 0 <= current_degree < 156.5:
                        return "LEFT"
                else:
                    if 180 > current_degree > 23.5:
                        return "RIGHT"
                    elif 180 < current_degree < 336.5:
                        return "LEFT"
            elif current_degree == 0:
                if 22.5 > (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360 or \
                337.5 < (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360:
                    a = 1
                else:    
                    if (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360 <= 180:
                        return "LEFT"
                    else:
                        return "RIGHT"
            elif not current_degree + 22.5 > (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360  > current_degree - 22.5:
                if current_degree + 22.5 < (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360 :
                    return "LEFT"
                elif (math.degrees(math.tan((target[1] - scene_info["y"]) / (target[0] - scene_info["x"]))) + 360) % 360 < current_degree - 22.5:
                    return "RIGHT"
        return "Perfect?"
    
    def not_on_path(self, scene_info, degree_tankG):
        for ally in scene_info["teammate_info"]:
            if scene_info["id"] == ally["id"]:
                continue
            if 20 > ally["y"] - scene_info["y"] - math.tan(degree_tankG) * (scene_info["x"] - ally["x"]) > -20:
                return False
        return True
            
