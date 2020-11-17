from decorators import Logger


@Logger.log('debug')
def get_default_sheep_move_dist() -> float:
    return 0.5


@Logger.log('debug')
def get_default_wolf_move_dist() -> float:
    return 1.0


class Sheep:
    class_name = 'Sheep'

    @Logger.log('info', class_name=class_name)
    def __init__(self, ID: int, position: list[float], move_dist: float = None):
        self.ID = ID
        self.position = position
        self.move_dist = move_dist if move_dist is not None else get_default_sheep_move_dist()
        self.alive = True

    @Logger.log('debug', class_name=class_name)
    def __str__(self) -> str:
        return f'{"Alive sheep," if self.alive else "Dead sheep, eaten"} at position {self.position}'

    def __repr__(self) -> str:
        return f'Sheep object, ID = {self.ID}, position = {self.position},' \
               f' move distance = {self.move_dist}, alive = {self.alive}'


class Wolf:
    class_name = 'Wolf'

    @Logger.log('info', class_name=class_name)
    def __init__(self, move_dist: float = None):
        self.position = [0.0, 0.0]
        self.move_dist = move_dist if move_dist is not None else get_default_wolf_move_dist()
        self.eaten_count = 0

    @Logger.log('debug', class_name=class_name)
    def __str__(self) -> str:
        return f'Wolf at position: {self.position} with {self.eaten_count} sheep eaten'

    def __repr__(self) -> str:
        return f'Wolf object: position = {self.position},' \
               f' move distance = {self.move_dist}, eaten_count = {self.eaten_count}'
