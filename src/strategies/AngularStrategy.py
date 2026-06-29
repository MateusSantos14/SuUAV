from typing import Tuple
from src.strategies.GenericStrategy import GenericStrategy

class AngularStrategy(GenericStrategy):
    """
    Estratégia de mobilidade angular.
    """
    def __init__(self, start_point: Tuple[float, float], max_length: float, start_angle: int = 0, max_turns: int = 3, angle_alpha: int = 30, max_speed: float = 10.0):
        distance_list = []
        angle_list = []
        for turn in range(max_turns):
            angle_list.append(start_angle + angle_alpha)
            distance_list.append(max_length)
            angle_list.append(180 - start_angle - angle_alpha)
            distance_list.append(max_length)

        for turn in range(max_turns):
            angle_list.append(start_angle - angle_alpha)
            distance_list.append(max_length)
            angle_list.append(180 + start_angle + angle_alpha)
            distance_list.append(max_length)

        super().__init__(start_point, distance_list, angle_list, max_speed)
