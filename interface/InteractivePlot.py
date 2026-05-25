import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd
import configparser
from matplotlib.widgets import Button, RadioButtons
import os
import time

# Labels para interface em português
label_dict = {
    'Circular': 'circular',
    'Angular': 'angular',
    'Trator': 'tractor',
    'Estático': 'static',
    'Quadrangular': 'square'
}

# Cores para cada tipo de padrão selecionado
pattern_colors = {
    "circular": "#3498db",  # Azul
    "angular": "#e67e22",   # Laranja
    "tractor": "#9b59b6",   # Roxo
    "static": "#2ecc71",    # Verde
    "square": "#e74c3c"     # Vermelho
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
        if not self.x_coords or not self.y_coords:
            raise ValueError(f"O arquivo XML '{xml_file}' não contém coordenadas ou elementos de veículos válidos.")
        self.min_x, self.max_x = min(self.x_coords), max(self.x_coords)
        self.min_y, self.max_y = min(self.y_coords), max(self.y_coords)
        self.saved_points = []  # Lista de tuplas: (x, y, pattern, vehicle_id)
        self.markers = []  # Lista de tuplas: (marker_collection, text_label)
        self.selected_pattern = "circular"  # Padrão inicial
        self.pattern_counts = {"circular": 0, "angular": 0, "tractor": 0, "static": 0, "square": 0}
        self.confirmed = False  # Flag para verificar se o botão "Confirmar" foi clicado
        self.last_draw_time = 0.0  # Para limitar a taxa de atualização no movimento do mouse

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
        if event.inaxes == self.ax:
            self.text.set_text(f"x: {event.xdata:.6f}, y: {event.ydata:.6f}")
            
            # Limita a taxa de atualização do desenho do canvas (max 10 FPS)
            # para evitar sobrecarregar o loop de eventos de renderização
            current_time = time.time()
            if current_time - self.last_draw_time > 0.1:
                self.fig.canvas.draw_idle()
                self.last_draw_time = current_time

    def on_click(self, event):
        """
        Adiciona um ponto ao mapa quando o usuário clica em uma área válida.

        Args:
            event: Evento de clique do mouse.
        """
        # Só processa cliques dentro da área principal do mapa (self.ax)
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            # Verifica se as coordenadas estão dentro dos limites do mapa
            if self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y:
                self.saved_points.append((x, y, self.selected_pattern, None))
                
                # Cor correspondente ao padrão selecionado
                color = pattern_colors.get(self.selected_pattern, "red")
                
                # Adiciona o marcador do ponto no mapa
                marker = self.ax.scatter(x, y, color=color, s=120, edgecolor="black", zorder=5)
                
                # Adiciona o rótulo de texto ordenado
                text_label = self.ax.text(
                    x, y, f" {len(self.saved_points)}", 
                    fontsize=9, fontweight="bold", color="black",
                    bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", boxstyle="round,pad=0.2"),
                    zorder=6
                )
                
                self.markers.append((marker, text_label))
                print(f"Coordenada salva: {x:.6f},{y:.6f} com padrão: {self.selected_pattern}")
                self.fig.canvas.draw()
            else:
                print(f"Clique ignorado fora da área do mapa: {x:.6f},{y:.6f}")

    def on_confirm(self, event):
        """
        Fecha a interface gráfica quando o botão de confirmação é clicado.
        """
        self.confirmed = True  # Define a flag como True
        plt.close()

    def on_undo(self, event):
        """
        Remove o último ponto adicionado ao mapa e sua correspondente marcação visual.
        """
        if self.saved_points:
            removed_point = self.saved_points.pop()
            marker, text_label = self.markers.pop()
            marker.remove()
            text_label.remove()
            print(f"Ponto desfeito: {removed_point[0]:.6f},{removed_point[1]:.6f} ({removed_point[2]})")
            self.fig.canvas.draw()
        else:
            print("Nenhum ponto para desfazer.")

    def on_pattern_select(self, label):
        """
        Atualiza o padrão selecionado com base na escolha do usuário.

        Args:
            label (str): Label do padrão selecionado.
        """
        self.selected_pattern = label_dict[label]
        print(f"Padrão selecionado: {self.selected_pattern}")

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
        print(f"Config file '{self.base_file_path}.ini' generated.")

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
        
        # Cria figura com proporções fixas adequadas e limpas para todos os monitores
        self.fig = plt.figure(figsize=(12, 8), dpi=100)
        
        # Define título amigável na barra da janela (se suportado pelo backend)
        if hasattr(self.fig.canvas, 'manager') and self.fig.canvas.manager:
            self.fig.canvas.manager.set_window_title("SuUAV - Configuração de Drones")
            
        # Adiciona eixos do mapa ocupando 70% de largura à esquerda (de 0.05 a 0.75)
        self.ax = self.fig.add_axes([0.05, 0.08, 0.70, 0.84])
        
        # Plota os limites do cenário sem preenchimento
        scenario.plot(ax=self.ax, alpha=0)
        
        # Adiciona margem de 10% nas extremidades dos limites do mapa para evitar clipping
        dx = self.max_x - self.min_x
        dy = self.max_y - self.min_y
        if dx == 0: dx = 0.001
        if dy == 0: dy = 0.001
        self.ax.set_xlim(self.min_x - dx * 0.1, self.max_x + dx * 0.1)
        self.ax.set_ylim(self.min_y - dy * 0.1, self.max_y + dy * 0.1)
        
        # Adiciona o basemap com tratamento de erro para uso offline resiliente
        try:
            cx.add_basemap(
                self.ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik
            )
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o mapa de fundo (basemap): {e}")
            print("A interface continuará sem o mapa de fundo.")

        # Conecta eventos do mouse
        self.cid_move = self.fig.canvas.mpl_connect(
            "motion_notify_event", self.on_mouse_move
        )
        self.cid_click = self.fig.canvas.mpl_connect(
            "button_press_event", self.on_click
        )
        
        # Caixa de texto com coordenadas sob o cursor
        self.text = self.ax.text(
            0.02, 0.98, "", 
            transform=self.ax.transAxes,
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.75, edgecolor='none', boxstyle='round,pad=0.3'),
            zorder=10
        )

        # Adiciona botões de seleção de padrão (RadioButtons) na barra lateral (de 0.78 a 0.96)
        ax_radio = self.fig.add_axes([0.78, 0.45, 0.18, 0.35])
        self.radio = RadioButtons(ax_radio, list(label_dict.keys()))
        self.radio.on_clicked(self.on_pattern_select)
        ax_radio.set_facecolor("#f9f9f9")

        # Adiciona botão de desfazer (Desfazer)
        ax_undo = self.fig.add_axes([0.78, 0.28, 0.18, 0.08])
        self.button_undo = Button(
            ax_undo, "Desfazer", 
            color="#fadbd8", 
            hovercolor="#ec7063"
        )
        self.button_undo.on_clicked(self.on_undo)

        # Adiciona botão de confirmação (Confirmar)
        ax_confirm = self.fig.add_axes([0.78, 0.15, 0.18, 0.08])
        self.button_confirm = Button(
            ax_confirm, "Confirmar", 
            color="#d4efdf", 
            hovercolor="#2ecc71"
        )
        self.button_confirm.on_clicked(self.on_confirm)

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