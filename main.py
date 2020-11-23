import argparse
import csv
import json
import logging
import os
import random
from configparser import ConfigParser
from typing import Any, Iterable, Union

from entities import Sheep, Wolf
from simulation import Simulation
from logger import Logger


def get_parsed_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()

    argparser.add_argument('-c', '--config', metavar='FILE', help='Filename to read configuration from')
    argparser.add_argument('-d', '--dir', help='Subdirectory to store exported program data')
    argparser.add_argument('-l', '--log', metavar='LEVEL', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
                           type=str.upper, help='Logging events, where LEVEL stands for event level,'
                                                ' one of (DEBUG, INFO, WARNING,  ERROR, CRITICAL)')
    # using str.upper for case insensitive arg parsing

    argparser.add_argument('-r', '--rounds', metavar='NUM', type=int, help='Number of rounds in the simulation')
    argparser.add_argument('-s', '--sheep', metavar='NUM', type=int, help='Number of sheep in the simulation')
    argparser.add_argument('-w', '--wait', action='store_true',
                           help='Flag set to wait for keyboard input after displaying each round statistics')

    parsed_args = argparser.parse_args()
    validate_parsed_args(parsed_args)
    return parsed_args


# validating rounds and sheep arguments for non-positive values, checking if config file exists
def validate_parsed_args(parsed_args: argparse.Namespace):
    int_arguments = {'rounds': parsed_args.rounds, 'sheep': parsed_args.sheep}
    for arg_name, arg_value in int_arguments.items():
        if arg_value is not None and arg_value <= 0:
            raise ValueError(f'Argument "{arg_name}" must be a positive integer, provided {arg_value}')

    if (config_arg := parsed_args.config) is not None and not os.path.isfile(config_arg):
        raise FileNotFoundError(f'Config file provided: "{config_arg}" was not found.')


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


@Logger.log_decor('debug')
# using Union[str, None] instead of shorter equivalent Optional[str] to avoid ambiguity
def setup_logging_config(level: Union[str, None], filename: str = 'chase.log', directory: str = '.'):
    if level is not None:
        file_path = os.path.join(directory, filename)
        logging_levels = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO,
                          'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
                          'CRITICAL': logging.CRITICAL}
        logging_level = logging_levels[level]
        # format_str = '%(levelname)s:%(name)s:%(module)s:%(message)s'
        format_str = '%(levelname)s:\t%(asctime)s - %(message)s'
        logging.basicConfig(filename=file_path, level=logging_level, format=format_str)
        # logging.basicConfig(level=logging_level)
    else:
        logging.disable()


@Logger.log_decor('debug')
def export_to_json(data: Any, filename: str = 'pos.json', directory: str = '.'):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


@Logger.log_decor('debug')
def export_to_csv(data: Iterable, filename: str = 'alive.csv', directory: str = '.', header_row=None):
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        if header_row:
            csv_writer.writerow(header_row)
        for item in data:
            csv_writer.writerow(item)


@Logger.log_decor('debug')
def main():
    args = get_parsed_args()

    init_pos_limit, sheep_move_dist, wolf_move_dist = Simulation.default_pos_limit, None, None
    # assigning None type to sheep and wolf move dist initially,
    # so that default class values from entities.py would be used if not specified otherwise

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

    setup_logging_config(args.log, directory=data_directory)
    # Logger.set_logger(logging.getLogger(__name__))

    all_sheep = [Sheep(i, [random.uniform(-init_pos_limit, init_pos_limit) for _ in range(2)],
                       move_dist=sheep_move_dist) for i in range(number_of_sheep)]
    wolf = Wolf(move_dist=wolf_move_dist)

    chase_simulation = Simulation(all_sheep, wolf)
    chase_simulation.run(number_of_rounds, await_input_after_round=wait_for_input)

    export_to_json(chase_simulation.simulation_data, directory=data_directory)

    alive_sheep_data = [(_round['round_no'], sum(1 for pos in _round['sheep_pos'] if pos))
                        for _round in chase_simulation.simulation_data]
    export_to_csv(alive_sheep_data, directory=data_directory, header_row=('Round number', 'Alive sheep'))


if __name__ == '__main__':
    main()
