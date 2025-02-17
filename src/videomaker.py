import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import contextily as cx
from shapely.geometry import Polygon
import geopandas as gpd
from typing import List, Tuple, Union
from matplotlib.collections import PathCollection

def _create_dataframe_optimized(
    vector_coordinates: List[List[List[Tuple[float, float]]]],
    limits_map: Union[List[Tuple[float, float]], int] = 0
) -> Tuple[gpd.GeoDataFrame, float]:
    """
    Cria um GeoDataFrame otimizado a partir de coordenadas vetoriais ou limites de mapa.

    Parâmetros:
    - vector_coordinates (List[List[List[Tuple[float, float]]]): Lista de coordenadas dos veículos.
    - limits_map (Union[List[Tuple[float, float]], int]): Limites do mapa. Se 0, calcula automaticamente.

    Retorna:
    - Tuple[gpd.GeoDataFrame, float]: GeoDataFrame contendo o polígono do cenário e a proporção entre largura e altura.
    """
    if limits_map == 0:
        # Extrai coordenadas válidas (diferentes de (0, 0)) de forma vetorizada
        coords = np.array([
            (x, y) for vehicle_list in vector_coordinates
            for vehicle_coords_list in vehicle_list
            for x, y in vehicle_coords_list if (x, y) != (0, 0)
        ])
        if coords.size == 0:
            raise ValueError("Nenhuma coordenada válida encontrada.")
    else:
        coords = np.array(limits_map)
        if coords.shape[1] != 2:
            raise ValueError("Cada coordenada deve ser uma tupla (x, y).")

    # Calcula os limites mínimo e máximo das coordenadas
    min_coords = np.min(coords, axis=0)
    max_coords = np.max(coords, axis=0)
    
    # Cria um polígono retangular com base nos limites
    polygon = Polygon(np.array([
        [min_coords[0], min_coords[1]],
        [min_coords[0], max_coords[1]],
        [max_coords[0], max_coords[1]],
        [max_coords[0], min_coords[1]],
        [min_coords[0], min_coords[1]]
    ]))

    # Retorna o GeoDataFrame e a proporção entre largura e altura
    return gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:4326"), (max_coords[0] - min_coords[0]) / (max_coords[1] - min_coords[1])

def generate_video_with_vector_coordinates_image(
    vector_coordinates: List[List[List[Tuple[float, float]]]],
    directory_video: str,
    names: List[str] = [],
    limits_map: Union[List[Tuple[float, float]], int] = 0,
    only_vants: int = 0
) -> None:
    """
    Gera um vídeo animado com base nas coordenadas vetoriais dos veículos.

    Parâmetros:
    - vector_coordinates (List[List[List[Tuple[float, float]]]): Lista de coordenadas dos veículos.
    - directory_video (str): Caminho onde o vídeo será salvo.
    - names (List[str]): Nomes dos veículos para a legenda.
    - limits_map (Union[List[Tuple[float, float]], int]): Limites do mapa. Se 0, calcula automaticamente.
    - only_vants (int): Se 1, considera apenas os UAVs
    """
    # Pré-processamento dos dados (se apenas um veículo for considerado)
    if only_vants == 1:
        vector_coordinates = [vector_coordinates[0]]
        names = [names[0]]

    # Cria o cenário (GeoDataFrame) e calcula a proporção
    scenario, proportion = _create_dataframe_optimized(vector_coordinates, limits_map)

    # Lista de cores para os veículos
    colors = [
        "red", "blue", "green", "orange", "purple", "#8B0000", "#FF6347",
        "crimson", "navy", "#87CEEB", "royalblue", "#228B22", "#00FF00",
        "olive", "#FF8C00", "#FFBF00", "coral", "violet", "lavender", "magenta"
    ]
    
    # Desempacota as coordenadas e atribui cores com base no tipo de veículo
    coordinates_list = []
    color_list = []
    for i in range(len(vector_coordinates)):
        for j in range(len(vector_coordinates[i])):
            coordinates_list.append(vector_coordinates[i][j])
            color_list.append(colors[i % len(colors)])  # Atribui cor com base no tipo de veículo

    # Configura a figura com tamanho proporcional ao cenário
    fig, ax = plt.subplots(figsize=(10 * proportion, 10), dpi=75)
    plt.ioff()  # Desativa o modo interativo do matplotlib

    # Transforma a geometria do cenário para melhor desempenho
    scenario["geometry"] = scenario["geometry"].apply(
        lambda geom: Polygon(np.array(geom.exterior.coords))
    )
    scenario.plot(ax=ax, alpha=0)  # Plota o cenário sem preenchimento

    # Cria a legenda de forma eficiente
    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="w", label=names[i],
                  markerfacecolor=colors[i], markersize=10)
        for i in range(len(names))
    ]
    ax.legend(handles=legend_handles, loc="upper left")  # Adiciona a legenda

    # Adiciona um mapa de fundo (basemap)
    cx.add_basemap(ax, crs=scenario.crs, source=cx.providers.OpenStreetMap.Mapnik)

    # Pré-aloca o gráfico de dispersão (scatter plot)
    num_points = len(coordinates_list)
    points = ax.scatter(np.zeros(num_points), np.zeros(num_points), color=color_list, marker="o", s=20)

    # Pré-computa as coordenadas para todos os frames
    total_frames = len(coordinates_list[0])
    coordinates_array = np.array([
        [(point[frame][0], point[frame][1]) for point in coordinates_list]
        for frame in range(total_frames)
    ])

    def update(frame: int) -> Tuple[PathCollection]:
        """
        Atualiza a posição dos pontos no gráfico para cada frame.

        Parâmetros:
        - frame (int): Número do frame atual.

        Retorna:
        - Tuple[plt.PathCollection]: Objeto de pontos atualizado.
        """
        points.set_offsets(coordinates_array[frame])
        if frame % 10 == 0:  # Reduz a frequência de atualizações de progresso
            print(f"{round(frame / total_frames * 100, 2)}%")
        return (points,)

    # Configura a animação com otimizações
    ani = FuncAnimation(
        fig,
        update,
        frames=range(total_frames),
        interval=100,
        blit=True,
        cache_frame_data=False  # Reduz o uso de memória
    )

    # Salva o vídeo com configurações otimizadas
    ani.save(
        directory_video,
        writer='ffmpeg',
        fps=10,
        dpi=75,
        bitrate=-1,  # Permite que o ffmpeg determine a taxa de bits ideal
        extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p']
    )
    
    plt.close(fig)  # Fecha a figura para liberar memória