from enum import Enum
from typing import Self


class ServiceEndpointCoverageStatus(str, Enum):
    MISSING = "MISSING"
    COVERED = "COVERED"
    UNCOVERED = "UNCOVERED"

    @property
    def is_missing(self) -> bool:
        return self == self.MISSING

    @property
    def is_covered(self) -> bool:
        return self == self.COVERED

    @classmethod
    def from_bool(cls, value: bool) -> Self:
        return cls.COVERED if value else cls.UNCOVERED

    @classmethod
    def from_has_item(cls, value: bool, has_item: bool) -> Self:
        return cls.from_bool(value) if has_item else cls.MISSING
