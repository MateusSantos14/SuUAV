from typing import Tuple
from src.strategies.MobilityStrategy import MobilityStrategy
from src.models.Vehicle import Vehicle
from src.subsystems.VehicleManager import VehicleManager

class StaticStrategy(MobilityStrategy):
    """
    Estratégia de drone estacionário.
    """
    def __init__(self, point: Tuple[float, float]):
        self.point = point

    def generate_trajectory(self, drone_id: str, timestep_total: int, vehicle_manager: VehicleManager) -> Vehicle:
        drone = Vehicle(drone_id, "VANT")
        lat, lon = self.point
        for time in range(timestep_total):
            drone.add_timestep(str(float(time)), str(lat), str(lon), "0", "0.0", "0", "0", "0")
        return drone
