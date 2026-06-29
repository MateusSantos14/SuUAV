import math
from typing import Tuple
from src.strategies.GenericStrategy import GenericStrategy
from src.utils.conversionMeters import meters_to_geo

class SquareStrategy(GenericStrategy):
    """
    Estratégia de mobilidade quadrada.
    """
    def __init__(self, center_point: Tuple[float, float], side_length: float, angle_degrees: int = 90, max_speed: float = 10.0):
        distance_list = []
        angle_list = []

        for i in range(4):
            distance_list.append(side_length)
            angle = angle_degrees - (90 * i)
            if angle < 0:
                angle += 360
            angle_list.append(angle)

        center_direction = ((-3) * angle_degrees) + 315
        if center_direction < 0:
            angle = 360 + (angle % 360)

        start_point = (
            center_point[0]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.cos(math.radians(center_direction))
            ),
            center_point[1]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.sin(math.radians(center_direction))
            ),
        )

        super().__init__(start_point, distance_list, angle_list, max_speed)
