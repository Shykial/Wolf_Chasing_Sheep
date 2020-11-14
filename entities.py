def get_default_sheep_move_dist() -> float:
    return 0.5


def get_default_wolf_move_dist() -> float:
    return 1.0


class Sheep:
    def __init__(self, ID: int, position: list[float], move_dist: float = None):
        self.ID = ID
        self.position = position
        self.move_dist = move_dist if move_dist is not None else get_default_sheep_move_dist()
        self.alive = True

    def __str__(self) -> str:
        return f'{"Alive sheep," if self.alive else "Dead sheep, eaten"} at position {self.position}'


class Wolf:
    def __init__(self, move_dist: float = None):
        self.position = [0.0, 0.0]
        self.move_dist = move_dist if move_dist is not None else get_default_wolf_move_dist()
        self.eaten_count = 0

    def __str__(self) -> str:
        return f'Wolf at position: {self.position} with {self.eaten_count} sheep eaten'
