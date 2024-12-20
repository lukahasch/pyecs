import ecs
import draw
import pyray as ray

world = ecs.World().plugin(draw.plugin("pygame"))

world.spawn(ecs.Bundle(role=draw.Camera(), position=ecs.Position(200, 200), draw=draw.Circle(10, ray.RED))) # type: ignore

world.run()
