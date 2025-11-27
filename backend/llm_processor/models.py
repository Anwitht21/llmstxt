from dataclasses import dataclass

@dataclass
class ProcessingResult:
    success: bool
    output: str
    error: str | None = None
    stats: dict | None = None

    @classmethod
    def success_result(cls, output: str, stats: dict) -> "ProcessingResult":
        return cls(success=True, output=output, error=None, stats=stats)

    @classmethod
    def failure_result(cls, original_output: str, error: str) -> "ProcessingResult":
        return cls(success=False, output=original_output, error=error, stats=None)
