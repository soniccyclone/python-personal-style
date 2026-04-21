from dataclasses import dataclass
from functools import partial


record = partial(dataclass, frozen=True, slots=True)
