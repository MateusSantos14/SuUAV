import math
from typing import Tuple, List
from src.strategies.MobilityStrategy import MobilityStrategy
from src.models.Vehicle import Vehicle
from src.subsystems.VehicleManager import VehicleManager
from src.utils.conversionMeters import earth_radius, meters_to_geo

class GenericStrategy(MobilityStrategy):
    """
    Estratégia genérica de padrão de voo baseada em listas de distância e ângulos.
    """
    def __init__(self, start_point: Tuple[float, float], distance_lists: List[float], angles_list: List[float], max_speed: float = 10.0):
        self.start_point = start_point
        self.distance_lists = distance_lists
        self.angles_list = angles_list
        self.max_speed = max_speed

    def generate_trajectory(self, drone_id: str, timestep_total: int, vehicle_manager: VehicleManager) -> Vehicle:
        drone_coordinates = self._generate_generic_pattern(timestep_total)
        drone = Vehicle(drone_id, "VANT")

        for time in range(timestep_total):
            x_current, y_current, speed = drone_coordinates[time]

            if (x_current, y_current) != (0, 0):
                drone.add_timestep(str(float(time)), str(x_current), str(y_current), "0", str(round(speed, 2)), "0", "0", "0")

        return drone

    def _generate_generic_pattern(self, num_samples: int) -> List[Tuple[float, float, float]]:
        coordinates: List[Tuple[float, float, float]] = []
        lat, lon = self.start_point
        distance_per_sample: float = self.max_speed  # Distância coberta por amostra
        distance_degrees: float = distance_per_sample / earth_radius * (180 / math.pi)

        coordinates.append((lat, lon, 0.0))
        turn: int = 0
        states_number: int = len(self.distance_lists)
        distance_to_cover: float = meters_to_geo(self.distance_lists[turn]) / math.sqrt(2)
        angle_of_movement: float = self.angles_list[turn]
        distance_covered: float = 0.0
        i: int = 0

        while i < num_samples:
            while distance_covered + distance_degrees <= distance_to_cover:
                rad = math.radians(angle_of_movement)
                lat += distance_degrees * math.cos(rad)
                lon += distance_degrees * math.sin(rad)
                coordinates.append((lat, lon, self.max_speed))
                distance_covered += distance_degrees
                i += 1

            lack_distance: float = distance_to_cover - distance_covered
            if lack_distance > 0:
                rad = math.radians(angle_of_movement)
                lat += lack_distance * math.cos(rad)
                lon += lack_distance * math.sin(rad)
                turn += 1
                turn %= states_number
                acumulated: float = distance_degrees - lack_distance
                distance_to_cover = meters_to_geo(self.distance_lists[turn])
                angle_of_movement = self.angles_list[turn]
                distance_covered = 0.0
                rad = math.radians(angle_of_movement)
                lat += acumulated * math.cos(rad)
                lon += acumulated * math.sin(rad)
                distance_covered += acumulated
                coordinates.append((lat, lon, self.max_speed))
                i += 1
            else:
                turn += 1
                turn %= states_number
                distance_to_cover = meters_to_geo(self.distance_lists[turn])
                angle_of_movement = self.angles_list[turn]
                rad = math.radians(angle_of_movement)
                distance_covered = 0.0

        return coordinates
