import datetime
import os
import pickle

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        print(ai_name)
        self.ball_served = False
        self.prev_ball_pos = None
        self.direction = None
        self.deltaX = None
        self.deltaY = None

        self.data = []
        self.x = []
        self.count = 10

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        self.data.append(scene_info)
        # Make the caller to invoke `reset()` for the next round.
        if scene_info["status"] == "GAME_OVER" or scene_info["status"] == "GAME_PASS":
            self.x.append("NONE")
            return "RESET"
        
        ball_pos = scene_info["ball"]
        platform_pos = scene_info["platform"]

        if not self.ball_served:
            #if self.count != 0:
            #    self.count -= 1
            #    self.x.append("MOVE_RIGHT")
            #    return "MOVE_LEFT"
            #else:
                self.ball_served = True
                self.prev_ball_pos = ball_pos
                self.x.append("NONE")
                return "SERVE_TO_LEFT"

        # Calculate direction and speed of the ball
        if self.prev_ball_pos is not None:
            self.deltaX = ball_pos[0] - self.prev_ball_pos[0]
            self.deltaY = ball_pos[1] - self.prev_ball_pos[1]

            if self.deltaX > 0:
                if self.deltaY > 0:
                    self.direction = 0 # ↘
                else:
                    self.direction = 1 # ↗
            else:
                if self.deltaY > 0:
                    self.direction = 2 # ↙
                else:
                    self.direction = 3 # ↖
        self.prev_ball_pos = ball_pos

        # Calculate predicted ball position
        if self.direction is not None and self.deltaX != 0:
            slope = self.deltaY / self.deltaX
            predicted_x = ball_pos[0] + (400 - ball_pos[1]) / slope

            # Calculate actual landing position after bouncing
            wall_hits = int(predicted_x / 200)
            if wall_hits % 2 == 0:
                predicted_x = abs(predicted_x - 200 * wall_hits)
            else:
                predicted_x = 200 - abs(predicted_x - 200 * wall_hits)

            # Move platform towards predicted position
            if platform_pos[0] + 20 > round(predicted_x / 5) * 5 + 5 :
                self.x.append("MOVE_LEFT")
                return "MOVE_LEFT"
            elif platform_pos[0] + 20 < round(predicted_x / 5) * 5 - 5:
                self.x.append("MOVE_RIGHT")
                return "MOVE_RIGHT"
        self.x.append("NONE")
        return "NONE"
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
        self.prev_ball_pos = None
        self.direction = None
        self.deltaX = None
        self.deltaY = None
        self.data = []
        self.x = []
        self.count = 10

