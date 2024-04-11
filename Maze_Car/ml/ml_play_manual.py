import datetime
import os
import pickle
import pygame


class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.control_list = {"left_PWM": 0, "right_PWM": 0}
        # print("Initial ml script")
        self.status = None 

        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}
        self.record_list = []
        self.data = []

    def update(self, scene_info: dict, keyboard: list = [], *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        self.status = scene_info["status"]
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        
        self.data.append(scene_info)
        if pygame.K_w in keyboard or pygame.K_UP in keyboard:
            self.control_list["left_PWM"] = 40
            self.control_list["right_PWM"] = 40
            self.record_list.append("UP")
        elif pygame.K_a in keyboard or pygame.K_LEFT in keyboard:
            self.control_list["left_PWM"] = 20
            self.control_list["right_PWM"] = 60
            self.record_list.append("LEFT")
        elif pygame.K_d in keyboard or pygame.K_RIGHT in keyboard:
            self.control_list["left_PWM"] = 60
            self.control_list["right_PWM"] = 20
            self.record_list.append("RIGHT")
        elif pygame.K_s in keyboard or pygame.K_DOWN in keyboard:
            self.control_list["left_PWM"] = -40
            self.control_list["right_PWM"] = -40
            self.record_list.append("DOWN")
        else:
            self.control_list["left_PWM"] = 0
            self.control_list["right_PWM"] = 0
            self.record_list.append("NONE")

        #self.record_list.append(self.control_list)

        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        if self.status == "GAME_PASS":
            # Save game data to a pickle file
            filepath = "log/"
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            #filename = "record.pickle"
            filename = f"game_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pickle"
            with open(os.path.join(filepath, filename), "wb") as g:   
                pickle.dump({'data' : self.data, 'record' : self.record_list}, g)

        self.record_list = []
        self.data = []
        pass
