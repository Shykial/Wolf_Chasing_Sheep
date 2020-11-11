import random
import math
import json
from decorators import timer
from entities import Sheep, Wolf, sheep_move_dist, wolf_move_dist

init_pos_limit = 10.0


def get_stats_str(alive_sheep: list[Sheep], round_number: int,
                  wolf: Wolf, sheep_eaten: Sheep = None) -> str:
    sheep_eaten_str = f'Sheep with ID {sheep_eaten.ID} has been eaten this round\n' if sheep_eaten else ''
    return f'''Round number {round_number + 1}:
Wolf position: x = {wolf.position[0]:.3f}, y = {wolf.position[1]:.3f}
Alive sheep: {len(alive_sheep)}
{sheep_eaten_str}'''


class Simulation:
    def __init__(self, all_sheep: list[Sheep], wolf: Wolf):
        self.all_sheep = all_sheep
        self.wolf = wolf

    def get_closest_sheep(self, alive_sheep: list[Sheep]) -> tuple[Sheep, float]:
        sheep_and_distances = {index: math.dist(self.wolf.position, sheep.position) for index, sheep in
                               enumerate(alive_sheep)}

        return alive_sheep[(min_dist := min(sheep_and_distances,
                                            key=sheep_and_distances.get))], sheep_and_distances[min_dist]

    def eat_sheep(self, alive_sheep: list[Sheep], sheep: Sheep):
        self.wolf.position = sheep.position
        sheep.alive = False
        alive_sheep.remove(sheep)
        self.wolf.eaten_count += 1

    def move_towards_sheep(self, sheep: Sheep, distance: float = None):
        if distance is None:
            distance = math.dist(sheep.position, self.wolf.position)
        distance_vector = [s_pos - w_pos for s_pos, w_pos in zip(sheep.position, self.wolf.position)]
        # gives [sheep_x - wolf_x, sheep_y - wolf_y]

        self.wolf.position = [w_pos + (wolf_move_dist / distance) * vector
                              for w_pos, vector in zip(self.wolf.position, distance_vector)]

    def run(self, number_of_rounds: int):
        # shallow copy of the list: object elements are still being shared,
        # but removing object from one list, doesn't affect the other
        alive_sheep = self.all_sheep.copy()

        for round_number in range(number_of_rounds):
            if len(alive_sheep) == 0:
                print('All sheep have been eaten')
                break

            for sheep in alive_sheep:
                sheep.position[random.randint(0, 1)] += random.choice((-1, 1)) * sheep_move_dist

            closest_sheep, closest_sheep_distance = self.get_closest_sheep(alive_sheep)
            sheep_eaten = None
            if closest_sheep_distance < wolf_move_dist:
                self.eat_sheep(alive_sheep, closest_sheep)
                sheep_eaten = closest_sheep
            else:
                self.move_towards_sheep(closest_sheep, closest_sheep_distance)

            print(get_stats_str(alive_sheep, round_number, self.wolf, sheep_eaten))


@timer
def main():
    number_of_rounds = 50
    number_of_sheep = 15
    all_sheep = [Sheep(i, [random.uniform(-init_pos_limit, init_pos_limit) for _ in range(2)])
                 for i in range(number_of_sheep)]
    wolf = Wolf()

    simulation = Simulation(all_sheep, wolf)
    simulation.run(number_of_rounds)


if __name__ == '__main__':
    main()
