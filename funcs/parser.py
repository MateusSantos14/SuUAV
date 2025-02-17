import configparser
from ast import literal_eval
from typing import Dict, Any, List, Tuple, Optional
from src.Simulation import Simulation  # Importa a classe Simulation

def parse_config_and_run(config_file: str) -> None:
    """
    Lê o arquivo de configuração e executa as funções correspondentes.

    Args:
        config_file (str): Caminho do arquivo de configuração.

    Raises:
        ValueError: Se a seção 'Simulation' não for encontrada no arquivo de configuração.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    # Inicializa a simulação
    if "Simulation" in config:
        trace_path: str = config["Simulation"]["trace_path"]
        simulation: Simulation = Simulation(trace_path)
    else:
        raise ValueError("Section 'Simulation' not found in the configuration file.")

    # Itera sobre as seções no arquivo de configuração
    for section in config.sections():
        if section.startswith("DroneCircular"):
            # Configuração para um drone circular
            center: Tuple[float, float] = literal_eval(config[section]["center"])
            radius_meters: int = int(config[section]["radius_meters"])
            max_speed: int = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10
            start_angle: int = config[section].getint("start_angle", fallback=0)  # Valor padrão: 0

            simulation.create_drone_circular(center, radius_meters, max_speed, start_angle)
            print(f"Circular drone created with center at {center} and radius {radius_meters}m.")

        elif section.startswith("DroneAngular"):
            # Configuração para um drone angular
            start_point: Tuple[float, float] = literal_eval(config[section]["start_point"])
            max_length: int = int(config[section]["max_length"])
            start_angle: int = config[section].getint("start_angle", fallback=0)  # Valor padrão: 0
            max_turns: int = config[section].getint("max_turns", fallback=3)  # Valor padrão: 3
            angle_alpha: int = config[section].getint("angle_alpha", fallback=30)  # Valor padrão: 30
            max_speed: int = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_angular(start_point, max_length, start_angle, max_turns, angle_alpha, max_speed)
            print(f"Angular drone created with start point at {start_point}.")

        elif section.startswith("DroneTractor"):
            # Configuração para um drone trator
            start_point: Tuple[float, float] = literal_eval(config[section]["start_point"])
            width_between_tracks: int = int(config[section]["width_between_tracks"])
            max_length: int = int(config[section]["max_length"])
            max_turns: int = int(config[section]["max_turns"])
            orientation: str = config[section].get("orientation", fallback="horizontal")  # Valor padrão: "horizontal"
            max_speed: int = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_tractor(start_point, width_between_tracks, max_length, max_turns, orientation, max_speed)
            print(f"Tractor drone created with start point at {start_point}.")

        elif section.startswith("DroneStatic"):
            # Configuração para um drone estático
            point: Tuple[float, float] = literal_eval(config[section]["point"])

            simulation.create_drone_static(point)
            print(f"Static drone created at point {point}.")

        elif section.startswith("DroneSquare"):
            # Configuração para um drone quadrado
            center_point: Tuple[float, float] = literal_eval(config[section]["center_point"])
            side_length: int = int(config[section]["side_length"])
            angle_degrees: int = config[section].getint("angle_degrees", fallback=90)  # Valor padrão: 90
            max_speed: int = config[section].getint("max_speed", fallback=10)  # Valor padrão: 10

            simulation.create_drone_square(center_point, side_length, angle_degrees, max_speed)
            print(f"Square drone created with center at {center_point}.")

        elif section.startswith("DroneFollowing"):
            # Configuração para um drone seguidor
            vehicle_id: str = config[section].get("vehicle_id", fallback="0")
            offset_distance: int = config[section].getint("angle_degrees", fallback=10)
            max_speed: int = config[section].getint("angle_degrees", fallback=10)  # Valor padrão: 10

            simulation.create_drone_following(vehicle_id, offset_distance, max_speed)
            print(f"Following drone created following vehicle with id {vehicle_id}.")

        elif section == "ExportVideo":
            # Exporta a simulação para um vídeo
            video_directory: str = config[section]["video_directory"]
            limits_map: Optional[Tuple[float, float]] = literal_eval(config[section].get("limits_map", fallback="0"))  # Valor padrão: 0
            only_vants: int = config[section].getint("only_vants", fallback=0)  # Valor padrão: 0

            simulation.export_to_video(video_directory, limits_map, only_vants)
            print(f"Video exported to {video_directory}.mp4.")

        elif section == "ExportXML":
            # Exporta a simulação para um arquivo XML
            new_xml_path: str = config[section]["new_xml_path"]
            geo: int = config[section].getint("geo", fallback=1)  # Valor padrão: 1

            simulation.export_timesteps_to_xml(new_xml_path, geo)
            print(f"Simulation exported to {new_xml_path}.")

        elif section.startswith("ChangeLegend"):
            # Altera a legenda da simulação
            old_legend: str = config[section]["old_legend"]
            new_legend: str = config[section]["new_legend"]

            simulation.changeLegend(old_legend, new_legend)
            print(f"Legend changed from '{old_legend}' to '{new_legend}'.")

        elif section == "PrintVehicleInfo":
            # Imprime informações de um veículo específico
            vehicle_id: str = config[section]["vehicle_id"]

            simulation.print_all_vehicle_info(vehicle_id)

        elif section == "RemoveVehicle":
            # Remove um veículo da simulação
            vehicle_id: str = config[section]["vehicle_id"]

            simulation.removeVehicle(vehicle_id)
            print(f"Vehicle {vehicle_id} removed from the simulation.")

        else:
            # Seção não reconhecida
            print(f"Section '{section}' not recognized. Skipping.")