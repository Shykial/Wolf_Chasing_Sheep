import math
import random

from decorators import Logger
from entities import Sheep, Wolf


class Simulation:
    class_name = 'Simulation'
    default_pos_limit = 10.0

    @Logger.log_decor('info', class_name=class_name)
    def __init__(self, all_sheep: list[Sheep], wolf: Wolf):
        self.all_sheep = all_sheep
        self.wolf = wolf
        self.alive_sheep = self.all_sheep.copy()
        # shallow copy of the list: object elements are still being shared,
        # but removing object from one list, doesn't affect the other

        self.simulation_data = []

    # @Logger.log_decor('debug', class_name=class_name)
    # not logging repr using Logger decorator as that would cause infinite recursion
    def __repr__(self) -> str:
        return f'Simulation object: all_sheep = {self.all_sheep}, wolf = {repr(self.wolf)},' \
               f' alive_sheep = {self.alive_sheep}, simulation_data = {self.simulation_data}'

    @Logger.log_decor('debug', class_name=class_name)
    def add_round_to_simulation_data(self, round_number: int):
        self.simulation_data.append({'round_no': round_number, 'wolf_pos': self.wolf.position,
                                     'sheep_pos': [sheep.position.copy() if sheep.alive else None for sheep in
                                                   self.all_sheep]})
        # using copy on sheep.position to avoid referencing sheep.position list changing in time

    @Logger.log_decor('debug', class_name=class_name)
    def get_round_stats_str(self, round_number: int, sheep_eaten: Sheep = None) -> str:
        sheep_eaten_str = f'Sheep with ID {sheep_eaten.ID} has been eaten this round\n' if sheep_eaten else ''
        return f'''Round number {round_number}:
Wolf position: x = {self.wolf.position[0]:.3f}, y = {self.wolf.position[1]:.3f}
Alive sheep: {len(self.alive_sheep)}
{sheep_eaten_str}'''

    @Logger.log_decor('info', class_name=class_name)
    def get_closest_sheep(self) -> tuple[Sheep, float]:
        sheep_distances = {sheep: math.dist(self.wolf.position, sheep.position) for sheep in self.alive_sheep}

        return (sheep := min(sheep_distances, key=sheep_distances.get)), sheep_distances[sheep]

    @Logger.log_decor('debug', class_name=class_name)
    def eat_sheep(self, sheep: Sheep):
        init_wolf_pos = self.wolf.position

        self.wolf.position = sheep.position
        sheep.alive = False
        self.alive_sheep.remove(sheep)
        self.wolf.eaten_count += 1

        log_msg = f'Wolf ate sheep with ID {sheep.ID}, moving from position {init_wolf_pos} to {self.wolf.position}'
        Logger.log('info', log_msg)

    @Logger.log_decor('debug', class_name=class_name)
    def move_towards_sheep(self, sheep: Sheep, distance: float = None):
        init_wolf_pos = self.wolf.position

        if distance is None:
            distance = math.dist(sheep.position, self.wolf.position)
        distance_vector = [s_pos - w_pos for s_pos, w_pos in zip(sheep.position, self.wolf.position)]
        # gives [sheep_x - wolf_x, sheep_y - wolf_y]

        self.wolf.position = [w_pos + (self.wolf.move_dist / distance) * vector
                              for w_pos, vector in zip(self.wolf.position, distance_vector)]

        log_msg = f'Wolf moved from position {init_wolf_pos} to {self.wolf.position} ' \
                  f'towards sheep with ID {sheep.ID}, on position {sheep.position}'
        Logger.log('info', log_msg)

    @Logger.log_decor('debug', class_name=class_name)
    def run(self, number_of_rounds: int, await_input_after_round: bool = False):

        for round_number in range(1, number_of_rounds + 1):
            if len(self.alive_sheep) == 0:
                print('All sheep have been eaten')
                break

            for sheep in self.alive_sheep:
                init_sheep_pos = sheep.position

                sheep.position[random.randint(0, 1)] += random.choice((-1, 1)) * sheep.move_dist

                log_msg = f'Sheep with ID {sheep.ID} moved from position {init_sheep_pos} to {sheep.position}'
                Logger.log('info', log_msg)

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
                input('Press enter to move onto next round\n')
