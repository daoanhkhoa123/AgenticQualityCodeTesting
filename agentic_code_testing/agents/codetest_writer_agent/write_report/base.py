from abc import ABC, abstractmethod
from pathlib import Path

from agentic_code_testing.agents.codetest_writer_agent.typed_schemas import TestWriteResult


class BaseTestWriter(ABC):
    @abstractmethod
    def write(self, results: list[TestWriteResult], output_dir: str | Path) -> list[Path]:
        ...
