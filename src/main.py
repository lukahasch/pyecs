import pyray as ray
import ecs

world = ecs.World()

world.spawn(ecs.Bundle(name="luka", age=18))

print(world.query(ecs.Query(name=ecs.Field("name"), age=ecs.Field("age"))))
