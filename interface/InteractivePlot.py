import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd
import configparser
from matplotlib.widgets import Button, RadioButtons
import os

# Labels para interface em português
label_dict = {
    'Circular': 'circular',
    'Angular': 'angular',
    'Trator': 'tractor',
    'Estático': 'static',
    'Quadrangular': 'square'
}

class InteractivePlot:
    """
    Classe para criar um gráfico interativo que permite ao usuário selecionar pontos em um mapa
    e gerar um arquivo de configuração baseado nos pontos selecionados.

    Parâmetros:
        xml_file (str): Caminho do arquivo XML contendo as coordenadas dos veículos.
    """

    def __init__(self, xml_file):
        """
        Inicializa a classe InteractivePlot.

        Args:
            xml_file (str): Caminho do arquivo XML.
        """
        self.xml_file = xml_file
        # Remove a extensão .xml do caminho do arquivo
        self.base_file_path = os.path.splitext(xml_file)[0]
        self.x_coords, self.y_coords = self.extract_coordinates(xml_file)
        self.min_x, self.max_x = min(self.x_coords), max(self.x_coords)
        self.min_y, self.max_y = min(self.y_coords), max(self.y_coords)
        self.saved_points = []  # Lista de tuplas: (x, y, pattern, vehicle_id)
        self.markers = []
        self.selected_pattern = "circular"  # Padrão inicial
        self.pattern_counts = {"circular": 0, "angular": 0, "tractor": 0, "static": 0, "square": 0}
        self.confirmed = False  # Flag para verificar se o botão "Confirmar" foi clicado

    def extract_coordinates(self, xml_file):
        """
        Extrai as coordenadas dos veículos de um arquivo XML.

        Args:
            xml_file (str): Caminho do arquivo XML.

        Returns:
            tuple: Duas listas contendo as coordenadas x e y dos veículos.
        """
        tree = ET.parse(xml_file)
        root = tree.getroot()
        x_coords = []
        y_coords = []

        for timestep in root.findall("timestep"):
            for vehicle in timestep.findall("vehicle"):
                x_coords.append(float(vehicle.get("x")))
                y_coords.append(float(vehicle.get("y")))

        return x_coords, y_coords

    def on_mouse_move(self, event):
        """
        Atualiza as coordenadas exibidas na interface conforme o movimento do mouse.

        Args:
            event: Evento de movimento do mouse.
        """
        if event.inaxes:
            self.text.set_text(f"x: {event.xdata:.6f}, y: {event.ydata:.6f}")
            self.fig.canvas.draw()

    def on_click(self, event):
        """
        Adiciona um ponto ao mapa quando o usuário clica em uma área válida.

        Args:
            event: Evento de clique do mouse.
        """
        # Ignora cliques fora da área do mapa ou dentro de elementos da interface
        if event.inaxes and event.inaxes not in [self.radio.ax, self.button]:
            x, y = event.xdata, event.ydata
            # Verifica se as coordenadas estão dentro dos limites do mapa
            if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
                self.saved_points.append((x, y, self.selected_pattern, None))
                marker = self.ax.scatter(x, y, color="red", s=100)
                self.markers.append(marker)
                print(f"Saved coordinates: {x:.6f},{y:.6f} with pattern: {self.selected_pattern}")
                self.fig.canvas.draw()
            else:
                print(f"Ignored click outside map area: {x:.6f},{y:.6f}")

    def on_confirm(self, event):
        """
        Fecha a interface gráfica quando o botão de confirmação é clicado.
        """
        self.confirmed = True  # Define a flag como True
        plt.close()

    def on_pattern_select(self, label):
        """
        Atualiza o padrão selecionado com base na escolha do usuário.

        Args:
            label (str): Label do padrão selecionado.
        """
        self.selected_pattern = label_dict[label]
        print(f"Selected pattern: {self.selected_pattern}")

    def generate_config(self):
        """
        Gera um arquivo de configuração (config.ini) com base nos pontos selecionados.
        """
        if not self.confirmed:
            print("Config file not generated because the 'Confirm' button was not clicked.")
            return

        config = configparser.ConfigParser()

        # Adiciona a seção Simulation
        config["Simulation"] = {
            "trace_path": self.xml_file
        }

        # Adiciona seções Drone para cada ponto clicado
        for i, (x, y, pattern, vehicle_id) in enumerate(self.saved_points, start=1):
            self.pattern_counts[pattern] += 1
            section_name = f"Drone{pattern.capitalize()}{self.pattern_counts[pattern]}"
            if pattern == "circular":
                config[section_name] = {
                    "center": f"{x:.6f}, {y:.6f}",
                    "radius_meters": "40",
                    "max_speed": "10",
                    "num_points": "12",
                    "start_angle": "0"
                }
            elif pattern == "angular":
                config[section_name] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "max_length": "40",
                    "start_angle": "0",
                    "max_turns": "3",
                    "angle_alpha": "30",
                    "max_speed": "10"
                }
            elif pattern == "tractor":
                config[section_name] = {
                    "start_point": f"{x:.6f}, {y:.6f}",
                    "width_between_tracks": "70",
                    "max_length": "100",
                    "max_turns": "6",
                    "orientation": "vertical",
                    "max_speed": "10"
                }
            elif pattern == "static":
                config[section_name] = {
                    "point": f"{x:.6f}, {y:.6f}"
                }
            elif pattern == "square":
                config[section_name] = {
                    "center_point": f"{x:.6f}, {y:.6f}",
                    "side_length": "50",
                    "angle_degrees": "90",
                    "max_speed": "10"
                }

        # Usa o base_file_path (sem .xml) para ExportXML e ExportVideo
        config["ExportXML"] = {
            "new_xml_path": f"{self.base_file_path}UAV.xml"
        }
        config["ExportVideo"] = {
            "video_directory": f"{self.base_file_path}_video",
            "only_vants": 0,
        }

        # Salva o arquivo de configuração
        with open(f"{self.base_file_path}.ini", "w") as configfile:
            config.write(configfile)
        print("Config file 'config.ini' generated.")

    def show(self):
        """
        Exibe a interface gráfica interativa.
        """
        coordinates_limits = [
            (self.min_x, self.min_y),
            (self.min_x, self.max_y),
            (self.max_x, self.max_y),
            (self.max_x, self.min_y),
            (self.min_x, self.min_y),
        ]
        polygon = Polygon(coordinates_limits)

        # Cria um GeoDataFrame com o polígono
        data = {"geometry": [polygon]}
        scenario = gpd.GeoDataFrame(data, crs="EPSG:4326")
        proportion = (self.max_x - self.min_x) / (self.max_y - self.min_y)
        self.fig, self.ax = plt.subplots(figsize=(10 * proportion, 10), dpi=100)
        scenario.plot(ax=self.ax, alpha=0)
        cx.add_basemap(
            self.ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik
        )

        # Conecta eventos
        self.cid_move = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_mouse_move
        )
        self.cid_click = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_click
        )
        self.text = self.ax.text(0.05, 0.95, "", transform=self.ax.transAxes)

        # Adiciona botões de seleção de padrão
        ax_radio = plt.axes([0.8, 0.1, 0.15, 0.2])
        self.radio = RadioButtons(ax_radio, list(label_dict.keys()))
        self.radio.on_clicked(self.on_pattern_select)

        # Adiciona botão de confirmação
        ax_button = plt.axes([0.8, 0.01, 0.1, 0.075])
        self.button = Button(ax_button, "Confirm")
        self.button.on_clicked(self.on_confirm)

        plt.show()

def run(path):
    """
    Função principal para executar a interface gráfica e gerar o arquivo de configuração.

    Args:
        path (str): Caminho do arquivo XML.
    """
    # Uso
    xml_file = path  # Substitua pelo caminho do seu arquivo XML
    interactive_plot = InteractivePlot(xml_file)
    interactive_plot.show()

    # Após fechar o gráfico, gera o arquivo de configuração
    interactive_plot.generate_config()