from dataclasses import dataclass, field
from collections import deque
from typing import Set, Deque

@dataclass
class CrawlState:
    base_url: str
    max_pages: int
    visited: Set[str] = field(default_factory=set)
    queue: Deque[str] = field(default_factory=deque)
