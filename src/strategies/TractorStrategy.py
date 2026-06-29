from typing import Tuple
from src.strategies.GenericStrategy import GenericStrategy

class TractorStrategy(GenericStrategy):
    """
    Estratégia de mobilidade do tipo trator (varredura).
    """
    def __init__(self, start_point: Tuple[float, float], width_between_tracks: float, max_length: float, max_turns: int, orientation: str = "horizontal", max_speed: float = 10.0):
        distance_list = []
        angle_list = []

        if orientation == "horizontal":
            start_angle = 0  # Move para a direita
        else:  # vertical
            start_angle = 90  # Move para cima
        distance_list.append(width_between_tracks)
        angle_list.append(start_angle)

        for turn in range(max_turns):
            if turn % 2 == 0:
                angle_list.append(90 - start_angle)
                distance_list.append(max_length)
            else:
                angle_list.append(270 - start_angle)
                distance_list.append(max_length)
            distance_list.append(width_between_tracks)
            angle_list.append(start_angle)
        angle_list.append(180 + start_angle)
        distance_list.append(width_between_tracks)

        for turn in range(max_turns):
            if turn % 2 == 0:
                angle_list.append(270 - start_angle)
                distance_list.append(max_length)
            else:
                angle_list.append(90 - start_angle)
                distance_list.append(max_length)
            angle_list.append(180 + start_angle)
            distance_list.append(width_between_tracks)

        super().__init__(start_point, distance_list, angle_list, max_speed)
