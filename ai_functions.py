import random
import copy
from settings import *

goals_used = default_goals_used

def generate_parameters(goals_used: int, rule_id: str) -> list:

    parameters = ["","","",""]

    if rule_id in fact_list:
        param_ids = facts[rule_id]
    elif rule_id in action_list:
        param_ids = actions[rule_id]
    elif rule_id in goal_fact_list:
        param_ids = goal_facts[rule_id]
    elif rule_id in goal_action_list:
        param_ids = goal_actions[rule_id]

    if rule_id != 'set-strategic-number':
        for i in range(len(parameters)):

            param_options = paramdict[param_ids[i+1]]

            if "|" in param_options:
                param_options = param_options.split('|')
                parameters[i] = str( random.randint(int(param_options[0]),int(param_options[1])) )
            else:
                param_options = param_options.split(';')
                parameters[i] = random.choice(param_options)

    else:
        strategic_number = random.choice(paramdict['SnId'].split(';'))

        parameters[0] = strategic_number
        param_options = snDict[strategic_number].split('|')
        parameters[1] = str( random.randint(int(param_options[0]),int(param_options[1])) )

    if rule_id in goal_fact_list or rule_id in goal_action_list:
        parameters[0] = str( random.randint(1,goals_used) )

    return parameters

def mutate_parameters(goals_used: int, rule_id: str, parameters: list, mutation_chance: float) -> list:

    if rule_id in fact_list:
        param_ids = facts[rule_id]
    elif rule_id in action_list:
        param_ids = actions[rule_id]
    elif rule_id in goal_fact_list:
        param_ids = goal_facts[rule_id]
    elif rule_id in goal_action_list:
        param_ids = goal_actions[rule_id]
    else:
        return ["do-nothing","","",""]

    local_param_dict = copy.deepcopy(paramdict)
    local_param_dict['GoalId'] = "0|" + str(goals_used)

    #print(rule_id)
    if rule_id != 'set-strategic-number':
        for i in range(len(parameters)):
            param_options = local_param_dict[param_ids[i+1]]

            if random.random() < mutation_chance:
                if "|" in param_options:
                    param_options = param_options.split('|')

                    if random.random() < .5:
                        parameters[i] = str( random.randint(int(param_options[0]),int(param_options[1])) )
                    else:
                        parameters[i] = max( int( param_options[0] ), min( int( param_options[1] ), int( float(parameters[i]) + random.uniform(.9,1.1) ) ) )
                else:
                    param_options = param_options.split(';')
                    parameters[i] = random.choice(param_options)

    else:
        if random.random() < mutation_chance:
            strategic_number = random.choice(local_param_dict['SnId'].split(';'))
            parameters[0] = strategic_number
            param_options = snDict[strategic_number].split('|')
            parameters[1] = str( random.randint(int(param_options[0]),int(param_options[1])) )


        else:
            strategic_number = parameters [0]
            parameters[0] = strategic_number
            param_options = snDict[strategic_number].split('|')
            if random.random() < mutation_chance:
                parameters[1] = str( random.randint(int(param_options[0]),int(param_options[1])) )

    if rule_id in goal_fact_list or rule_id in goal_action_list:
        if random.random() < mutation_chance:
            parameters[0] = str( random.randint(1,goals_used) )

    return parameters

def generate_rule_piece(goals_used: int, type: str) -> str:


    if type == 'fact':
        piece = random.choice(fact_list)
    elif type == 'action':
        piece = random.choice(action_list)
    elif type == 'goal_fact':
        piece = random.choice(goal_fact_list)
    elif type == 'goal_action':
        piece = random.choice(goal_action_list)

    inverse = random.choice([True,False])

    parameters = generate_parameters(goals_used, piece)

    piece_string = piece + " "

    for i in range(len(parameters)):
        piece_string += parameters[i] + " "

    if inverse and type in ['fact','goal_fact']:
        piece_string = "(not(" + piece_string + "))\n"
    else:
        piece_string = "(" + piece_string + ")\n"
    return piece_string

def generate_rule(goals_used: int, layer: str) -> str:

    fact_length = 10
    action_length = 10
    while fact_length + action_length > 8:
        fact_length = random.randint(1,5)
        action_length = random.randint(1,5)

    facts = []
    actions = []
    pair_types = []

    if layer == 'input':
        rule_string = ";==input\n"
        for i in range(fact_length):
            facts.append(generate_rule_piece(goals_used,'fact'))

        for i in range(action_length):
            actions.append(generate_rule_piece(goals_used,'goal_action'))

    elif layer == 'output':
        rule_string = ";==output\n"
        for i in range(fact_length):
            facts.append(generate_rule_piece(goals_used,'goal_fact'))

        for i in range(action_length):
            actions.append(generate_rule_piece(goals_used,'action'))

    elif layer == 'goal_layer':
        rule_string = ";==middle\n"
        for i in range(fact_length):
            facts.append(generate_rule_piece(goals_used,'goal_fact'))

        for i in range(action_length):
            actions.append(generate_rule_piece(goals_used,'goal_action'))

    elif layer == 'normal':
        rule_string = ";==normal\n"
        for i in range(fact_length):
            facts.append(generate_rule_piece(goals_used,'fact'))

        for i in range(action_length):
            actions.append(generate_rule_piece(goals_used,'action'))


    pair_check_number = fact_length

    while pair_check_number >= 2:
        pair_check_number = int(pair_check_number/2)
        for i in range(pair_check_number):
            pair_types.append(random.choice(pair_type_list))

    #I need to add not/or trees but what a pain in the ass!!!!

    rule_string += "(defrule\n"

    for i in range(len(facts)):
        rule_string += "\t" + facts[i]

    rule_string += "=>\n"

    for i in range(len(actions)):
        rule_string += "\t" + actions[i]

    rule_string += ")\n\n"

    if len(rule_string.split("=>")[0]) > 10 and len(rule_string.split("=>")[1]) > 5:
        return rule_string
    else:
        return "\n\n"

