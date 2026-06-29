import xml.etree.ElementTree as ET
from src.subsystems.VehicleManager import VehicleManager
from src.models.Vehicle import Vehicle

class XMLTraceReader:
    """
    Leitura e parsing do arquivo XML de traços do SUMO.
    """
    def __init__(self, trace_path: str):
        self.trace_path = trace_path

    def read(self, vehicle_manager: VehicleManager) -> int:
        """
        Lê o arquivo XML de traços e popula a lista de veículos no VehicleManager.
        Retorna o timestep total da simulação.
        """
        outputxml = ET.parse(self.trace_path)
        timestep_list = outputxml.getroot()
        timestep_total = 0
        for timestep in timestep_list:
            time_instant = timestep.attrib["time"]
            timestep_total = int(float(time_instant))
            for timestep_vehicle_data in timestep:
                if timestep_vehicle_data.tag == "vehicle":
                    vehicle_data = timestep_vehicle_data.attrib
                    vehicle_id = vehicle_data["id"]
                    vehicle_x = vehicle_data["x"]
                    vehicle_y = vehicle_data["y"]
                    vehicle_angle = vehicle_data["angle"]
                    vehicle_type = vehicle_data["type"]
                    vehicle_speed = vehicle_data["speed"]
                    vehicle_pos = vehicle_data["pos"]
                    vehicle_lane = vehicle_data["lane"]
                    vehicle_slope = vehicle_data["slope"]
                    
                    if not vehicle_manager.has_vehicle(vehicle_id):
                        vehicle_manager.add_vehicle(Vehicle(vehicle_id, vehicle_type))
                    
                    vehicle_manager.get_vehicle(vehicle_id).add_timestep(
                        str(float(time_instant) + 1),  # Offset para garantir IDs únicos
                        vehicle_x,
                        vehicle_y,
                        vehicle_angle,
                        vehicle_speed,
                        vehicle_pos,
                        vehicle_lane,
                        vehicle_slope,
                    )
        return timestep_total + 1
