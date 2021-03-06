from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PathParameters:
    remaining: str
    params: Dict[str, str]

    @staticmethod
    def from_conn(conn) -> "PathParameters":  # type: ignore
        return PathParameters(remaining=conn.path or "", params={})


@dataclass(frozen=True)
class Parameters:
    path: PathParameters
    params: Dict[str, Any]

    @staticmethod
    def from_conn(conn) -> "Parameters":  # type: ignore
        return Parameters(path=PathParameters.from_conn(conn), params={})

    def with_updated_path(
        self, params: Dict[str, str], remaining: str
    ) -> "Parameters":
        return Parameters(
            path=PathParameters(remaining=remaining, params=params),
            params=self.params,
        )

    def with_new_params(self, new_params: Dict[str, Any]) -> "Parameters":
        return Parameters(path=self.path, params={**self.params, **new_params})
