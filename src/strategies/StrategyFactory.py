from typing import Dict, Any
from src.strategies.MobilityStrategy import MobilityStrategy
from src.strategies.CircularStrategy import CircularStrategy
from src.strategies.TractorStrategy import TractorStrategy
from src.strategies.AngularStrategy import AngularStrategy
from src.strategies.StaticStrategy import StaticStrategy
from src.strategies.SquareStrategy import SquareStrategy
from src.strategies.FollowingStrategy import FollowingStrategy
from src.strategies.GenericStrategy import GenericStrategy

class StrategyFactory:
    """
    Fábrica dinâmica que lê a configuração e instancia a estratégia.
    """
    @staticmethod
    def create_strategy(strategy_type: str, params: Dict[str, Any]) -> MobilityStrategy:
        strategy_type_lower = strategy_type.lower()
        if "circular" in strategy_type_lower:
            return CircularStrategy(
                center=params["center"],
                radius_meters=params["radius_meters"],
                max_speed=params.get("max_speed", 10.0),
                start_angle=params.get("start_angle", 0)
            )
        elif "angular" in strategy_type_lower:
            return AngularStrategy(
                start_point=params["start_point"],
                max_length=params["max_length"],
                start_angle=params.get("start_angle", 0),
                max_turns=params.get("max_turns", 3),
                angle_alpha=params.get("angle_alpha", 30),
                max_speed=params.get("max_speed", 10.0)
            )
        elif "tractor" in strategy_type_lower:
            return TractorStrategy(
                start_point=params["start_point"],
                width_between_tracks=params["width_between_tracks"],
                max_length=params["max_length"],
                max_turns=params["max_turns"],
                orientation=params.get("orientation", "horizontal"),
                max_speed=params.get("max_speed", 10.0)
            )
        elif "static" in strategy_type_lower:
            return StaticStrategy(
                point=params["point"]
            )
        elif "square" in strategy_type_lower:
            return SquareStrategy(
                center_point=params["center_point"],
                side_length=params["side_length"],
                angle_degrees=params.get("angle_degrees", 90),
                max_speed=params.get("max_speed", 10.0)
            )
        elif "following" in strategy_type_lower:
            return FollowingStrategy(
                vehicle_id=params["vehicle_id"],
                offset_distance=params.get("offset_distance", 10.0),
                max_speed=params.get("max_speed", 10.0)
            )
        elif "generic" in strategy_type_lower:
            return GenericStrategy(
                start_point=params["start_point"],
                distance_lists=params["distance_lists"],
                angles_list=params["angles_list"],
                max_speed=params.get("max_speed", 10.0)
            )
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
