"""
The template of the main script of the machine learning process
"""
import datetime
import os
import pickle
import pygame


class MLPlay:
    def __init__(self,ai_name, *args, **kwargs):
        """
        Constructor
        """
        self.ball_served = False
        self.data = []
        self.x = []

    def update(self, scene_info, keyboard=None, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        self.data.append(scene_info)
        # Make the caller to invoke `reset()` for the next round.
        if keyboard is None:
            keyboard = []
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            self.x.append("NONE")
            return "RESET"

        if pygame.K_q in keyboard:
            command = "SERVE_TO_LEFT"
            self.ball_served = True
        elif pygame.K_e in keyboard:
            command = "SERVE_TO_RIGHT"
            self.ball_served = True
        elif pygame.K_LEFT in keyboard or pygame.K_a in keyboard:
            command = "MOVE_LEFT"
        elif pygame.K_RIGHT in keyboard or pygame.K_d in keyboard:
            command = "MOVE_RIGHT"
        else:
            command = "NONE"
        self.x.append(command)
        return command

    def reset(self):
        """
        Reset the status
        """
        if self.data and (self.data[-1]["status"] == "GAME_PASS" or len(self.data[-1]["bricks"]) <= 3):
            # Save game data to a pickle file
            filepath = "log/"
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            #filename = "record.pickle"
            filename = f"game_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pickle"
            with open(os.path.join(filepath, filename), "wb") as f:   
                pickle.dump({'data': self.data, 'x': self.x}, f)

        self.ball_served = False
        self.data = []
        self.x = []
