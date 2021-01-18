import csv
import json
import os
import random
from typing import Any, Iterable

from .configuration import get_parsed_args, get_config_parser, get_values_from_config, setup_logging_config
from .entities import Sheep, Wolf
from .logger import Logger
from .simulation import Simulation


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
    try:
        main()
    except Exception as e:
        Logger.log('exception', str(e))
