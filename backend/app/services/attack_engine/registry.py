from typing import Dict, List, Type, Optional
from backend.app.services.attack_engine.base import BaseScenario

class AttackRegistry:
    """Extensible registry for BreakTraceFix AI attack scenarios."""
    _instance: Optional["AttackRegistry"] = None
    _scenarios: Dict[str, BaseScenario] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AttackRegistry, cls).__new__(cls)
            cls._instance._scenarios = {}
        return cls._instance

    @classmethod
    def register(cls, scenario_class: Type[BaseScenario]) -> Type[BaseScenario]:
        """Decorator or method to register an attack scenario."""
        instance = scenario_class()
        cls()._scenarios[instance.id] = instance
        return scenario_class

    @classmethod
    def get(cls, scenario_id: str) -> Optional[BaseScenario]:
        """Retrieve a registered scenario by ID."""
        return cls()._scenarios.get(scenario_id)

    @classmethod
    def list_all(cls) -> List[BaseScenario]:
        """List all registered scenarios sorted by ID."""
        return sorted(cls()._scenarios.values(), key=lambda s: s.id)

    @classmethod
    def list_by_category(cls, category: str) -> List[BaseScenario]:
        """Filter scenarios by category."""
        return [s for s in cls()._scenarios.values() if s.category.lower() == category.lower()]

    @classmethod
    def list_by_severity(cls, severity: str) -> List[BaseScenario]:
        """Filter scenarios by severity."""
        return [s for s in cls()._scenarios.values() if s.severity.lower() == severity.lower()]

registry = AttackRegistry()

