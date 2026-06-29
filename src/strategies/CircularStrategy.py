import math
from typing import Tuple
from src.strategies.GenericStrategy import GenericStrategy
from src.utils.conversionMeters import meters_to_geo

class CircularStrategy(GenericStrategy):
    """
    Estratégia de voo circular.
    """
    def __init__(self, center: Tuple[float, float], radius_meters: float, max_speed: float = 10.0, start_angle: int = 0):
        omega = max_speed / radius_meters  # Velocidade angular em radianos por segundo

        # Calcula a posição inicial com base no ângulo inicial
        start_point = (
            center[0] + meters_to_geo(radius_meters) * math.cos(math.radians(start_angle)),
            center[1] + meters_to_geo(radius_meters) * math.sin(math.radians(start_angle)),
        )

        distance_list = []
        angle_list = []

        # Número de passos para completar um círculo
        steps_per_circle = int((2 * math.pi) / omega)

        for i in range(steps_per_circle):
            theta_i = math.radians(start_angle) + omega * i  # Ângulo atual em radianos
            angle_list.append(math.degrees(theta_i))  # Armazena ângulos em graus
            distance_list.append(max_speed)  # Distância percorrida em cada passo

        super().__init__(start_point, distance_list, angle_list, max_speed)
