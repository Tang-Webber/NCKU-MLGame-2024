"""
The template of the main script of the machine learning process
"""
import random
import pygame

from src.env import IS_DEBUG
import pygame
from typing import List, Literal
import pickle
from dataclasses import dataclass
import numpy as np
import random
import math
import random
import os

MY_NAME = "Tank_3"

INF = 1e9
READ_QTABLE = False
SAVE_QTABLE = False
UPDATE_QTABLE = False
FROM_ALGORITHM = False
FROM_QTABLE = False
TOTAL_TRAINING_TIMES = 0

GX = [-8, -6, 0, 8, 6, 8, 0, -8]
GY = [0, 6, 8, 8, 0, -8, -6, -8]

@dataclass
class Player:
    id: str
    x: int
    y: int
    speed: int
    score: int
    power: int
    oil: int
    lives: int
    angle: int
    gun_angle: int
    cooldown: int
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        speed: int,
        score: int,
        power: int,
        oil: int,
        lives: int,
        angle: int,
        gun_angle: int,
        cooldown: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.score = score
        self.power = power
        self.oil = oil
        self.lives = lives
        self.angle = angle
        self.gun_angle = gun_angle
        self.cooldown = cooldown

class Wall:
    id: str
    x: int
    y: int
    lives: int
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        lives: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.lives = lives

class Bullet:
    id: str
    x: int
    y: int
    speed: int
    rot: int
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        speed: int,
        rot: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.rot = rot

class BulletStt:
    id: str
    x: int
    y: int
    power: int
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        power: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.power = power

