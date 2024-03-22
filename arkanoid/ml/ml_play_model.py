import pickle

class MLPlay:
    def __init__(self, ai_name, *args, **kwargs):
        """
        Constructor
        """
        print(ai_name)
        self.knn_classifier = self.look_knn_model("knn_classifier_model.pickle")

    def look_knn_model(self, filename):
        with open(filename, 'rb') as file:
            knn_model = pickle.load(file)
        return knn_model

    def update(self, scene_info, *args, **kwargs):
        """
        Generate the command according to the received `scene_info`.
        """
        # Make the caller to invoke `reset()` for the next round.
        if (scene_info["status"] == "GAME_OVER" or
                scene_info["status"] == "GAME_PASS"):
            return "RESET"
        
        # Extract features from scene_info
        ball_position = scene_info["ball"]
        platform_position = scene_info["platform"]
        bricks_remaining = len(scene_info["bricks"])
        features = [ball_position[0], ball_position[1], platform_position[0], bricks_remaining]
        
        # Predict action using KNN model
        reverse_mapping = {-1: "MOVE_LEFT", 0: "NONE", 1: "MOVE_RIGHT"}
        action = self.knn_classifier.predict([features])[0]
        predicted_action = reverse_mapping[action]

        if not scene_info["ball_served"]:
            command = "SERVE_TO_LEFT"
        else:
            # Translate predicted action into game command
            if predicted_action == "MOVE_LEFT":
                command = "MOVE_LEFT"
            elif predicted_action == "MOVE_RIGHT":
                command = "MOVE_RIGHT"
            else:
                command = "NONE"  # Handle cases where the model predicts an unknown action

        return command

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
