from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import numpy as np
import tcod
from RogueLike.actions import Action, MeleeAction, MovementAction, WaitAction
from components.base_components import BaseComponent

if TYPE_CHECKING:
    from RogueLike.entity import Actor

class BaseAI(Action, BaseComponent):
    entity: Actor
    def perform(self) -> None:
        raise NotImplementedError()
    
    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute   and return a path to a target position, if there is no valid target return an empty list"""
        
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)
        
        for entity in self.entity.gamemap.entities:
            if entity.block_movement and cost[entity.x, entity.y]:
                cost[entity.x, entity.y]+= 10
                
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)
        pathfinder.add_root((self.entity.x, self.entity.y))

        result = pathfinder.path_to((dest_x, dest_y))

        # Normalize result into a numpy array we can inspect.
        if isinstance(result, (tuple, list)):
            arr = None
            for part in result:
                try:
                    part_arr = np.asarray(part)
                except Exception:
                    continue
                if part_arr.size:
                    arr = part_arr
                    break
            if arr is None:
                return []
        else:
            arr = np.asarray(result)

        if arr.size == 0:
            return []

        # If arr is Nx2 -> list of (x,y). If 1D of ints -> treat as flattened indices (Fortran order).
        if arr.ndim == 2 and arr.shape[1] == 2:
            coords = [(int(x), int(y)) for x, y in arr.tolist()]
        elif arr.ndim == 1:
            coords = [
                tuple(int(v) for v in np.unravel_index(int(i), cost.shape, order="F"))
                for i in arr.tolist()
            ]
        else:
            flat = arr.ravel().tolist()
            it = iter(flat)
            coords = [(int(a), int(b)) for a, b in zip(it, it)]

        if coords and coords[0] == (self.entity.x, self.entity.y):
            coords = coords[1:]

        return coords
    
class HostileEnemy(BaseAI):
        def __init__(self, entity: Actor):
            super().__init__(entity)
            self.path: List[Tuple[int, int]] = []
            
        def perform(self) -> None:
            target = self.engine.player
            dx = target.x - self.entity.x
            dy = target.y - self.entity.y
            distance = max(abs(dx), abs(dy))
            
            if self.engine.game_map.visible[self.entity.x, self.entity.y]:
                if distance <= 1:
                    return MeleeAction(self.entity, dx , dy). perform()
                
                self.path = self.get_path_to(target.x, target.y)
                
                if self.path:
                    dest_x, dest_y = self.path.pop(0)
                    return MovementAction(
                        self.entity, dest_x - self.entity.x, dest_y - self.entity.y,).perform()
                    
                    return WaitAction(self.entity).perform()
