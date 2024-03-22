import os

for level in range(1, 25):
    os.system(f"python -m mlgame -f 120 --one-shot -i .\\ml\\ml_play_model.py . --difficulty NORMAL --level {level}")
