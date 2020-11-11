sheep_move_dist = 0.5
wolf_move_dist = 1


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
