from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MarketAlert:
    title: str
    source: str
    category: str
    asset_tags: List[str] = field(default_factory=list)
    summary: str = ""
    url: str = ""
    impact_score: int = 0
    published_at: str = ""


@dataclass
class UserWatchlist:
    chat_id: int
    assets: List[str]
