import json
from dataclasses import asdict, dataclass
from time import strftime, strptime, struct_time

URL_CHECK_TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"


@dataclass
class UrlStatus:
    timestamp: struct_time
    url: str
    status_code: int
    failure_reason: str
    response_time: float
    regexp_match: bool

    def to_json(self) -> str:
        json_dict = asdict(self)
        json_dict["timestamp"] = strftime(URL_CHECK_TIMESTAMP_FORMAT, self.timestamp)
        return json.dumps(json_dict)

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        json_dict["timestamp"] = strptime(
            json_dict["timestamp"], URL_CHECK_TIMESTAMP_FORMAT
        )
        return UrlStatus(**json_dict)
