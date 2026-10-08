"""Sports Assessment Factory Registry.

Facilitates runtime resolution of sport assessment strategies (Plugin/Strategy pattern).
"""
from typing import Dict, Type, Any
from app.sports.base import BaseSportAssessment
from app.sports.squat import SquatAssessment
from app.sports.pushup import PushupAssessment
from app.sports.vertical_jump import VerticalJumpAssessment
from app.config import SPORT_CONFIGS


class SportAssessmentFactory:
    """Factory to instantiate sport assessment strategies."""

    _registry: Dict[str, Type[BaseSportAssessment]] = {
        "squat": SquatAssessment,
        "pushup": PushupAssessment,
        "vertical_jump": VerticalJumpAssessment,
    }

    @classmethod
    def register(cls, sport_name: str, assessment_cls: Type[BaseSportAssessment]):
        """Register a new sport assessment class dynamically."""
        cls._registry[sport_name.lower()] = assessment_cls

    @classmethod
    def get_strategy(cls, sport_name: str, fps: float = 30.0) -> BaseSportAssessment:
        """Instantiate the strategy for the requested sport."""
        key = sport_name.lower()
        if key not in cls._registry:
            supported = list(cls._registry.keys())
            raise ValueError(f"Unsupported sport activity '{sport_name}'. Supported sports: {supported}")

        config = SPORT_CONFIGS.get(key, {})
        strategy_cls = cls._registry[key]
        return strategy_cls(config=config, fps=fps)

    @classmethod
    def supported_sports(cls) -> list:
        return list(cls._registry.keys())
