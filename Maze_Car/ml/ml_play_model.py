import pickle

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        print(ai_name)
        self.model = self.load_model("multi_output_decision_tree_model.pickle")
        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}

    def load_model(self, filename):
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        return model

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        
        # Extract features from scene_info
        features = [scene_info["F_sensor"], scene_info["L_sensor"], scene_info["L_T_sensor"], scene_info["R_sensor"], scene_info["R_T_sensor"], scene_info["end_x"], scene_info["end_y"]]
        
        # Predict action using model
        predicted_actions = self.model.predict([features])[0]
        if predicted_actions == 0:
            self.control_list["left_PWM"] = 40
            self.control_list["right_PWM"] = 40
        elif predicted_actions == 1:
            self.control_list["left_PWM"] = -40
            self.control_list["right_PWM"] = -40
        elif predicted_actions == 2:
            self.control_list["left_PWM"] = 60
            self.control_list["right_PWM"] = 20
        elif predicted_actions == 3:
            self.control_list["left_PWM"] = 20
            self.control_list["right_PWM"] = 60
        elif predicted_actions == 4:
            self.control_list["left_PWM"] = -40
            self.control_list["right_PWM"] = -40

        #self.control_list["left_PWM"] = predicted_actions[0]
        #self.control_list["right_PWM"] = predicted_actions[1]
        #print(self.control_list["left_PWM"], end = " ")
        #print(self.control_list["right_PWM"])
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        pass
