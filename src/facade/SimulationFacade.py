from typing import Tuple, Optional, List, Dict
from src.subsystems.VehicleManager import VehicleManager
from src.subsystems.XMLTraceReader import XMLTraceReader
from src.subsystems.SimulationExporter import SimulationExporter
from src.strategies.MobilityStrategy import MobilityStrategy

class SimulationFacade:
    """
    Fachada unificada que expõe a API simplificada (SRP) da Simulação,
    orquestrando os subsistemas XMLTraceReader, VehicleManager e SimulationExporter.
    """
    def __init__(self, trace_path: str):
        self.vehicle_manager = VehicleManager()
        self.trace_reader = XMLTraceReader(trace_path)
        self.exporter = SimulationExporter(trace_path)

        # Lê o arquivo XML de traços e popula o VehicleManager
        timestep_total = self.trace_reader.read(self.vehicle_manager)
        self.vehicle_manager.set_timestep_total(timestep_total)

    def add_drone(self, strategy: MobilityStrategy) -> None:
        """
        Cria um drone com base em uma estratégia de mobilidade e o adiciona à simulação.
        """
        drone_id = self.vehicle_manager.generate_next_drone_id()
        timestep_total = self.vehicle_manager.get_timestep_total()
        drone = strategy.generate_trajectory(drone_id, timestep_total, self.vehicle_manager)
        self.vehicle_manager.add_vehicle(drone)

    def remove_vehicle(self, vehicle_id: str) -> None:
        """
        Remove um veículo da simulação.
        """
        self.vehicle_manager.remove_vehicle(vehicle_id)

    def change_legend(self, old_legend: str, new_legend: str) -> None:
        """
        Altera a legenda de um tipo de veículo.
        """
        self.vehicle_manager.change_type_legend(old_legend, new_legend)

    def print_all_vehicle_info(self, vehicle_id: str) -> None:
        """
        Imprime todas as informações de um veículo.
        """
        vehicle = self.vehicle_manager.get_vehicle(vehicle_id)
        timestep_total = self.vehicle_manager.get_timestep_total()
        for i in range(timestep_total + 1):
            timestep = vehicle.get_timestep_dict(i)
            if timestep is not None:
                print(timestep)

    def export_to_video(self, video_directory: str, limits_map: int = 0, only_vants: int = 0) -> None:
        """
        Exporta a simulação para um vídeo.
        """
        self.exporter.export_to_video(self.vehicle_manager, video_directory, limits_map, only_vants)

    def export_timesteps_to_xml(self, new_xml_path: str, geo: int = 1) -> None:
        """
        Exporta os timesteps da simulação para um arquivo XML.
        """
        self.exporter.export_timesteps_to_xml(self.vehicle_manager, new_xml_path, geo)

    def get_timestep_total(self) -> int:
        """
        Retorna o total de timesteps da simulação.
        """
        return self.vehicle_manager.get_timestep_total()
