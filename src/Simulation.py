import xml.etree.ElementTree as ET
from xml.dom import minidom
import math
from typing import Dict, List, Tuple, Optional
from src.Vehicle import Vehicle
from src.videomaker import generate_video_with_vector_coordinates_image
from src.creating_drones import (
    create_drone_following_object,
    create_drone_static_point,
    create_drone_generic_pattern,
    meters_to_geo,
)
from src.utils.conversionMeters import convert_coordinates


class Simulation:
    """
    Classe que representa uma simulação de veículos e drones.
    Permite a leitura de um arquivo XML de traços, criação de drones e exportação de resultados.
    """

    def __init__(self, trace_path: str):
        """
        Inicializa a simulação com base no caminho do arquivo XML de traços.

        Parâmetros:
        - trace_path (str): Caminho do arquivo XML contendo os traços da simulação.
        """
        self.vehicleList: Dict[str, Vehicle] = {}  # Dicionário com todos os veículos
        self.typeList: Dict[str, str] = {}  # Dicionário com tipos de veículos
        self.typeList["VANT"] = "UAV"  # Define o tipo "VANT" como "UAV"
        self.timestep_total: int = 0  # Total de intervalos de tempo
        self.trace_path: str = trace_path  # Caminho do arquivo XML
        self.droneNumber: int = 0  # Contador de drones criados
        self.read_xml(trace_path)  # Lê o arquivo XML

    def read_xml(self, trace_path: str):
        """
        Lê o arquivo XML e popula a lista de veículos.

        Parâmetros:
        - trace_path (str): Caminho do arquivo XML.
        """
        outputxml = ET.parse(trace_path)
        timestepList = outputxml.getroot()
        for timestep in timestepList:
            timeInstant = timestep.attrib["time"]
            self.timestep_total = int(float(timeInstant))
            for timestepVehicleData in timestep:
                if timestepVehicleData.tag == "vehicle":
                    vehicleData = timestepVehicleData.attrib
                    vehicleId = vehicleData["id"]
                    vehicleX = vehicleData["x"]
                    vehicleY = vehicleData["y"]
                    vehicleAngle = vehicleData["angle"]
                    vehicleType = vehicleData["type"]
                    vehicleSpeed = vehicleData["speed"]
                    vehiclePos = vehicleData["pos"]
                    vehicleLane = vehicleData["lane"]
                    vehicleSlope = vehicleData["slope"]
                    if vehicleId not in self.vehicleList.keys():
                        self.vehicleList[vehicleId] = Vehicle(vehicleId, vehicleType)
                        if vehicleType not in self.typeList:
                            self.typeList[vehicleType] = vehicleType
                    self.vehicleList[vehicleId].add_timestep(
                        str(float(timeInstant) + 1),  # Offset para garantir IDs únicos
                        vehicleX,
                        vehicleY,
                        vehicleAngle,
                        vehicleSpeed,
                        vehiclePos,
                        vehicleLane,
                        vehicleSlope,
                    )
        self.timestep_total += 1

    def getVehicleById(self, id: str) -> Vehicle:
        """
        Retorna um veículo pelo ID.

        Parâmetros:
        - id (str): ID do veículo.

        Retorna:
        - Vehicle: Objeto do veículo.

        Lança:
        - ValueError: Se o ID não for encontrado.
        """
        if id in self.vehicleList.keys():
            return self.vehicleList[id]
        else:
            raise ValueError("ID not found in simulation.")

    def export_to_video(self, video_directory: str, limits_map: int = 0, only_vants: int = 0):
        """
        Exporta a simulação para um vídeo.

        Parâmetros:
        - video_directory (str): Diretório de saída do vídeo.
        - limits_map (Union[List[Tuple[float, float]], int]): Limites do mapa. Se 0, calcula automaticamente.
        - only_vants (int): Define se apenas drones devem ser incluídos no vídeo.
        """
        video_directory += ".mp4"
        names = list(self.typeList.keys())
        vector_coordinates = [[] for _ in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total) + 1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep is None:
                    coordinates.append((0, 0))
                else:
                    coordinates.append((timestep.x(), timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        names = list(self.typeList.values())

        generate_video_with_vector_coordinates_image(
            vector_coordinates, video_directory, names, limits_map, only_vants
        )

    def get_timestep_total(self) -> int:
        """
        Retorna o total de intervalos de tempo da simulação.

        Retorna:
        - int: Total de intervalos de tempo.
        """
        return self.timestep_total

    def export_timesteps_to_xml(self, new_xml_path: str, geo: int = 1):
        """
        Exporta os intervalos de tempo para um arquivo XML.

        Parâmetros:
        - new_xml_path (str): Caminho do arquivo XML de saída.
        - geo (int): Define se as coordenadas devem ser mantidas geográficas. Se 0 converte para valores maiores que 0.
        """
        tree = ET.parse(self.trace_path)
        root = tree.getroot()

        for timestep in root.findall("timestep"):
            time = timestep.attrib["time"]
            for vehicle in timestep.findall("vehicle"):
                timestep.remove(vehicle)

            if int(float(time)) <= self.timestep_total:
                for vehicle_id, vehicle_obj in self.vehicleList.items():
                    if vehicle_obj.is_present(int(float(time))):
                        timestep_vehicle = vehicle_obj.get_timestep(int(float(time)))
                        ET.SubElement(
                            timestep,
                            "vehicle",
                            {
                                "id": vehicle_obj.id(),
                                "x": str(timestep_vehicle.x()),
                                "y": str(timestep_vehicle.y()),
                                "angle": str(timestep_vehicle.angle()),
                                "type": vehicle_obj.type(),
                                "speed": str(timestep_vehicle.speed()),
                                "pos": str(timestep_vehicle.pos()),
                                "lane": timestep_vehicle.lane(),
                                "slope": str(timestep_vehicle.slope()),
                            },
                        )
        tree.write(new_xml_path, encoding="utf-8", xml_declaration=True)
        if geo == 0:
            convert_coordinates(new_xml_path, new_xml_path)

    def create_drone_angular(
        self, start_point: Tuple[float, float], max_length: float, start_angle: int = 0, max_turns: int = 3, angle_alpha: int = 30, max_speed: float = 10
    ):
        """
        Cria um drone com um padrão de movimento angular.

        Parâmetros:
        - start_point (Tuple[float, float]): Ponto inicial (latitude, longitude).
        - max_length (float): Comprimento máximo de cada segmento.
        - start_angle (int): Ângulo inicial de movimento.
        - max_turns (int): Número máximo de curvas.
        - angle_alpha (int): Ângulo de inclinação para as curvas.
        - max_speed (float): Velocidade máxima do drone.
        """
        self.droneNumber += 1

        distance_list = []
        angle_list = []
        for turn in range(max_turns):
            angle_list.append(start_angle + angle_alpha)
            distance_list.append(max_length)
            angle_list.append(180 - start_angle - angle_alpha)
            distance_list.append(max_length)

        for turn in range(max_turns):
            angle_list.append(start_angle - angle_alpha)
            distance_list.append(max_length)
            angle_list.append(180 + start_angle + angle_alpha)
            distance_list.append(max_length)

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_static(self, point: Tuple[float, float]):
        """
        Cria um drone estacionário em um ponto específico.

        Parâmetros:
        - point (Tuple[float, float]): Coordenadas do ponto (latitude, longitude).
        """
        self.droneNumber += 1

        drone = create_drone_static_point(
            self.timestep_total, f"drone{self.droneNumber}", point
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_following(self, vehicle_id: str, offset_distance: float, max_speed: float = 10):
        """
        Cria um drone que segue um veículo.

        Parâmetros:
        - vehicle_id (str): ID do veículo a ser seguido.
        - offset_distance (float): Distância de offset entre o drone e o veículo.
        - max_speed (float): Velocidade máxima do drone.

        Lança:
        - ValueError: Se o ID do veículo não for encontrado.
        """
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]

        self.droneNumber += 1

        drone = create_drone_following_object(
            self.timestep_total,
            f"drone{self.droneNumber}",
            vehicle,
            offset_distance,
            max_speed=max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_tractor(
        self,
        start_point: Tuple[float, float],
        width_between_tracks: float,
        max_length: float,
        max_turns: int,
        orientation: str = "horizontal",
        max_speed: float = 10,
    ):
        """
        Cria um drone com um padrão de movimento em trator.

        Parâmetros:
        - start_point (Tuple[float, float]): Ponto inicial (latitude, longitude).
        - width_between_tracks (float): Distância entre as trilhas.
        - max_length (float): Comprimento máximo de cada trilha.
        - max_turns (int): Número máximo de curvas.
        - orientation (str): Orientação do movimento ("horizontal" ou "vertical").
        - max_speed (float): Velocidade máxima do drone.
        """
        self.droneNumber += 1

        distance_list = []
        angle_list = []

        if orientation == "horizontal":
            start_angle = 0  # Move para a direita
        else:  # vertical
            start_angle = 90  # Move para cima
        distance_list.append(width_between_tracks)
        angle_list.append(start_angle)

        for turn in range(max_turns):
            if turn % 2 == 0:
                angle_list.append(90 - start_angle)
                distance_list.append(max_length)
            else:
                angle_list.append(270 - start_angle)
                distance_list.append(max_length)
            distance_list.append(width_between_tracks)
            angle_list.append(start_angle)
        angle_list.append(180 + start_angle)
        distance_list.append(width_between_tracks)

        for turn in range(max_turns):
            if turn % 2 == 0:
                angle_list.append(270 - start_angle)
                distance_list.append(max_length)
            else:
                angle_list.append(90 - start_angle)
                distance_list.append(max_length)
            angle_list.append(180 + start_angle)
            distance_list.append(width_between_tracks)

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_circular(self, center: Tuple[float, float], radius_meters: float, max_speed: float = 10, start_angle: int = 0):
        """
        Cria um drone com um padrão de movimento circular.

        Parâmetros:
        - center (Tuple[float, float]): Coordenadas do centro do círculo.
        - radius_meters (float): Raio do círculo em metros.
        - max_speed (float): Velocidade máxima do drone.
        - start_angle (int): Ângulo inicial de movimento.
        """
        self.droneNumber += 1
        omega = max_speed / radius_meters  # Velocidade angular em radianos por segundo

        # Calcula a posição inicial com base no ângulo inicial
        start_point = (
            center[0] + meters_to_geo(radius_meters) * math.cos(math.radians(start_angle)),
            center[1] + meters_to_geo(radius_meters) * math.sin(math.radians(start_angle)),
        )

        # Gera listas de distância e ângulo com base na velocidade angular
        distance_list = []
        angle_list = []

        # Número de passos para completar um círculo
        steps_per_circle = int((2 * math.pi) / omega)

        for i in range(steps_per_circle):
            theta_i = math.radians(start_angle) + omega * i  # Ângulo atual em radianos
            angle_list.append(math.degrees(theta_i))  # Armazena ângulos em graus
            distance_list.append(max_speed)  # Distância percorrida em cada passo

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_square(
        self, center_point: Tuple[float, float], side_length: float, angle_degrees: int = 90, max_speed: float = 10
    ):
        """
        Cria um drone com um padrão de movimento quadrado.

        Parâmetros:
        - center_point (Tuple[float, float]): Coordenadas do centro do quadrado.
        - side_length (float): Comprimento do lado do quadrado.
        - angle_degrees (int): Ângulo inicial de movimento.
        - max_speed (float): Velocidade máxima do drone.
        """
        self.droneNumber += 1

        distance_list = []
        angle_list = []

        for i in range(4):
            distance_list.append(side_length)
            angle = angle_degrees - (90 * i)
            if angle < 0:
                angle += 360
            angle_list.append(angle)

        center_direction = ((-3) * angle_degrees) + 315
        if center_direction < 0:
            angle = 360 + (angle % 360)
        start_point = (
            center_point[0]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.cos(math.radians(center_direction))
            ),
            center_point[1]
            - abs(
                meters_to_geo(math.sqrt(2) * side_length / 2)
                * math.sin(math.radians(center_direction))
            ),
        )

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_list,
            angle_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def create_drone_generic(
        self, start_point: Tuple[float, float], distance_lists: List[float], angles_list: List[float], max_speed: float = 10
    ):
        """
        Cria um drone com um padrão de movimento genérico.

        Parâmetros:
        - start_point (Tuple[float, float]): Ponto inicial (latitude, longitude).
        - distance_lists (List[float]): Lista de distâncias a serem percorridas.
        - angles_list (List[float]): Lista de ângulos de movimento.
        - max_speed (float): Velocidade máxima do drone.
        """
        self.droneNumber += 1

        drone = create_drone_generic_pattern(
            self.timestep_total,
            f"drone{self.droneNumber}",
            start_point,
            distance_lists,
            angles_list,
            max_speed,
        )

        self.vehicleList[f"drone{self.droneNumber}"] = drone

    def addVehicle(self, vehicle: Vehicle):
        """
        Adiciona um veículo à simulação.

        Parâmetros:
        - vehicle (Vehicle): Objeto do veículo a ser adicionado.

        Lança:
        - ValueError: Se o ID do veículo já existir.
        """
        if vehicle.id() in self.vehicleList.keys():
            raise ValueError("ID already exists.")
        else:
            self.vehicleList[vehicle.id()] = vehicle
            if vehicle.type() not in self.typeList:
                self.typeList[vehicle.type()] = vehicle.type()

    def removeVehicle(self, vehicleId: str):
        """
        Remove um veículo da simulação.

        Parâmetros:
        - vehicleId (str): ID do veículo a ser removido.

        Lança:
        - ValueError: Se o ID do veículo não existir.
        """
        if vehicleId not in self.vehicleList.keys():
            raise ValueError("ID doesn't exists.")
        else:
            del self.vehicleList[vehicleId]

    def changeLegend(self, oldLegend: str, newLegend: str):
        """
        Altera a legenda de um tipo de veículo.

        Parâmetros:
        - oldLegend (str): Legenda antiga.
        - newLegend (str): Nova legenda.

        Lança:
        - ValueError: Se a legenda antiga não existir.
        """
        if oldLegend not in self.typeList.keys():
            raise ValueError("Type does not exists")
        else:
            self.typeList[oldLegend] = newLegend

    def print_all_vehicle_info(self, vehicle_id: str):
        """
        Imprime todas as informações de um veículo.

        Parâmetros:
        - vehicle_id (str): ID do veículo.

        Lança:
        - ValueError: Se o ID do veículo não for encontrado.
        """
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]
        for i in range(self.timestep_total + 1):
            timestep = vehicle.get_timestep_dict(i)
            if timestep is not None:
                print(timestep)

    def get_vehicle_dict(self, vehicle_id: str) -> List[Optional[Dict]]:
        """
        Retorna um dicionário com todas as informações de um veículo.

        Parâmetros:
        - vehicle_id (str): ID do veículo.

        Retorna:
        - List[Optional[Dict]]: Lista de dicionários com informações de cada intervalo de tempo.

        Lança:
        - ValueError: Se o ID do veículo não for encontrado.
        """
        if vehicle_id not in self.vehicleList.keys():
            raise ValueError("ID not found in simulation.")
        vehicle = self.vehicleList[vehicle_id]
        timesteps = []
        for i in range(self.timestep_total + 1):
            timestep = vehicle.get_timestep_dict(i)
            timesteps.append(timestep)
        return timesteps

    def vector_with_all_coordinates(self) -> List[List[Tuple[float, float]]]:
        """
        Retorna um vetor com todas as coordenadas dos veículos.

        Retorna:
        - List[List[Tuple[float, float]]]: Lista de listas de coordenadas (latitude, longitude).
        """
        names = list(self.typeList.keys())
        vector_coordinates = [[] for _ in names]
        for vehicle_id in self.vehicleList.keys():
            coordinates = []
            vehicle_object = self.vehicleList[vehicle_id]
            for i in range(int(float(self.timestep_total) + 1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep is None:
                    coordinates.append((0, 0))
                else:
                    coordinates.append((timestep.x(), timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
        return vector_coordinates