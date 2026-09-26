from abc import ABC, abstractmethod
from pathlib import Path

from agentic_code_testing.agents.planner_agent.typed_schemas import Scenario


class BaseScenarioWriter(ABC):
    @abstractmethod
    def write(self, scenarios: list[Scenario], output_dir: str | Path) -> list[Path]:
        ...
