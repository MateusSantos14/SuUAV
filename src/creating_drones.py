import math
from typing import List, Tuple, Optional
from src.Vehicle import Vehicle

# Raio da Terra em metros
earth_radius: float = 6371000

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância do círculo máximo entre dois pontos na superfície da Terra
    com base em suas latitudes e longitudes.

    Parâmetros:
    - lat1 (float): Latitude do primeiro ponto em graus.
    - lon1 (float): Longitude do primeiro ponto em graus.
    - lat2 (float): Latitude do segundo ponto em graus.
    - lon2 (float): Longitude do segundo ponto em graus.

    Retorna:
    - float: Distância entre os dois pontos em metros.
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius * c


def calculate_angle(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calcula o ângulo de direção entre dois pontos na superfície da Terra.

    Parâmetros:
    - p1 (Tuple[float, float]): Tupla contendo a latitude e longitude do primeiro ponto.
    - p2 (Tuple[float, float]): Tupla contendo a latitude e longitude do segundo ponto.

    Retorna:
    - float: Ângulo de direção em radianos.
    """
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    angle = math.atan2(x, y)
    return angle


def limit_speed(start_point: Tuple[float, float], end_point: Tuple[float, float], max_distance: float) -> Tuple[float, float]:
    """
    Limita a distância entre dois pontos a um valor máximo, preservando a direção.

    Parâmetros:
    - start_point (Tuple[float, float]): Ponto inicial (latitude, longitude).
    - end_point (Tuple[float, float]): Ponto final (latitude, longitude).
    - max_distance (float): Distância máxima permitida em metros.

    Retorna:
    - Tuple[float, float]: Novo ponto ajustado para não exceder a distância máxima.
    """
    distance = haversine_distance(start_point[0], start_point[1], end_point[0], end_point[1])
    if distance > max_distance:
        ratio = max_distance / distance
        lat = start_point[0] + (end_point[0] - start_point[0]) * ratio
        lon = start_point[1] + (end_point[1] - start_point[1]) * ratio
        return (lat, lon)
    else:
        return end_point


def generate_drone_coordinates(
    vehicle_coordinates: List[Tuple[float, float]],
    offset_distance: float,
    max_speed: float,
    smoothing_factor: float = 0.4
) -> List[Tuple[float, float, float]]:
    """
    Gera coordenadas para o drone com base nas coordenadas do veículo e na distância de offset.

    Parâmetros:
    - vehicle_coordinates (List[Tuple[float, float]]): Lista de coordenadas (latitude, longitude) do veículo.
    - offset_distance (float): Distância entre o veículo e o drone em metros.
    - max_speed (float): Velocidade máxima do drone em metros por segundo.
    - smoothing_factor (float): Fator de suavização para movimentos suaves. Valor entre 0 e 1.

    Retorna:
    - List[Tuple[float, float, float]]: Lista de coordenadas (latitude, longitude, velocidade) para o drone.
    """
    drone_coordinates: List[Tuple[float, float, float]] = []
    first_non_zero_coordinate: bool = False
    previous_time: int = 0

    for i, vehicle_position in enumerate(vehicle_coordinates):
        current_time = i

        if vehicle_position != (0, 0) and not first_non_zero_coordinate:
            first_non_zero_coordinate = True
            drone_coordinates.append((vehicle_position[0], vehicle_position[1], 0))
            previous_time = current_time
            continue

        if vehicle_position == (0, 0):
            drone_coordinates.append((0, 0, 0))
            continue

        if i < len(vehicle_coordinates) - 1:
            angle = calculate_angle(vehicle_coordinates[i], vehicle_coordinates[i + 1])
        else:
            angle = calculate_angle(vehicle_coordinates[i - 1], vehicle_coordinates[i])

        if angle is None and i > 0:
            drone_coordinates.append(drone_coordinates[-1])
        else:
            lat = vehicle_position[0] - (offset_distance / earth_radius) * (180 / math.pi) * math.cos(angle)
            lon = vehicle_position[1] - (offset_distance / earth_radius) * (180 / math.pi) / math.cos(math.radians(vehicle_position[0])) * math.sin(angle)

            current_lat, current_lon, _ = drone_coordinates[-1]
            smoothed_lat = current_lat + smoothing_factor * (lat - current_lat)
            smoothed_lon = current_lon + smoothing_factor * (lon - current_lon)

            next_drone_position = (smoothed_lat, smoothed_lon)
            limited_drone_position = limit_speed((current_lat, current_lon), next_drone_position, max_speed)

            # Calcula a velocidade
            distance = haversine_distance(current_lat, current_lon, limited_drone_position[0], limited_drone_position[1])
            speed = distance / (current_time - previous_time)
            speed = round(speed, 2)

            drone_coordinates.append((limited_drone_position[0], limited_drone_position[1], speed))
            previous_time = current_time

    return drone_coordinates


def generate_drone_coordinates_static(point: Tuple[float, float], num_samples: int) -> List[Tuple[float, float, float]]:
    """
    Gera coordenadas discretas para o drone girando em torno de um ponto específico na Terra.

    Parâmetros:
    - point (Tuple[float, float]): Coordenadas do centro (latitude, longitude) em graus.
    - num_samples (int): Número de amostras discretas a serem geradas.

    Retorna:
    - List[Tuple[float, float, float]]: Lista de coordenadas (latitude, longitude, velocidade) do drone.
    """
    lat_center, lon_center = point
    coordinates: List[Tuple[float, float, float]] = []

    for i in range(num_samples):
        coordinates.append((lat_center, lon_center, 0))

    return coordinates


def generate_generic_pattern(
    start_point: Tuple[float, float],
    distance_lists: List[float],
    angles_list: List[float],
    num_samples: int,
    max_speed: float
) -> List[Tuple[float, float, float]]:
    """
    Gera coordenadas para um padrão de mobilidade genérico.

    Parâmetros:
    - start_point (Tuple[float, float]): Coordenadas iniciais (latitude, longitude).
    - distance_lists (List[float]): Lista de distâncias a serem percorridas em cada estado.
    - angles_list (List[float]): Lista de ângulos de movimento para cada estado.
    - num_samples (int): Número de amostras a serem geradas.
    - max_speed (float): Velocidade máxima do drone em metros por segundo.

    Retorna:
    - List[Tuple[float, float, float]]: Lista de coordenadas (latitude, longitude, velocidade) para o padrão de mobilidade.
    """
    coordinates: List[Tuple[float, float, float]] = []
    lat, lon = start_point
    distance_per_sample: float = max_speed  # Distância coberta por amostra

    distance_degrees: float = distance_per_sample / earth_radius * (180 / math.pi)

    coordinates.append((lat, lon, 0))
    turn: int = 0
    states_number: int = len(distance_lists)
    distance_to_cover: float = meters_to_geo(distance_lists[turn]) / math.sqrt(2)
    angle_of_movement: float = angles_list[turn]
    distance_covered: float = 0
    i: int = 0

    while i < num_samples:
        while distance_covered + distance_degrees <= distance_to_cover:
            rad = math.radians(angle_of_movement)
            lat += distance_degrees * math.cos(rad)
            lon += distance_degrees * math.sin(rad)
            coordinates.append((lat, lon, max_speed))
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
            distance_to_cover = meters_to_geo(distance_lists[turn])
            angle_of_movement = angles_list[turn]
            distance_covered = 0
            rad = math.radians(angle_of_movement)
            lat += acumulated * math.cos(rad)
            lon += acumulated * math.sin(rad)
            distance_covered += acumulated
            coordinates.append((lat, lon, max_speed))
            i += 1
        else:
            turn += 1
            turn %= states_number
            distance_to_cover = meters_to_geo(distance_lists[turn])
            angle_of_movement = angles_list[turn]
            rad = math.radians(angle_of_movement)
            distance_covered = 0

    return coordinates


def create_drone_static_point(timesteps: int, drone_id: str, point: Tuple[float, float]) -> Vehicle:
    """
    Cria um drone estacionário em um ponto específico.

    Parâmetros:
    - timesteps (int): Número de intervalos de tempo.
    - drone_id (str): Identificador do drone.
    - point (Tuple[float, float]): Coordenadas do ponto (latitude, longitude).

    Retorna:
    - Vehicle: Objeto do drone com as coordenadas definidas.
    """
    drone_coordinates = generate_drone_coordinates_static(point, timesteps)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]

        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone


def create_drone_following_object(
    timesteps: int,
    drone_id: str,
    vehicle: Vehicle,
    offset_distance: float,
    max_speed: float
) -> Vehicle:
    """
    Cria um drone que segue um objeto móvel.

    Parâmetros:
    - timesteps (int): Número de intervalos de tempo.
    - drone_id (str): Identificador do drone.
    - vehicle (Vehicle): Objeto do veículo a ser seguido.
    - offset_distance (float): Distância de offset entre o drone e o veículo.
    - max_speed (float): Velocidade máxima do drone.

    Retorna:
    - Vehicle: Objeto do drone com as coordenadas definidas.
    """
    vehicle_data = [vehicle.get_timestep_dict(i) for i in range(timesteps + 1)]
    coordinates = [(data["x"], data["y"]) if data else (0, 0) for data in vehicle_data]

    drone_coordinates = generate_drone_coordinates(coordinates, offset_distance, max_speed)
    drone = Vehicle(drone_id, "VANT")

    first = True

    for time in range(timesteps + 1):
        x_current, y_current, speed = drone_coordinates[time]

        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")
            if first:
                for timeIn in range(time):
                    drone.add_timestep(timeIn, x_current, y_current, "0", round(speed, 2), "0", "0", "0")
                first = False

    return drone


def create_drone_generic_pattern(
    timesteps: int,
    drone_id: str,
    start_point: Tuple[float, float],
    distance_lists: List[float],
    angles_list: List[float],
    max_speed: float
) -> Vehicle:
    """
    Cria um drone com um padrão de mobilidade genérico.

    Parâmetros:
    - timesteps (int): Número de intervalos de tempo.
    - drone_id (str): Identificador do drone.
    - start_point (Tuple[float, float]): Coordenadas iniciais (latitude, longitude).
    - distance_lists (List[float]): Lista de distâncias a serem percorridas em cada estado.
    - angles_list (List[float]): Lista de ângulos de movimento para cada estado.
    - max_speed (float): Velocidade máxima do drone.

    Retorna:
    - Vehicle: Objeto do drone com as coordenadas definidas.
    """
    drone_coordinates = generate_generic_pattern(start_point, distance_lists, angles_list, timesteps, max_speed)
    drone = Vehicle(drone_id, "VANT")

    for time in range(timesteps):
        x_current, y_current, speed = drone_coordinates[time]

        if (x_current, y_current) != (0, 0):
            drone.add_timestep(time, x_current, y_current, "0", round(speed, 2), "0", "0", "0")

    return drone


def meters_to_geo(a: float) -> float:
    """
    Converte metros para graus geográficos.

    Parâmetros:
    - a (float): Distância em metros.

    Retorna:
    - float: Distância em graus geográficos.
    """
    return a / earth_radius * (180 / math.pi)


def geo_to_meters(a: float) -> float:
    """
    Converte graus geográficos para metros.

    Parâmetros:
    - a (float): Distância em graus geográficos.

    Retorna:
    - float: Distância em metros.
    """
    return a * earth_radius * (math.pi / 180)