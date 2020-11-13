import csv
import json
import math
import random

from decorators import timer
from entities import Sheep, Wolf, sheep_move_dist, wolf_move_dist

init_pos_limit = 10.0


def export_to_json(data, filename: str = 'pos.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def export_to_csv(data, filename: str = 'alive.csv', header_row=None):
    with open(filename, 'w', encoding='utf-8', newline='') as f:
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
                                     'sheep_pos': [sheep.position if sheep.alive else None for sheep in
                                                   self.all_sheep]})

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

        self.wolf.position = [w_pos + (wolf_move_dist / distance) * vector
                              for w_pos, vector in zip(self.wolf.position, distance_vector)]

    def run(self, number_of_rounds: int):

        for round_number in range(1, number_of_rounds + 1):
            if len(self.alive_sheep) == 0:
                print('All sheep have been eaten')
                break

            for sheep in self.alive_sheep:
                sheep.position[random.randint(0, 1)] += random.choice((-1, 1)) * sheep_move_dist

            closest_sheep, closest_sheep_distance = self.get_closest_sheep()
            sheep_eaten = None
            if closest_sheep_distance < wolf_move_dist:
                self.eat_sheep(closest_sheep)
                sheep_eaten = closest_sheep
            else:
                self.move_towards_sheep(closest_sheep, closest_sheep_distance)
            self.add_round_to_simulation_data(round_number)
            print(self.get_round_stats_str(round_number, sheep_eaten))


@timer
def main():
    number_of_rounds = 50
    number_of_sheep = 15
    all_sheep = [Sheep(i, [random.uniform(-init_pos_limit, init_pos_limit) for _ in range(2)])
                 for i in range(number_of_sheep)]
    wolf = Wolf()

    simulation = Simulation(all_sheep, wolf)
    simulation.run(number_of_rounds)
    export_to_json(simulation.simulation_data)
    alive_sheep_data = [(_round['round_no'], sum(1 for pos in _round['sheep_pos'] if pos))
                        for _round in simulation.simulation_data]
    export_to_csv(alive_sheep_data, header_row=('Round number', 'Alive sheep'))


if __name__ == '__main__':
    main()
