import argparse
import csv
import json
import math
import os
import random
from configparser import ConfigParser
from typing import Iterable, Any

from decorators import timer
from entities import Sheep, Wolf


def get_default_pos_limit() -> float:
    return 10.0


def get_parsed_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-c', '--config', metavar='FILE', help='Filename to read configuration from')
    argparser.add_argument('-d', '--dir', help='Subdirectory to store exported program data')
    argparser.add_argument('-l', '--log', metavar='LEVEL', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                           type=str.upper, help='Logging events, where LEVEL stands for event level,'
                                                'one of (DEBUG, INFO, WARNING,  ERROR, CRITICAL)')
    # using str.upper for case insensitive arg parsing

    argparser.add_argument('-r', '--rounds', metavar='NUM', type=int, help='Number of rounds in the simulation')
    argparser.add_argument('-s', '--sheep', metavar='NUM', type=int, help='Number of sheep in the simulation')
    argparser.add_argument('-w', '--wait', action='store_true',
                           help='Flag set to wait for keyboard input after displaying each round statistics')

    parsed_args = argparser.parse_args()
    validate_parsed_args(parsed_args)
    return parsed_args


# validating rounds and sheep arguments as negative values would otherwise be accepted.
def validate_parsed_args(parsed_args: argparse.Namespace):
    int_arguments = {'rounds': parsed_args.rounds, 'sheep': parsed_args.sheep}
    for arg_name, arg_value in int_arguments.items():
        if arg_value is not None and arg_value <= 0:
            raise ValueError(f'Argument "{arg_name}" must be a positive integer, provided {arg_value}')


def get_config_parser(config_file: str) -> ConfigParser:
    config = ConfigParser()
    config.read(config_file)
    return config


def get_values_from_config(config: ConfigParser) -> tuple[float, float, float]:
    try:
        init_pos_limit = float(config['Terrain']['InitPosLimit'])
        sheep_move_dist = float(config['Movement']['SheepMoveDist'])
        wolf_move_dist = float(config['Movement']['WolfMoveDist'])
    except KeyError as error:
        raise KeyError(f'Missing key for {error.args[0]}, have you declared it in the config file?')
    except ValueError:
        raise ValueError('Values passed in the config file could not be converted to float, correct them and try again')

    for val in (init_pos_limit, sheep_move_dist, wolf_move_dist):
        if val <= 0:
            raise ValueError(f'Values passed in the config file need to be floats higher than 0,'
                             f' correct value {val} and try again')

    return init_pos_limit, sheep_move_dist, wolf_move_dist


def export_to_json(data: Any, filename: str = 'pos.json', directory: str = '.'):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def export_to_csv(data: Iterable, filename: str = 'alive.csv', directory: str = '.', header_row=None):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        if header_row:
            csv_writer.writerow(header_row)
        for item in data:
            csv_writer.writerow(item)


class Simulation:
    def __init__(self, all_sheep: list[Sheep], wolf: Wolf):
        self.all_sheep = all_sheep
        self.wolf = wolf
        self.alive_sheep = self.all_sheep.copy()
        # shallow copy of the list: object elements are still being shared,
        # but removing object from one list, doesn't affect the other

        self.simulation_data = []

    def add_round_to_simulation_data(self, round_number: int):
        self.simulation_data.append({'round_no': round_number, 'wolf_pos': self.wolf.position,
                                     'sheep_pos': [sheep.position.copy() if sheep.alive else None for sheep in
                                                   self.all_sheep]})
        # using copy on sheep.position to avoid referencing sheep.position list changing in time

    def get_round_stats_str(self, round_number: int, sheep_eaten: Sheep = None) -> str:
        sheep_eaten_str = f'Sheep with ID {sheep_eaten.ID} has been eaten this round\n' if sheep_eaten else ''
        return f'''Round number {round_number}:
Wolf position: x = {self.wolf.position[0]:.3f}, y = {self.wolf.position[1]:.3f}
Alive sheep: {len(self.alive_sheep)}
{sheep_eaten_str}'''

    def get_closest_sheep(self) -> tuple[Sheep, float]:
        sheep_distances = {sheep: math.dist(self.wolf.position, sheep.position) for sheep in self.alive_sheep}

        return (sheep := min(sheep_distances, key=sheep_distances.get)), sheep_distances[sheep]

    def eat_sheep(self, sheep: Sheep):
        self.wolf.position = sheep.position
        sheep.alive = False
        self.alive_sheep.remove(sheep)
        self.wolf.eaten_count += 1

    def move_towards_sheep(self, sheep: Sheep, distance: float = None):
        if distance is None:
            distance = math.dist(sheep.position, self.wolf.position)
        distance_vector = [s_pos - w_pos for s_pos, w_pos in zip(sheep.position, self.wolf.position)]
        # gives [sheep_x - wolf_x, sheep_y - wolf_y]

        self.wolf.position = [w_pos + (self.wolf.move_dist / distance) * vector
                              for w_pos, vector in zip(self.wolf.position, distance_vector)]

    def run(self, number_of_rounds: int, await_input_after_round: bool = False):

        for round_number in range(1, number_of_rounds + 1):
            if len(self.alive_sheep) == 0:
                print('All sheep have been eaten')
                break

            for sheep in self.alive_sheep:
                sheep.position[random.randint(0, 1)] += random.choice((-1, 1)) * sheep.move_dist

            closest_sheep, closest_sheep_distance = self.get_closest_sheep()
            sheep_eaten = None
            if closest_sheep_distance < self.wolf.move_dist:
                self.eat_sheep(closest_sheep)
                sheep_eaten = closest_sheep
            else:
                self.move_towards_sheep(closest_sheep, closest_sheep_distance)
            self.add_round_to_simulation_data(round_number)
            print(self.get_round_stats_str(round_number, sheep_eaten))
            if await_input_after_round:
                input('Press any key to move onto next round')


@timer
def main():
    args = get_parsed_args()

    init_pos_limit, sheep_move_dist, wolf_move_dist = get_default_pos_limit(), None, None
    # assigning None type to sheep and wolf move dist initially,
    # so that default values from entities.py would be used if not specified otherwise

    if config_file := args.config:
        config = get_config_parser(config_file)
        init_pos_limit, sheep_move_dist, wolf_move_dist = get_values_from_config(config)

    number_of_rounds = rounds_num if (rounds_num := args.rounds) else 50
    number_of_sheep = sheep_num if (sheep_num := args.sheep) else 15
    wait_for_input = args.wait

    if directory := args.dir:
        data_directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)  # using makedirs instead of simple mkdir to allow nested directories
    else:
        data_directory = '.'

    all_sheep = [Sheep(i, [random.uniform(-init_pos_limit, init_pos_limit) for _ in range(2)],
                       move_dist=sheep_move_dist) for i in range(number_of_sheep)]
    wolf = Wolf(move_dist=wolf_move_dist)

    simulation = Simulation(all_sheep, wolf)
    simulation.run(number_of_rounds, await_input_after_round=wait_for_input)

    export_to_json(simulation.simulation_data, directory=data_directory)

    alive_sheep_data = [(_round['round_no'], sum(1 for pos in _round['sheep_pos'] if pos))
                        for _round in simulation.simulation_data]
    export_to_csv(alive_sheep_data, directory=data_directory, header_row=('Round number', 'Alive sheep'))


if __name__ == '__main__':
    main()