def generate_ai_script(goals_used: int) -> str:
    ai_script = ";" + str(goals_used) + ";=="
    ai_script += ";This is a genetically evolved AI, contact MattyBeRad for more information|||"

    for i in range(default_input_neuron_count):
        ai_script += generate_rule(goals_used,'input')

    for i in range(default_goal_neuron_count):
        ai_script += generate_rule(goals_used,'goal_layer')

    for i in range(default_output_neuron_count):
        ai_script += generate_rule(goals_used,'output')

    return ai_script

def mutate_script(given_script: str, mutation_chance: float) -> str:

    parent_script = given_script
    ai_script = given_script

    while parent_script == ai_script:

        script = given_script
        #parse rule
        script = ai_script.replace("(defrule","")
        script = script.replace("\n)\n","\n\n")
        script = script.split(';==')

        goals_used = script.pop(0).split(';')
        goals_used = int(goals_used[1])

        if random.random() < mutation_chance:
            goals_used += random.randint(-2,2)

        ai_script = ";" + str(goals_used) + ";=="
        ai_script += ";This is a genetically evolved AI, contact MattyBeRad for more information|||"

        script = random_remove(script.copy(), mutation_chance)

        script_part_two = ""

        for i in range(1,len(script)):

            rule = script[i].split('=>')

            facts = rule[0].split('\n')
            actions = rule[1].split('\n')
            rule_type = facts.pop(0)

            lock = False
            if "==lock==" in rule_type:
                mutation_chance = 0
                lock = True
                rule_type = rule_type.replace("==lock==","")

            if not lock:
                rule_string = ';==' + rule_type + "\n(defrule\n"
            else:
                rule_string = ';==' + rule_type + "==lock==\n(defrule\n"

            if rule_type in ['input','normal']:
                piece_type = 'fact'
            else:
                piece_type = 'goal_fact'

            facts = random_remove(facts.copy(), mutation_chance)

            for r in range(len(facts)):
                #print(facts[r])
                if facts[r].replace(" ","") != '':
                    rule_string += "\t" + mutate_rule_piece(goals_used, piece_type, facts[r], mutation_chance)

            while random.random() < mutation_chance and len(facts) + len(actions) < 8:
                rule_string += "\t" + generate_rule_piece(goals_used, piece_type)

            rule_string += "=>\n"

            if rule_type in ['output','normal']:
                piece_type = 'action'
            else:
                piece_type = 'goal_action'

            actions = random_remove(actions.copy(), mutation_chance)

            for r in range(len(actions)):
                #print(actions[r])
                if actions[r].replace(" ","") != '':
                    rule_string += "\t" + mutate_rule_piece(goals_used, piece_type, actions[r], mutation_chance)

            while random.random() < mutation_chance and len(facts) + len(actions) < 8:
                rule_string += "\t" + generate_rule_piece(goals_used, piece_type)

            rule_string += ")\n"

            if len(rule_string.split("=>")[0]) > 21 and len(rule_string.split("=>")[1]) > 5:
                script_part_two += rule_string

                while random.random() < mutation_chance:
                    script_part_two += rule_string

            #if rule.pop(0) == 'input':

        while random.random() < mutation_chance:
            script_part_two += generate_rule(goals_used, random.choice(['input','goal_layer','output','normal']))

    return ai_script + "\n\n" + resign_rule + "\n\n" + script_part_two

def mutate_rule_piece(goals_used: int, piece_type:str, piece: str, mutation_chance: float) -> str:

    if random.random() < mutation_chance:
        return generate_rule_piece(goals_used, piece_type)

    if "(not" in piece:
        inverse = True
        piece = piece.replace("(not(","")
    else:
        inverse = False

    if random.random() < mutation_chance:
        inverse = random.choice([True,False])

    piece = piece.replace("\t","")
    piece = piece.replace("(","")
    piece = piece.replace(")","")

    parameters = piece.split(" ")
    rule_id = parameters.pop(0)

    #print(parameters)
    while len(parameters) > 4:
        parameters.pop(-1)

    parameters = mutate_parameters(goals_used,rule_id,parameters,mutation_chance)

    piece_string = rule_id + " "

    for i in range(len(parameters)):
        piece_string += str(parameters[i]) + " "

    if inverse and type in ['fact','goal_fact']:
        piece_string = "(not(" + piece_string + "))\n"
    else:
        piece_string = "(" + piece_string + ")\n"

    return piece_string

def write_ai(ai: str, file_name: str):
    f = open(ai_directory + file_name + ".per","w+")

    f.write(ai)

    f.close()

def load_ai(file_name: str) -> str:
    f = open(ai_directory + file_name + ".per","r")
    ai = f.read()
    f.close()

    return ai

def random_remove(item_list: list, mutation_chance) -> list:

    while random.random() < mutation_chance and len(item_list) > 1:
        item_for_removal = item_list[ random.randint(0,len(item_list)-1) ]
        if "==lock==" not in item_for_removal:
            if len(item_list) > 1:
                item_list.remove(item_for_removal)

    return item_list
