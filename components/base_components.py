from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from RogueLike.engine import Engine
    from RogueLike.entity import Entity
    
class BaseComponent:
    entity: Entity
    
    @property
    def engine(self) -> Engine:
        return self.entity.gamemap.engine