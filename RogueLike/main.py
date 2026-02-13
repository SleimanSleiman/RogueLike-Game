import tcod
from pathlib import Path
from engine import Engine
from input_handlers import EventHandler
from entity import Entity
from procgen import generate_dungeon

def main() -> None:
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 50


    tileset_path = Path(__file__).parent / "dejavu10x10_gs_tc.png"
    tileset = tcod.tileset.load_tilesheet(
        str(tileset_path), 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    
    event_handler = EventHandler()

    player = Entity(int(screen_width / 2), int(screen_height / 2 ), "@", (255, 255, 255))
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2 ), "@", (255, 255, 0))
    entities = {npc, player}

    game_map = generate_dungeon(map_width, map_height)

    engine = Engine(entities=entities, game_map=game_map, event_handler=event_handler, player=player)

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Game",
        vsync=True,
    ) as context:
         root_console = tcod.Console(screen_width, screen_height, order="F")
         while True:
            engine.render(console=root_console, context=context)
            events = tcod.event.wait()
            engine.handle_events(events)

            

if __name__ == "__main__":
    main()
