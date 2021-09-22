import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import AnyStr, Optional


@dataclass
class UrlStatus:
    timestamp: datetime
    url: str
    status_code: int
    failure_reason: Optional[str]
    response_time: float
    regexp: Optional[str]
    regexp_matched: bool

    def to_json(self) -> str:
        json_dict = asdict(self)
        json_dict["timestamp"] = self.timestamp.isoformat()
        return json.dumps(json_dict)

    @staticmethod
    def from_json(json_str: AnyStr):
        json_dict = json.loads(json_str)
        json_dict["timestamp"] = datetime.fromisoformat(json_dict["timestamp"])
        return UrlStatus(**json_dict)
