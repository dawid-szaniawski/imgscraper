from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ImagesSource:
    current_url_address: str
    container_class: str
    pagination_class: str
    pages_to_scan: int

    def __post_init__(self):
        self.domain = self.current_url_address


@dataclass(frozen=True)
class Image:
    source: str
    url_address: str
    title: str
    created_at: datetime

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.url_address == other.url_address
        return False

    def __hash__(self):
        return hash(self.url_address)

    def as_dict(self) -> dict[str, str | datetime]:
        return asdict(self)
