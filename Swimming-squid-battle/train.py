import pygame

from mlgame.game.generic import quit_or_esc
from src.game import SwimmingSquid
from ml import ml_play_template, ml_test
from tqdm import tqdm

LEVEL = 8
LEVEL_FILE = ""
GAME_TIMES = 1
SOUND = "off"

game_times = 0
p1_win = 0
p2_win = 0

if __name__ == '__main__':
    player1 = ml_play_template.MLPlay("A", {'level': LEVEL, 'level_file': LEVEL_FILE, 'game_times': GAME_TIMES, 'sound': SOUND})
    player2 = ml_test.MLPlay("B", {'level': LEVEL, 'level_file': LEVEL_FILE, 'game_times': GAME_TIMES, 'sound': SOUND})
    # for i in tqdm(1501):
    with tqdm(total=197, unit="場遊戲") as pbar:
        pbar.set_description("進度條")
        for i in range(197):
            pygame.init()
            game = SwimmingSquid(level=LEVEL,level_file=LEVEL_FILE, game_times=GAME_TIMES,sound=SOUND)
            scene_init_info_dict = game.get_scene_init_data()
            frame_count = 0
            while game.is_running and not quit_or_esc():
                commands = game.get_keyboard_command()
                game.update({'1P': player1.update(game.get_data_from_game_to_player()['1P']), '2P': player2.update(game.get_data_from_game_to_player()['2P'])})
                frame_count += 1
            game_times += 1
            game_result = game.get_game_result()
            if game_result['attachment'][0]['rank'] == 1:
                p1_win += 1
            elif game_result['attachment'][1]['rank'] == 1:
                p2_win += 1
                
            # print(pd.DataFrame(game_result['attachment']).to_string())
            pbar.postfix = "玩家1: %d, 玩家2: %d" % (p1_win, p2_win)
            pbar.update(1)
            if p1_win >= 750 or p2_win >= 750:
                break


    print("\n共%d場比賽\n玩家1\t玩家2\n%d\t%d" % (game_times, p1_win, p2_win))


    pygame.quit()