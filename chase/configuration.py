import argparse
import logging
import os
from configparser import ConfigParser
from typing import Union

from .logger import Logger


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


# using Union[str, None] instead of Optional[str] to avoid ambiguity
@Logger.log_decor('debug')
def setup_logging_config(level: Union[str, None], filename: str = 'chase_backup.log', directory: str = '.'):
    if level:
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
