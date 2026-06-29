from typing import Dict, List, Optional
from src.models.Vehicle import Vehicle

class VehicleManager:
    """
    Gerência de estado, timesteps e geração dos sequenciais drone_ids.
    """
    def __init__(self):
        self.vehicle_list: Dict[str, Vehicle] = {}
        self.type_list: Dict[str, str] = {"VANT": "UAV"}
        self.timestep_total: int = 0
        self.drone_number: int = 0

    def add_vehicle(self, vehicle: Vehicle) -> None:
        if vehicle.id() in self.vehicle_list:
            raise ValueError(f"Vehicle with ID '{vehicle.id()}' already exists.")
        self.vehicle_list[vehicle.id()] = vehicle
        if vehicle.type() not in self.type_list:
            self.type_list[vehicle.type()] = vehicle.type()

    def remove_vehicle(self, vehicle_id: str) -> None:
        if vehicle_id not in self.vehicle_list:
            raise ValueError(f"Vehicle with ID '{vehicle_id}' does not exist.")
        del self.vehicle_list[vehicle_id]

    def has_vehicle(self, vehicle_id: str) -> bool:
        return vehicle_id in self.vehicle_list

    def get_vehicle(self, vehicle_id: str) -> Vehicle:
        if vehicle_id not in self.vehicle_list:
            raise ValueError(f"Vehicle with ID '{vehicle_id}' not found.")
        return self.vehicle_list[vehicle_id]

    def get_all_vehicles(self) -> Dict[str, Vehicle]:
        return self.vehicle_list

    def get_type_list(self) -> Dict[str, str]:
        return self.type_list

    def change_type_legend(self, old_legend: str, new_legend: str) -> None:
        if old_legend not in self.type_list:
            raise ValueError(f"Type '{old_legend}' does not exist.")
        self.type_list[old_legend] = new_legend

    def get_timestep_total(self) -> int:
        return self.timestep_total

    def set_timestep_total(self, total: int) -> None:
        self.timestep_total = total

    def generate_next_drone_id(self) -> str:
        self.drone_number += 1
        return f"drone{self.drone_number}"
