from dataclasses import dataclass
from typing import Dict, Any

from machine.connection import Connection


@dataclass(frozen=True)
class PathParameters:
    remaining: str
    params: Dict[str, str]

    @staticmethod
    def from_conn(conn: Connection) -> 'PathParameters':
        return PathParameters(
            remaining=conn.path,
            params={}
        )


@dataclass(frozen=True)
class Parameters:
    path: PathParameters
    params: Dict[str, Any]

    @staticmethod
    def from_conn(conn: Connection) -> 'Parameters':
        return Parameters(
            path=PathParameters.from_conn(conn),
            params={}
        )

    def with_updated_path(self, params: Dict[str, str], remaining: str) -> 'Parameters':
        return Parameters(
            path=PathParameters(remaining=remaining, params=params),
            params=self.params
        )

    def with_new_params(self, new_params: Dict[str, Any]) -> 'Parameters':
        return Parameters(
            path=self.path,
            params={**self.params, **new_params}
        )
