import random
import math
import json
from decorators import timer

init_pos_limit = 10.0
sheep_move_dist = 0.5
wolf_move_dist = 2


# sheep_possible_moves = [(-sheep_move_dist, 0), (sheep_move_dist, 0), (0, -sheep_move_dist), (0, sheep_move_dist)]

# liczba tur: 50
# liczba owiec: 15
# init_pos_limit: 10.0
# sheep_move_dist: 0.5
# wolf_move_dist: 1.0

class Sheep:
    def __init__(self, ID: int, position: list[float]):
        self.ID = ID
        self.position = position
        self.move_dist = sheep_move_dist
        self.alive = True

    def __str__(self) -> str:
        return f'Alive sheep, at position {self.position}'


class Wolf:
    def __init__(self):
        self.position = [0.0, 0.0]
        self.move_dist = wolf_move_dist
        self.eaten_count = 0

    def __str__(self) -> str:
        return f'Wolf at position: {self.position} with {self.eaten_count} sheep eaten'


def get_stats_str(all_sheep: list[Sheep], round_number: int, sheep_eaten_str: str, wolf: Wolf) -> str:
    return f'''Round number {round_number + 1}:
Wolf position: x = {wolf.position[0]:.3f}, y = {wolf.position[1]:.3f}
Alive sheep: {sum(1 for sheep in all_sheep if sheep.alive)}
{sheep_eaten_str}'''


def simulation(number_of_rounds: int, all_sheep: list[Sheep], wolf: Wolf):
    ################################################################################
    # inner methods

    # returns closest sheep along with its distance from the wolf
    def get_closest_sheep(alive_sheep: list[Sheep]) -> tuple[Sheep, float]:
        sheep_and_distances = {index: math.dist(wolf.position, sheep.position) for index, sheep in enumerate(alive_sheep)}

        return alive_sheep[(min_dist := min(sheep_and_distances, key=sheep_and_distances.get))], sheep_and_distances[
            min_dist]

    def eat_sheep(sheep: Sheep):
        wolf.position = sheep.position
        wolf.eaten_count += 1
        # all_sheep[all_sheep.index(sheep)].alive = False
        sheep.alive = False

    def move_towards_sheep(sheep: Sheep, distance: float = None):
        if distance is None:
            distance = math.dist(sheep.position, wolf.position)
        distance_vector = [x - y for x, y in zip(sheep.position, wolf.position)]
        wolf.position = [w_pos + (wolf_move_dist / distance) * vector
                         for w_pos, vector in zip(wolf.position, distance_vector)]

    ################################################################################

    for round_number in range(number_of_rounds):
        alive_sheep = [sheep for sheep in all_sheep if sheep.alive]
        if len(alive_sheep) == 0:
            print('All sheep have been eaten')
            break

        for sheep in alive_sheep:
            sheep.position[random.randint(0, 1)] += random.choice((-1, 1)) * sheep_move_dist

        closest_sheep, closest_sheep_distance = get_closest_sheep(alive_sheep)
        sheep_eaten_str = ''
        if closest_sheep_distance < wolf_move_dist:
            eat_sheep(closest_sheep)
            sheep_eaten_str = f'Sheep with ID {closest_sheep.ID} has been eaten this round\n'
        else:
            move_towards_sheep(closest_sheep, closest_sheep_distance)
        # print(wolf)
        # print(f'{math.dist(x, wolf.position):.3f}')

        print(get_stats_str(all_sheep, round_number, sheep_eaten_str, wolf))


@timer
def main():
    number_of_rounds = 50
    number_of_sheep = 15
    all_sheep = [Sheep(i, [random.uniform(-init_pos_limit, init_pos_limit) for _ in range(2)])
                 for i in range(number_of_sheep)]
    wolf = Wolf()

    simulation(number_of_rounds, all_sheep, wolf)


if __name__ == '__main__':
    main()
