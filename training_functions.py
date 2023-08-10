from ai_functions import *
from game_launcher import *

import time

def run_vs_other(training_ai: str, robustness: int, do_fast: bool, games_per_round: int):

    parent = load_ai('best')

    gs = GameSettings(civilisations = ['huns','huns'], names = ['alpha_test',training_ai], map_size = 'tiny',  game_time_limit = max_game_time, map_id = 'arabia', speed = do_fast)

    f = open("best_score.txt","r")
    best = int(f.read())
    f.close()

    print("Initial score: " + str(best))

    wins = 0
    mutation_chance = default_mutation_chance
    fails = 0

    while wins < games_per_round * robustness:

        child = mutate_script(parent, mutation_chance)

        write_ai(child, "alpha_test")

        wins = 0
        nest_break = False
        start = time.time()

        for i in range(robustness):

            l = Launcher(executable_path = "C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe", settings = gs)

            master_score_list = []
            times = []

            games =  l.launch_games(instances = games_per_round,round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            for game in games:
                if game.stats.winner == 1:
                    wins += 1
                master_score_list.append(game.stats.scores)
                if game.stats.elapsed_game_time < 100:
                    nest_break = True
            if wins == 0 or wins + (robustness - (i + 1)) * games_per_round < best or nest_break:
                break

        b_score = wins

        print("Wins: " + str(wins) + "  Time: " + str(time.time() - start) + " Mutation chance: " + str(mutation_chance))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(default_mutation_chance + fails * anneal_amount, .1)
            else:
                mutation_chance = max(default_mutation_chance - fails * anneal_amount, .001)
        else:
            best = b_score
            print(str(best) + " real wins: " + str(wins))
            parent = child
            fails = 0
            mutation_chance = default_mutation_chance

            write_ai(child, 'best')

            f = open("best_score.txt",'w+')
            f.write(str(best))
            f.close()

def run_for_speed(training_ai: str, robustness: int, do_fast: bool, games_per_round: int):

    parent = load_ai('best')

    gs = GameSettings(civilisations = ['huns','huns'], names = ['alpha_test',training_ai], map_size = 'tiny',  game_time_limit = max_game_time, map_id = 'arabia', speed = do_fast)

    best = float('-inf')

    generation = 0

    wins = 0
    mutation_chance = default_mutation_chance
    fails = 0

    while True:

        if generation != 0:
            child = mutate_script(parent, mutation_chance)
        else:
            child = parent

        generation += 1

        write_ai(child, "alpha_test")

        wins = 0
        nest_break = False
        start = time.time()

        times = []

        for i in range(robustness):

            l = Launcher(executable_path = "C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe", settings = gs)

            games =  l.launch_games(instances = games_per_round,round_robin=False)
            games = [game for game in games if game.status != GameStatus.EXCEPTED]

            for game in games:
                if game.stats.winner == 1:
                    wins += 1
                times.append(game.stats.elapsed_game_time)

            if wins < len(times):
                break

        if wins == robustness * games_per_round:

            b_score = - sum(times)/len(times)

            gs.game_time_limit = max(times) + 120
            print(str( max(times) + 120 ))

        else:

            if generation == 0:
                print("fail")
                generation = 0

            b_score = float('-inf')


        print("Time: " + str(time.time() - start) + " Mutation chance: " + str(mutation_chance))

        # checks number of rounds with no improvement and sets annealing
        if b_score <= best:
            fails += 1
            if fails % 2 == 0:
                mutation_chance = min(default_mutation_chance + fails * anneal_amount, .1)
            else:
                mutation_chance = max(default_mutation_chance - fails * anneal_amount, .001)
        else:
            best = b_score
            print(str(best) + " real wins: " + str(wins))
            parent = child
            fails = 0
            mutation_chance = default_mutation_chance

            write_ai(child, 'best')

def benchmark(ai_one: str, ai_two: str, robustness: int, do_fast: bool, games_per_round: int):
    gs = GameSettings(civilisations = ['huns','huns'], names = [ai_one,ai_two], map_size = 'tiny',  game_time_limit = max_game_time, map_id = 'arabia', speed = do_fast)

    wins = 0
    nest_break = False
    start = time.time()

    for i in range(robustness):

        l = Launcher(executable_path = "C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe", settings = gs)

        master_score_list = []
        times = []

        games =  l.launch_games(instances = games_per_round,round_robin=False)
        games = [game for game in games if game.status != GameStatus.EXCEPTED]

        for game in games:
            if game.stats.winner == 1:
                wins += 1
            master_score_list.append(game.stats.scores)
            if game.stats.elapsed_game_time < 100:
                nest_break = True

        if nest_break:
            break

    print("AI_One Wins: " + str(wins) + "  Time: " + str(time.time() - start))

def run_vs_self(robustness: int, do_fast: bool, games_per_round: int):

    parent = load_ai('best')

    gs = GameSettings(civilisations = ['huns','huns'], names = ['alpha_test',"test_best"], map_size = 'tiny',  game_time_limit = max_game_time, map_id = 'arabia', speed = do_fast)

    while True:

        best = 0
        wins = 0
        mutation_chance = default_mutation_chance
        fails = 0
        generation = 0

        write_ai(parent, "test_best")
        print("new round")

        while wins < games_per_round * robustness:

            generation += 1

            if generation != 1:
                child = mutate_script(parent, mutation_chance)
            else:
                child = parent

            write_ai(child, "alpha_test")

            wins = 0
            nest_break = False
            start = time.time()

            for i in range(robustness):

                l = Launcher(executable_path = "C:\\Program Files\\Microsoft Games\\Age of Empires II\\age2_x1.5.exe", settings = gs)

                master_score_list = []
                times = []

                games =  l.launch_games(instances = games_per_round,round_robin=False)
                games = [game for game in games if game.status != GameStatus.EXCEPTED]

                for game in games:
                    if game.stats.winner == 1:
                        wins += 1
                    master_score_list.append(game.stats.scores)
                    if game.stats.elapsed_game_time < 100:
                        nest_break = True
                if wins == 0 or wins + (robustness - (i + 1)) * games_per_round < best or nest_break:
                    break

            b_score = wins

            print("Wins: " + str(wins) + "  Time: " + str(time.time() - start))

            # checks number of rounds with no improvement and sets annealing
            if b_score <= best:
                fails += 1
                if fails % 2 == 0:
                    mutation_chance = min(default_mutation_chance + fails * anneal_amount, .1)
                else:
                    mutation_chance = max(default_mutation_chance - fails * anneal_amount, .001)
            else:
                best = b_score
                print(str(best) + " real wins: " + str(wins))
                parent = child
                fails = 0
                mutation_chance = default_mutation_chance

                write_ai(child, 'best')

                f = open("best_score.txt",'w+')
                f.write(str(best))
                f.close()
