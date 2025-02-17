from typing import Dict, Optional

class Vehicle:
    """
    A classe Vehicle é projetada para armazenar e gerenciar informações de trajetória de um veículo.

    Atributos:
    - _id (str): Identificador único do veículo.
    - _type (str): Tipo do veículo.
    - timesteps (Dict[int, Timestep]): Dicionário que armazena objetos Timestep, indexados pelo tempo (como inteiros).
    """

    def __init__(self, id: str, type: str) -> None:
        """
        Inicializa uma nova instância da classe Vehicle com o ID e tipo especificados.

        Parâmetros:
        - id (str): Identificador único do veículo.
        - type (str): Tipo do veículo.
        """
        self._id: str = id
        self._type: str = type
        self.timesteps: Dict[int, 'Timestep'] = {}

    def add_timestep(self, time: str, x: str, y: str, angle: str, speed: str, pos: str, lane: str, slope: str) -> None:
        """
        Adiciona um novo Timestep ao histórico do veículo, convertendo os valores de entrada (strings) para os tipos apropriados.

        Parâmetros:
        - time (str): Tempo do timestep.
        - x (str): Coordenada x da posição do veículo.
        - y (str): Coordenada y da posição do veículo.
        - angle (str): Ângulo de orientação do veículo.
        - speed (str): Velocidade do veículo.
        - pos (str): Indicador de posição do veículo.
        - lane (str): Faixa em que o veículo está.
        - slope (str): Inclinação da via ou do veículo.
        """
        time_int: int = int(float(time))
        timestep: 'Timestep' = Timestep(
            time_int,
            float(x),
            float(y),
            float(angle),
            float(speed),
            float(pos),
            lane,
            float(slope),
        )
        self.timesteps[timestep.time()] = timestep  # Adiciona um timestep indexado pelo tempo

    def get_timestep(self, time: int) -> Optional['Timestep']:
        """
        Retorna o objeto Timestep para um determinado tempo, se existir; caso contrário, retorna None.

        Parâmetros:
        - time (int): Tempo do timestep.

        Retorna:
        - Optional[Timestep]: Objeto Timestep ou None.
        """
        return self.timesteps.get(time)

    def get_timestep_dict(self, time: int) -> Optional[dict]:
        """
        Retorna uma representação em dicionário do Timestep para um determinado tempo, se existir; caso contrário, retorna None.

        Parâmetros:
        - time (int): Tempo do timestep.

        Retorna:
        - Optional[dict]: Dicionário com os dados do timestep ou None.
        """
        if time in self.timesteps:
            timestep: 'Timestep' = self.timesteps[time]
            return {
                "id": self.id(),
                "x": timestep.x(),
                "y": timestep.y(),
                "angle": timestep.angle(),
                "speed": timestep.speed(),
                "pos": timestep.pos(),
                "lane": timestep.lane(),
                "slope": timestep.slope(),
            }
        return None

    def print_timestep(self, time: int) -> None:
        """
        Imprime a representação em dicionário do Timestep para um determinado tempo, se existir.

        Parâmetros:
        - time (int): Tempo do timestep.
        """
        if time in self.timesteps:
            timestep: 'Timestep' = self.timesteps[time]
            print({
                "id": self.id(),
                "x": timestep.x(),
                "y": timestep.y(),
                "angle": timestep.angle(),
                "speed": timestep.speed(),
                "pos": timestep.pos(),
                "lane": timestep.lane(),
                "slope": timestep.slope(),
            })

    def is_present(self, time: int) -> bool:
        """
        Verifica se existe um Timestep para um determinado tempo.

        Parâmetros:
        - time (int): Tempo do timestep.

        Retorna:
        - bool: True se o timestep existir; False caso contrário.
        """
        return time in self.timesteps

    def id(self) -> str:
        """
        Retorna o ID do veículo.

        Retorna:
        - str: ID do veículo.
        """
        return self._id

    def type(self) -> str:
        """
        Retorna o tipo do veículo.

        Retorna:
        - str: Tipo do veículo.
        """
        return self._type


class Timestep:
    """
    A classe Timestep encapsula o estado de um veículo em um momento específico, detalhando sua posição, orientação e atributos de movimento.

    Atributos:
    - _time (int): Momento do timestep.
    - _x (float): Coordenada x da posição do veículo.
    - _y (float): Coordenada y da posição do veículo.
    - _angle (float): Ângulo de orientação do veículo.
    - _speed (float): Velocidade do veículo.
    - _pos (float): Indicador de posição do veículo.
    - _lane (str): Faixa em que o veículo está.
    - _slope (float): Inclinação da via ou do veículo.
    """

    def __init__(self, time: int, x: float, y: float, angle: float, speed: float, pos: float, lane: str, slope: float) -> None:
        """
        Inicializa um Timestep com detalhes de posição, orientação e movimento.

        Parâmetros:
        - time (int): Momento do timestep.
        - x (float): Coordenada x da posição do veículo.
        - y (float): Coordenada y da posição do veículo.
        - angle (float): Ângulo de orientação do veículo.
        - speed (float): Velocidade do veículo.
        - pos (float): Indicador de posição do veículo.
        - lane (str): Faixa em que o veículo está.
        - slope (float): Inclinação da via ou do veículo.
        """
        self._time: int = time
        self._x: float = x
        self._y: float = y
        self._angle: float = angle
        self._speed: float = speed
        self._pos: float = pos
        self._lane: str = lane
        self._slope: float = slope

    def time(self) -> int:
        """
        Retorna o momento do timestep.

        Retorna:
        - int: Momento do timestep.
        """
        return self._time

    def x(self) -> float:
        """
        Retorna a coordenada x da posição do veículo.

        Retorna:
        - float: Coordenada x.
        """
        return self._x

    def y(self) -> float:
        """
        Retorna a coordenada y da posição do veículo.

        Retorna:
        - float: Coordenada y.
        """
        return self._y

    def angle(self) -> float:
        """
        Retorna o ângulo de orientação do veículo.

        Retorna:
        - float: Ângulo de orientação.
        """
        return self._angle

    def speed(self) -> float:
        """
        Retorna a velocidade do veículo.

        Retorna:
        - float: Velocidade.
        """
        return self._speed

    def pos(self) -> float:
        """
        Retorna o indicador de posição do veículo.

        Retorna:
        - float: Indicador de posição.
        """
        return self._pos

    def lane(self) -> str:
        """
        Retorna a faixa em que o veículo está.

        Retorna:
        - str: Faixa do veículo.
        """
        return self._lane

    def slope(self) -> float:
        """
        Retorna a inclinação da via ou do veículo.

        Retorna:
        - float: Inclinação.
        """
        return self._slope