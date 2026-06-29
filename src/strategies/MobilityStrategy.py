from abc import ABC, abstractmethod
from src.models.Vehicle import Vehicle
from src.subsystems.VehicleManager import VehicleManager

class MobilityStrategy(ABC):
    """
    Classe abstrata que define a interface comum para todas as lógicas de voo.
    """
    @abstractmethod
    def generate_trajectory(self, drone_id: str, timestep_total: int, vehicle_manager: VehicleManager) -> Vehicle:
        """
        Gera a trajetória do drone com base no ID do drone, no número total de timesteps,
        e no vehicle_manager. Retorna um objeto Vehicle.
        """
        pass
