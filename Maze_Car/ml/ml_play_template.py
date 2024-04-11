import datetime
import os
import pickle


class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.l_t_sensor_value = 0
        self.r_t_sensor_value = 0

        self.status = None 

        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}
        self.record_list = []
        #self.f_sensor_list = []
        #self.l_sensor_list = []
        #self.r_sensor_list = []
        #self.l_t_sensor_list = []
        #self.r_t_sensor_list = []
        #self.end_x = []
        #self.end_y = []
        self.data = []


    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        
        self.status = scene_info["status"]
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        self.data.append(scene_info)
        self.r_sensor_value = scene_info["R_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.f_sensor_value = scene_info["F_sensor"]
        self.l_t_sensor_value = scene_info["L_T_sensor"]
        self.r_t_sensor_value = scene_info["R_T_sensor"]

        if self.f_sensor_value < 5:
            self.control_list["left_PWM"] = -100
            self.control_list["right_PWM"] = -100
        elif self.l_sensor_value < 5 and self.r_sensor_value < 5:
            self.control_list["left_PWM"] = 100
            self.control_list["right_PWM"] = 100
        elif self.r_sensor_value > self.f_sensor_value and self.r_sensor_value > self.l_sensor_value and self.r_sensor_value > self.r_t_sensor_value and self.r_sensor_value > self.l_t_sensor_value:
            self.control_list["left_PWM"] = 50
            self.control_list["right_PWM"] = -100
        elif self.r_t_sensor_value > self.f_sensor_value and self.r_t_sensor_value > self.l_sensor_value and self.r_t_sensor_value > self.r_sensor_value and self.r_t_sensor_value > self.l_t_sensor_value:
            self.control_list["left_PWM"] = 100
            self.control_list["right_PWM"] = 50
        elif self.l_sensor_value > self.f_sensor_value and self.l_sensor_value > self.r_sensor_value and self.l_sensor_value > self.r_t_sensor_value and self.l_sensor_value > self.l_t_sensor_value:
            self.control_list["left_PWM"] = -200
            self.control_list["right_PWM"] = 200
        elif self.l_t_sensor_value > self.f_sensor_value and self.l_t_sensor_value > self.l_sensor_value and self.l_t_sensor_value > self.r_t_sensor_value and self.l_t_sensor_value > self.r_sensor_value:
            self.control_list["left_PWM"] = 100
            self.control_list["right_PWM"] = 200
        else: 
            self.control_list["left_PWM"] = 100
            self.control_list["right_PWM"] = 100
        self.record_list.append(self.control_list)
        #self.f_sensor_list.append(self.f_sensor_value)
        #self.l_sensor_list.append(self.l_sensor_value)
        #self.r_sensor_list.append(self.r_sensor_value)
        #self.l_t_sensor_list.append(self.l_t_sensor_value)
        #self.r_t_sensor_list.append(self.r_t_sensor_value)
        #self.end_x.append(scene_info["end_x"])
        #self.end_y.append(scene_info["end_y"])
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        # print("reset ml script")
        if self.status == "GAME_PASS":
            # Save game data to a pickle file
            filepath = "log/"
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            #filename = "record.pickle"
            filename = f"game_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pickle"
            with open(os.path.join(filepath, filename), "wb") as g:   
                pickle.dump({'data' : self.data, 'record' : self.record_list}, g)

        #self.f_sensor_list = []
        #self.l_sensor_list = []
        #self.r_sensor_list = []
        #self.l_t_sensor_list = []
        #self.r_t_sensor_list = []
        self.record_list = []
        self.data = []
        #self.end_y = []
        #self.end_x = []
        pass
