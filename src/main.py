import draw
import pyray as ray
from ecs import World, Bundle, Position

world = World().plugin(draw.plugin("pygame"))

world.spawn(Bundle(role=draw.Camera(), position=Position(200, 200), draw=draw.Circle(10, ray.RED))) # type: ignore

world.run()
