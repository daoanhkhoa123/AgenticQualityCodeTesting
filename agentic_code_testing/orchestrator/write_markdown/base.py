from abc import ABC, abstractmethod
from pathlib import Path

from agentic_code_testing.orchestrator.typed_schemas import PipelineResult


class BasePipelineResultWriter(ABC):
    @abstractmethod
    def write(self, result: PipelineResult, output_dir: str | Path) -> Path:
        ...
