import configparser
from ast import literal_eval
from typing import Dict, Any, List, Tuple, Optional
from src.facade.SimulationFacade import SimulationFacade
from src.strategies.StrategyFactory import StrategyFactory

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

    # Inicializa a simulação usando a Facade
    if "Simulation" in config:
        trace_path: str = config["Simulation"]["trace_path"]
        simulation: SimulationFacade = SimulationFacade(trace_path)
    else:
        raise ValueError("Section 'Simulation' not found in the configuration file.")

    # Itera sobre as seções no arquivo de configuração
    for section in config.sections():
        if section.startswith("DroneCircular"):
            # Configuração para um drone circular
            center: Tuple[float, float] = literal_eval(config[section]["center"])
            radius_meters: float = float(config[section]["radius_meters"])
            max_speed: float = config[section].getfloat("max_speed", fallback=10.0)
            start_angle: int = config[section].getint("start_angle", fallback=0)

            params = {
                "center": center,
                "radius_meters": radius_meters,
                "max_speed": max_speed,
                "start_angle": start_angle
            }
            strategy = StrategyFactory.create_strategy("circular", params)
            simulation.add_drone(strategy)
            print(f"Circular drone created with center at {center} and radius {radius_meters}m.")

        elif section.startswith("DroneAngular"):
            # Configuração para um drone angular
            start_point: Tuple[float, float] = literal_eval(config[section]["start_point"])
            max_length: float = float(config[section]["max_length"])
            start_angle: int = config[section].getint("start_angle", fallback=0)
            max_turns: int = config[section].getint("max_turns", fallback=3)
            angle_alpha: int = config[section].getint("angle_alpha", fallback=30)
            max_speed: float = config[section].getfloat("max_speed", fallback=10.0)

            params = {
                "start_point": start_point,
                "max_length": max_length,
                "start_angle": start_angle,
                "max_turns": max_turns,
                "angle_alpha": angle_alpha,
                "max_speed": max_speed
            }
            strategy = StrategyFactory.create_strategy("angular", params)
            simulation.add_drone(strategy)
            print(f"Angular drone created with start point at {start_point}.")

        elif section.startswith("DroneTractor"):
            # Configuração para um drone trator
            start_point: Tuple[float, float] = literal_eval(config[section]["start_point"])
            width_between_tracks: float = float(config[section]["width_between_tracks"])
            max_length: float = float(config[section]["max_length"])
            max_turns: int = config[section].getint("max_turns")
            orientation: str = config[section].get("orientation", fallback="horizontal")
            max_speed: float = config[section].getfloat("max_speed", fallback=10.0)

            params = {
                "start_point": start_point,
                "width_between_tracks": width_between_tracks,
                "max_length": max_length,
                "max_turns": max_turns,
                "orientation": orientation,
                "max_speed": max_speed
            }
            strategy = StrategyFactory.create_strategy("tractor", params)
            simulation.add_drone(strategy)
            print(f"Tractor drone created with start point at {start_point}.")

        elif section.startswith("DroneStatic"):
            # Configuração para um drone estático
            point: Tuple[float, float] = literal_eval(config[section]["point"])

            params = {
                "point": point
            }
            strategy = StrategyFactory.create_strategy("static", params)
            simulation.add_drone(strategy)
            print(f"Static drone created at point {point}.")

        elif section.startswith("DroneSquare"):
            # Configuração para um drone quadrado
            center_point: Tuple[float, float] = literal_eval(config[section]["center_point"])
            side_length: float = float(config[section]["side_length"])
            angle_degrees: int = config[section].getint("angle_degrees", fallback=90)
            max_speed: float = config[section].getfloat("max_speed", fallback=10.0)

            params = {
                "center_point": center_point,
                "side_length": side_length,
                "angle_degrees": angle_degrees,
                "max_speed": max_speed
            }
            strategy = StrategyFactory.create_strategy("square", params)
            simulation.add_drone(strategy)
            print(f"Square drone created with center at {center_point}.")

        elif section.startswith("DroneFollowing"):
            # Configuração para um drone seguidor
            vehicle_id: str = config[section].get("vehicle_id", fallback="0")
            offset_distance: float = config[section].getfloat("offset_distance", fallback=config[section].getfloat("angle_degrees", fallback=10.0))
            max_speed: float = config[section].getfloat("max_speed", fallback=config[section].getfloat("angle_degrees", fallback=10.0))

            params = {
                "vehicle_id": vehicle_id,
                "offset_distance": offset_distance,
                "max_speed": max_speed
            }
            strategy = StrategyFactory.create_strategy("following", params)
            simulation.add_drone(strategy)
            print(f"Following drone created following vehicle with id {vehicle_id}.")

        elif section == "ExportVideo":
            # Exporta a simulação para um vídeo
            video_directory: str = config[section]["video_directory"]
            limits_map: Optional[Tuple[float, float]] = literal_eval(config[section].get("limits_map", fallback="0"))
            only_vants: int = config[section].getint("only_vants", fallback=0)

            simulation.export_to_video(video_directory, limits_map, only_vants)
            print(f"Video exported to {video_directory}.mp4.")

        elif section == "ExportXML":
            # Exporta a simulação para um arquivo XML
            new_xml_path: str = config[section]["new_xml_path"]
            geo: int = config[section].getint("geo", fallback=1)

            simulation.export_timesteps_to_xml(new_xml_path, geo)
            print(f"Simulation exported to {new_xml_path}.")

        elif section.startswith("ChangeLegend"):
            # Altera a legenda da simulação
            old_legend: str = config[section]["old_legend"]
            new_legend: str = config[section]["new_legend"]

            simulation.change_legend(old_legend, new_legend)
            print(f"Legend changed from '{old_legend}' to '{new_legend}'.")

        elif section == "PrintVehicleInfo":
            # Imprime informações de um veículo específico
            vehicle_id: str = config[section]["vehicle_id"]

            simulation.print_all_vehicle_info(vehicle_id)

        elif section == "RemoveVehicle":
            # Remove um veículo da simulação
            vehicle_id: str = config[section]["vehicle_id"]

            simulation.remove_vehicle(vehicle_id)
            print(f"Vehicle {vehicle_id} removed from the simulation.")

        else:
            # Seção não reconhecida
            if section != "Simulation":
                print(f"Section '{section}' not recognized. Skipping.")