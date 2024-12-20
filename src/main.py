import pyray as ray
from ecs import Query, Has, ECS, Entity, And, Component, Is, Bundle, Attr, Single
import draw

ecs = ECS().add_plugin(draw.Raylib("Hello World", ray.RAYWHITE))

class Rocket:
    pass

ecs.spawn(Bundle(x=1, y=2, comp=draw.Circle(10, ray.RED), vx=5, vy=5, role=Rocket()))
ecs.spawn(Bundle(x=100, y=200, comp=draw.Circle(20, ray.BLUE), vx=2, vy=2, role=draw.Camera()))

@ecs.system(Query(And([Has("x"), Has("y"), Attr("vx"), Attr("vy")])))
def move(entities):
    for [x, y, vx, vy] in entities.values():
        x.x += vx
        y.y += vy

while not ray.window_should_close():
    ecs.update()
