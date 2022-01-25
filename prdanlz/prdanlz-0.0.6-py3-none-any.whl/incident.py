import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def _clone_with_primitives(input: Dict) -> Dict:
    return {k: v for k, v in input.items() if type(v) in [str, int, float]}


class Incident:
    class Level:
        def __init__(
            self,
            level: str,
            params: Dict,
            fallback: Dict = {},
        ):
            assert level
            self._level = level
            self._vars: Dict = _clone_with_primitives(params)
            self._vars["level"] = level
            for key in ["trigger", "untrigger", "escalation"]:
                if key not in params:
                    if key in fallback:
                        self._vars[key] = fallback[key]
                    else:
                        raise Exception(f"'{key}' is missing in '{level}' level")

            self._trigger: str = self._vars["trigger"]
            self._untrigger: str = self._vars["untrigger"]
            self._escalation: str = self._vars["escalation"]

            self._triggered: bool = False

        def clear(self) -> None:
            self._triggered = False

        def escalate_if_in_range(self, locals: Dict) -> bool:
            my_locals = {**locals, **self._vars}
            logger.debug(f"Checking trigger='{self._trigger}' at level={self._level}")
            expr = eval(f'f"{self._trigger}"', {"__builtins__": {}}, my_locals)
            logger.debug(f"Resolved to exprssion='{expr}'")
            if eval(expr, {"__builtins__": {}}, my_locals):
                if not self._triggered:
                    cmd = eval(f'f"{self._escalation}"', my_locals)
                    logger.debug(f"Escalating at level={self._level} with cmd=[{cmd}]")
                    self._triggered = True
                    os.system(cmd)
                return True
            if self._triggered:
                logger.debug(
                    f"Checking untrigger='{self._untrigger}' at level='{self._level}"
                )
                expr = eval(f'f"{self._untrigger}"', {"__builtins__": {}}, my_locals)
                logger.debug(f"Resolved to exprssion='{expr}'")
                if eval(expr, {"__builtins__": {}}, my_locals):
                    self._triggered = False
                    logger.debug(f"Untriggered at level={self._level}")
                else:
                    return True
            return False

    def __init__(self, name: str, params: Dict):
        if "description" in params:
            self._desc = params["description"]
        else:
            raise Exception("'description' is missing")

        count = 0
        self._levels = {}
        fallback = {}
        err = None
        for key in ["error", "warn", "info"]:
            try:
                level = Incident.Level(key, params[key], fallback)
                self._levels[key] = level
                count += 1
                fallback = level._vars
            except Exception as e:
                if err is None:
                    err = e
                self._levels[key] = None
        if count == 0:
            if err:
                raise Exception(f"{err} of '{name}' incident")
            raise Exception(
                "One or more of 'info', 'warn' and/or 'error' must be specified"
            )
        self._name: str = name
        self._vars: Dict = _clone_with_primitives(params)

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return self._name == other._name

    @property
    def name(self) -> str:
        return self._name

    def escalated(self, locals: Dict) -> bool:
        in_range = False
        my_locals = None
        for key in ["error", "warn", "info"]:  # be explicit about ordering
            level = self._levels[key]
            if level:
                if in_range:
                    level.clear()
                else:
                    if my_locals is None:
                        my_locals = {**locals, **self._vars}
                    if level.escalate_if_in_range(my_locals):
                        in_range = True
        return in_range