class Oil_Stt:
    id: str
    x: int
    y: int
    power: int
    def __init__(
        self,
        id: str,
        x: int,
        y: int,
        power: int
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.power = power

class Qtable:
    table: np.array
    def __init__(self):
        self.table = np.zeros((8, 4, 4, 4, 4, 4), dtype=np.float32)
        if(not READ_QTABLE):
           return
        try:
            self.read()
        except:
            pass
    def confine(self, x, l, r):
        x = max(x, l)
        x = min(x, r)
        return x
    def get_table(self, state: tuple) -> list[int]:
        if(not READ_QTABLE):
           return
        a, x, y, z, w = state
        a = self.confine(a, 0, 7)
        x = self.confine(x, 0, 3)
        y = self.confine(y, 0, 3)
        z = self.confine(z, 0, 3)
        w = self.confine(w, 0, 3)
        qs = self.table[a][x][y][z][w].tolist()
        return qs
    def get_value(self, state: tuple, action: int) -> int:
        qs = self.get_table(state)
        value = qs[action]
        return value
    def get_max_value(self, state: tuple) -> float:
        qs = self.get_table(state)
        max_value = max(qs)
        return max_value
    def get_best_aciton(self, state: tuple) -> int:
        # print(state)
        qs = self.get_table(state)
        best_actions = []
        for i in range(0,4):
            if(qs[i] == max(qs)):
                best_actions.append(i)
        idx = best_actions[random.randint(0,len(best_actions)-1)]
        return idx
    def set_value(self, state: tuple, action: int, value):
        a, x, y, z, w = state
        a = self.confine(a, 0, 1)
        x = self.confine(x, 0, 3)
        y = self.confine(y, 0, 3)
        z = self.confine(z, 0, 3)
        w = self.confine(w, 0, 3)
        self.table[a][x][y][z][w][action] = value
        return
    def update(self, last_state, state, action, reward, learing_rate, gamma):
        if(not UPDATE_QTABLE):
            return
        learned_value = reward + gamma * self.get_max_value(state)
        Q_old_value = self.get_value(last_state, action)
        Q_new_value = (1 - learing_rate) * Q_old_value + learing_rate * learned_value
        self.set_value(last_state, action, Q_new_value)
        return
    def read(self):
        folder_path = MY_NAME
        if not os.path.isdir(folder_path): os.mkdir(folder_path)        # 如果不存在這個路徑則建立資料夾
        file_path = os.path.join(folder_path,"qtable.npy")
        self.table = np.load(file_path)
        return
    def save(self,name):
        if(not SAVE_QTABLE):
            return
        folder_path = MY_NAME
        if not os.path.isdir(folder_path): os.mkdir(folder_path)        # 如果不存在這個路徑則建立資料夾
        file_path = os.path.join(folder_path,name+".npy")
        np.save(file_path, self.table)
        return

class MLPlay:
    state: tuple        #我的state
    times: int          #現在的訓練次數

    def __init__(self, ai_name, *args, **kwargs):
        self.side = ai_name
        print(f"Initial Game {ai_name} ml script")
        self.time = 0
        self.qtable = Qtable()
        self.newqtable = Qtable()
        self.action = List[Player]
        self.state = List[Player]
        self.score = List[int]

        self.id: str
        self.frame: int
        self.myInfo: Player
        self.teammate_info: tuple[Player]
        self.competitor_info: tuple[Player]
        walls: tuple[Wall]
        bullets: tuple[Bullet]
        bulletStts: tuple[BulletStt]
        oil_Stts: tuple[Oil_Stt]

    def myInfo(self):
        for i in range(0,len(self.teammate_info)):
            if(self.teammate_info[i]['id'] == self.id):
                return self.teammate_info[i]

    def getDis(pos1, pos2):
        return math.sqrt((pos1['x']-pos2['x'])**2 + (pos1['y']-pos2['y'])**2)
    
    def getDeg(pos1, pos2):
        myx = pos1['x']
        myy = pos1['y']
        targetx = pos2['x']
        targety = pos2['y']
        rex = abs(targetx-myx)
        rey = abs(targety-myy)
        deg = (rex*(1.0))/(((rex**2)+(rey**2))**(0.5))
        deg = math.acos(deg)
        deg = math.degrees(deg)
        if(targetx <= myx and targety>=myy):
            deg=deg
        elif(targetx >= myx and targety >= myy):
            deg=180-deg
        elif(targetx >= myx and targety <= myy):
            deg+=180
        elif(targetx <= myx and targety <= myy):
            deg=360-deg
        deg_num=0
        if(deg>337.5 or deg<22.5):
            deg_num=0
        if(deg>=22.5 and deg<67.5):
            deg_num=1
        if(deg>=67.5 and deg<112.5):
            deg_num=2
        if(deg>=112.5 and deg<157.5):
            deg_num=3
        if(deg>=157.5 and deg<202.5):
            deg_num=4
        if(deg>=202.5 and deg<247.5):
            deg_num=5
        if(deg>=247.5 and deg<292.5):
            deg_num=6
        if(deg>=292.5 and deg<337.5):
            deg_num=7
        return deg_num

    def getMinTarget(self, targets):
        if(len(targets) == 0):
            return None
        bestTarget = targets[0]
        for target in targets:
            if(target['id'] == self.id):
                continue
            if(MLPlay.getDis(self.myInfo, target) < MLPlay.getDis(self.myInfo, bestTarget)):
                bestTarget = target
        return bestTarget
    
    def tWall(self):
        newx = self.myInfo['x'] + GX[(int)(self.myInfo['angle']/45)]
        newy = self.myInfo['y'] + GY[(int)(self.myInfo['angle']/45)]
        newpos = {
            'x': newx,
            'y': newy
        }
        mindis = INF
        for wall in self.walls:
            if(MLPlay.getDis(newpos, wall) < mindis):
                mindis = MLPlay.getDis(newpos, wall)

        print("minDis = ", mindis)
        return mindis
            

    def move(self, target):
        targetDeg = MLPlay.getDeg(self.myInfo, target)
        while((self.myInfo['angle']/45) != targetDeg):
            dif = (self.myInfo['angle']/45 - targetDeg + 8) % 8
            if(dif < 4):
                return 1
            else:
                return 2
        if(self.myInfo['power'] !=0 and (((int)((int)(self.myInfo['angle']/45)%2 == 0) and (MLPlay.tWall(self)) < 25) or ((int)((int)(self.myInfo['angle']/45)%2 == 1) and (MLPlay.tWall(self) < 25)))):
            # newx = self.myInfo['x'] + GX[(int)(self.myInfo['angle']/45)]
            # newy = self.myInfo['y'] + GY[(int)(self.myInfo['angle']/45)]
            # newpos = {
            #     'x': newx,
            #     'y': newy
            # }
            return MLPlay.attack(self, self.minWall)
        return 3

    def attack(self, target):
        targetDeg = MLPlay.getDeg(self.myInfo, target)
        while((self.myInfo['gun_angle']/45) != targetDeg):
            dif = (self.myInfo['gun_angle']/45 - targetDeg + 8) % 8
            if(dif < 4):
                return 5
            else:
                return 6
        return 7
    
    def attackOk(self, target):
        difx = abs(self.myInfo['x'] - target['x'])
        dify = abs(self.myInfo['y'] - target['y'])
        if(difx < 25):
            return 1
        if(dify < 25):
            return 1
        if(abs(difx - dify) < 25):
            return 1
        return 0

    #子彈30射程300 坦克6
    def update(self, scene_info: dict, keyboard=[], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        
        # print(keyboard)
        self.id = scene_info["id"]
        self.frame = scene_info["used_frame"]
        self.teammate_info = scene_info["teammate_info"]
        self.competitor_info = scene_info["competitor_info"]
        self.walls = scene_info["walls_info"]
        self.bullets = scene_info["bullets_info"]
        self.bulletStts = scene_info["bullet_stations_info"]
        self.oil_Stts = scene_info["oil_stations_info"]
        self.myInfo = MLPlay.myInfo(self)
        print("myinfo = " , self.myInfo)

        if(self.frame > 0):
            self.qtable.update(self.myInfo, self.myInfo, self.action, self.score, 0.9, 0.4)

        self.minCompetitor: Player = MLPlay.getMinTarget(self, self.competitor_info)
        self.minWall: Wall = MLPlay.getMinTarget(self, self.walls)
        self.minBuillet: Bullet = MLPlay.getMinTarget(self, self.bullets)
        self.minBuilletStt: BulletStt = MLPlay.getMinTarget(self, self.bulletStts)
        self.minoil_Stts: Oil_Stt = MLPlay.getMinTarget(self, self.oil_Stts)
        
        move_act = 0
        if(random.random() > -1):
            if(self.myInfo['power'] == 0):
                print("move")
                move_act = MLPlay.move(self, self.minBuilletStt)
            elif(MLPlay.getDis(self.myInfo, self.minCompetitor) < 200 and MLPlay.attackOk(self, self.minCompetitor)):
                print("attackCompetitor")
                move_act = MLPlay.attack(self, self.minCompetitor)
            elif(self.myInfo['power'] < 7):
                print("move")
                move_act = MLPlay.move(self, self.minBuilletStt)
            else:
                move_act = MLPlay.attack(self, self.minWall)
                print("attackWall")
        else:
            move_act = self.qtable.get_value(self.myInfo)

        shoot_cd = random.randrange(15, 31)

        is_shoot = 0
        if scene_info["used_frame"] % shoot_cd == 0:
            is_shoot = random.randrange(2)

        if(random.random() > 0.95):
            move_act = random.randrange(1, 7)
        command = []
        if move_act == 1:
            command.append("TURN_RIGHT")
        elif move_act == 2:
            command.append("TURN_LEFT")
        elif move_act == 3:
            command.append("FORWARD")
        elif move_act == 4:
            command.append("BACKWARD")

        if move_act == 5:
            command.append("AIM_RIGHT")
        elif move_act == 6:
            command.append("AIM_LEFT")

        if move_act == 7:
            command.append("SHOOT")
        if(random.random() > 0.95):
            command.append("SHOOT")
        if not command:
            command.append("NONE")
        print("command = ", command)
        print()
        return command

    def reset(self):
        """
        Reset the status
        """
        print(f"reset Game {self.side}")