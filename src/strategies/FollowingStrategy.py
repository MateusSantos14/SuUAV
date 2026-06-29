import math
from typing import Tuple, List
from src.strategies.MobilityStrategy import MobilityStrategy
from src.models.Vehicle import Vehicle
from src.subsystems.VehicleManager import VehicleManager
from src.utils.conversionMeters import haversine_distance, calculate_angle, limit_speed, earth_radius

class FollowingStrategy(MobilityStrategy):
    """
    Estratégia de seguir um veículo específico.
    """
    def __init__(self, vehicle_id: str, offset_distance: float, max_speed: float = 10.0):
        self.vehicle_id = vehicle_id
        self.offset_distance = offset_distance
        self.max_speed = max_speed

    def generate_trajectory(self, drone_id: str, timestep_total: int, vehicle_manager: VehicleManager) -> Vehicle:
        if not vehicle_manager.has_vehicle(self.vehicle_id):
            raise ValueError(f"Vehicle ID '{self.vehicle_id}' not found in simulation.")
        vehicle = vehicle_manager.get_vehicle(self.vehicle_id)

        # Get positions of target vehicle
        vehicle_data = [vehicle.get_timestep_dict(i) for i in range(timestep_total + 1)]
        coordinates = [(data["x"], data["y"]) if data else (0, 0) for data in vehicle_data]

        # Generate drone coordinates following the vehicle
        drone_coordinates = self._generate_drone_coordinates(coordinates)
        drone = Vehicle(drone_id, "VANT")
        first = True

        for time in range(timestep_total + 1):
            x_current, y_current, speed = drone_coordinates[time]
            if (x_current, y_current) != (0, 0):
                drone.add_timestep(str(float(time)), str(x_current), str(y_current), "0", str(round(speed, 2)), "0", "0", "0")
                if first:
                    for time_in in range(time):
                        drone.add_timestep(str(float(time_in)), str(x_current), str(y_current), "0", str(round(speed, 2)), "0", "0", "0")
                    first = False

        return drone

    def _generate_drone_coordinates(self, vehicle_coordinates: List[Tuple[float, float]], smoothing_factor: float = 0.4) -> List[Tuple[float, float, float]]:
        drone_coordinates: List[Tuple[float, float, float]] = []
        first_non_zero_coordinate: bool = False
        previous_time: int = 0

        for i, vehicle_position in enumerate(vehicle_coordinates):
            current_time = i

            if vehicle_position != (0, 0) and not first_non_zero_coordinate:
                first_non_zero_coordinate = True
                drone_coordinates.append((vehicle_position[0], vehicle_position[1], 0.0))
                previous_time = current_time
                continue

            if vehicle_position == (0, 0):
                drone_coordinates.append((0.0, 0.0, 0.0))
                continue

            if i < len(vehicle_coordinates) - 1:
                angle = calculate_angle(vehicle_coordinates[i], vehicle_coordinates[i + 1])
            else:
                angle = calculate_angle(vehicle_coordinates[i - 1], vehicle_coordinates[i])

            if angle is None and i > 0:
                drone_coordinates.append(drone_coordinates[-1])
            else:
                lat = vehicle_position[0] - (self.offset_distance / earth_radius) * (180 / math.pi) * math.cos(angle)
                lon = vehicle_position[1] - (self.offset_distance / earth_radius) * (180 / math.pi) / math.cos(math.radians(vehicle_position[0])) * math.sin(angle)

                current_lat, current_lon, _ = drone_coordinates[-1]
                smoothed_lat = current_lat + smoothing_factor * (lat - current_lat)
                smoothed_lon = current_lon + smoothing_factor * (lon - current_lon)

                next_drone_position = (smoothed_lat, smoothed_lon)
                limited_drone_position = limit_speed((current_lat, current_lon), next_drone_position, self.max_speed)

                # Calcula a velocidade
                distance = haversine_distance(current_lat, current_lon, limited_drone_position[0], limited_drone_position[1])
                speed = distance / (current_time - previous_time) if (current_time - previous_time) > 0 else 0.0
                speed = round(speed, 2)

                drone_coordinates.append((limited_drone_position[0], limited_drone_position[1], speed))
                previous_time = current_time

        return drone_coordinates
