import os
import pickle
import random
import math

class MLPlay:

    def __init__(self, ai_name, *args, **kwargs):
        self.side = ai_name
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
            print("ok")

        self.bullet_x = 0
        self.bullet_y = 0
        self.last_bullets = []
        self.last_target = None

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

            if abs(w_diff_x) <= 12.5 and -50 <= w_diff_y <= 0:
                degree[6] = 1
            elif abs(w_diff_x) <= 12.5 and 0 <= w_diff_y <= 50.0:
                degree[2] = 1
            elif abs(w_diff_y) <= 12.5 and -50.0 <= w_diff_x <= 0:
                degree[4] = 1
            elif abs(w_diff_y) <= 12.5 and 0 <= w_diff_x <= 50.0:
                degree[0] = 1
            elif 0 <= w_diff_x <= 50 and 0 <= w_diff_y <= 50:
                degree[1] = 1
            elif 0 <= w_diff_x <= 50 and w_diff_y >= -50 and w_diff_y <= 0:
                degree[7] = 1
            elif w_diff_x >= -50 and 0 <= w_diff_y <= 50 and w_diff_x <= 0:
                degree[3] = 1
            elif w_diff_x >= -50 and w_diff_y >= -50 and w_diff_x <= 0 and w_diff_y <= 0:                
                degree[5] = 1

            if abs(w_diff_x) <= 14 and -80 <= w_diff_y <= 0:
                degree[14] = 1
            elif abs(w_diff_x) <= 14 and 0 <= w_diff_y <= 80.0:
                degree[10] = 1
            elif abs(w_diff_y) <= 14 and -80.0 <= w_diff_x <= 0:
                degree[12] = 1
            elif abs(w_diff_y) <= 14 and 0 <= w_diff_x <= 80.0:
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
                return (q_angle, q_dist, self.front, self.back, self.left, self.right)

    def check_bullet(self, scene_info):
        bullets = scene_info["bullets_info"]
        if bullets == []:
            self.last_bullets = bullets
            return False
        else:
            for bullet in bullets:
                # skip new bullets or disappear bullets
                if bullet not in self.last_bullets:
                    continue

                # calculate direction 
                last_bullet = self.last_bullets[self.last_bullets.index(bullet)]
                dx = bullet["x"] - last_bullet["x"]
                dy = bullet["y"] - last_bullet["y"]
                #direction = math.atan2(dy, dx) * 180 / math.pi

                ab_x = scene_info["x"] - bullet["x"]
                ab_y = scene_info["y"] - bullet["y"]

                if ab_x * dy == ab_y * dx and dx * ab_x > 0:
                    # check if there's a wall between
                    for wall in scene_info["walls_info"]:
                        if (min(bullet["x"], scene_info["x"]) < wall["x"] < max(bullet["x"], scene_info["x"]) and
                            min(bullet["y"], scene_info["y"]) < wall["y"] < max(bullet["y"], scene_info["y"])):
                            wc_x = scene_info["x"] - wall["x"]
                            wc_y = scene_info["y"] - wall["y"]
                            if abs(wc_x * dy - wc_y * dx) < 0.1:
                                return False
                    self.bullet_x = dx
                    self.bullet_y = dy
                    return True

            self.last_bullets = bullets
            return False

    def update(self, scene_info: dict, *args, **kwargs):
        if random.random() < 0.05:
            action = random.choice(["SHOOT", "FORWARD", "TURN_LEFT", "TURN_RIGHT",  "BACKWARD"])
            command = []
            command.append(action)
            return command           
        else:
            if scene_info["oil"] <= 30:
            #if scene_info["oil"] > 0:
                state = self.preprocess(scene_info, "oil")
                q_values = {a: self.q_table.get((state, a), 0) for a in ["FORWARD", "BACKWARD", "TURN_LEFT", "TURN_RIGHT"]}
                action = max(q_values, key=q_values.get)
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
                if self.check_bullet(scene_info):
                    car_angle = ((scene_info["angle"] + 180) % 360)
                    car_angle = (360 - car_angle) % 360         
                    angle = math.atan2(self.bullet_y, self.bullet_x) * 180 / math.pi
                    angle = int((angle + 360 ) % 360)
                    angle = int((angle - car_angle + 360) % 360  // 45)
                    if angle == 0 or angle == 1 or angle == 4 or  angle == 5:
                        action = "TURN_RIGHT"
                    elif angle == 3 or angle == 7:
                        action = "TURN_LEFT"
                    else:
                        action = "FORWARD"
                    command = []
                    command.append(action)
                    return command              
                else:
                    if scene_info["cooldown"] == 0:
                        # Comfirm Target
                        competitors = scene_info["competitor_info"]
                        competitors.sort(key=lambda x: x["oil"])
                        target = competitors[0]
                        if competitors[0]["oil"] < 30:
                            oil_stations = scene_info["oil_stations_info"]
                            oil_stations.sort(key=lambda x: abs(x["x"] - competitors[0]["x"]) + abs(x["y"] - competitors[0]["y"]))
                            target = oil_stations[0]

                        dx = target["x"] - scene_info["x"]
                        dy = target["y"] - scene_info["y"]
                        
                        angle_to_target = math.atan2(dy, dx) * 180 / math.pi
                        angle_to_target = (angle_to_target + 360) % 360
                        print(angle_to_target, end = " ")
                        # Adjust the gun angle to the target
                        gun_angle = ((scene_info["gun_angle"] + 180) % 360)
                        gun_angle = (360 - gun_angle) % 360
                        angle = (angle_to_target - gun_angle + 360) % 360
                        print(gun_angle)
                        print(angle)
                        if angle >= 320 or angle < 40:
                            action = "SHOOT"
                        else:
                            action = "AIM_LEFT"
                        #elif 22.5 <= angle < 180:
                        #    action = "AIM_LEFT"
                        #elif 180 <= angle < 337.5:
                        #    action = "AIM_RIGHT"

                        command = []
                        command.append(action)
                        return command    
                    else:
                        action = random.choice(["NONE", "NONE","NONE", "NONE", "NONE", "FORWARD", "TURN_LEFT", "TURN_RIGHT", "BACKWARD"])
                        command = []
                        command.append(action)
                        return command     

    def reset(self):
        self.last_score = 0
