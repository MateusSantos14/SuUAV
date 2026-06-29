import xml.etree.ElementTree as ET
from src.subsystems.VehicleManager import VehicleManager
from src.utils.videomaker import generate_video_with_vector_coordinates_image
from src.utils.conversionMeters import convert_coordinates

class SimulationExporter:
    """
    Orquestração de exportação (delegação para XML e vídeo).
    """
    def __init__(self, trace_path: str):
        self.trace_path = trace_path

    def export_to_video(self, vehicle_manager: VehicleManager, video_directory: str, limits_map: int = 0, only_vants: int = 0) -> None:
        """
        Exporta a simulação para um vídeo.
        """
        video_directory += ".mp4"
        type_list = vehicle_manager.get_type_list()
        names = list(type_list.keys())
        vector_coordinates = [[] for _ in names]
        
        vehicles = vehicle_manager.get_all_vehicles()
        timestep_total = vehicle_manager.get_timestep_total()
        
        for vehicle_id, vehicle_object in vehicles.items():
            coordinates = []
            for i in range(int(float(timestep_total) + 1)):
                timestep = vehicle_object.get_timestep(i)
                if timestep is None:
                    coordinates.append((0, 0))
                else:
                    coordinates.append((timestep.x(), timestep.y()))
            index_in_vector_coordinates = names.index(vehicle_object.type())
            vector_coordinates[index_in_vector_coordinates].append(coordinates)
            
        names_values = list(type_list.values())
        generate_video_with_vector_coordinates_image(
            vector_coordinates, video_directory, names_values, limits_map, only_vants
        )

    def export_timesteps_to_xml(self, vehicle_manager: VehicleManager, new_xml_path: str, geo: int = 1) -> None:
        """
        Exporta os timesteps da simulação para um arquivo XML.
        """
        tree = ET.parse(self.trace_path)
        root = tree.getroot()
        timestep_total = vehicle_manager.get_timestep_total()
        vehicles = vehicle_manager.get_all_vehicles()

        for timestep in root.findall("timestep"):
            time = timestep.attrib["time"]
            for vehicle in timestep.findall("vehicle"):
                timestep.remove(vehicle)

            if int(float(time)) <= timestep_total:
                for vehicle_id, vehicle_obj in vehicles.items():
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
