import re

from machine.utils import Either, Left, Right


class Path:
    _param_regex = r"{(?P<param>\w+)}"

    def __init__(self, path: str):
        self._pattern = self._format_pattern(path)

    def parse(self, path: str) -> Either:
        match = re.match(self._pattern, path)

        if match is None:
            return Left("Path didn't match with given pattern")

        start, end = match.span()

        return Right((match.groupdict(), path[end:]))

    def _format_pattern(self, path):
        if not re.search(self._param_regex, path):
            return path

        regex = r""
        last_pos = 0

        for match in re.finditer(self._param_regex, path):
            regex += path[last_pos: match.start()]
            param = match.group("param")
            regex += r"(?P<%s>\w+)" % param
            last_pos = match.end()

        return regex

    def __str__(self):
        return f"Path('{self._pattern}')"
