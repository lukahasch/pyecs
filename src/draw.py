import pyray as ray
from ecs import World, Bundle, Field, Query, Position, Velocity, system, Resource, Component, Single

class Drawable:
    pass

class Camera:
    pass

class Circle(Drawable):
    def __init__(self, radius: float, color: tuple[int, int, int]):
        self.radius = radius
        self.color = color

    def draw(self, x: float, y: float, scale: int):
        ray.draw_circle(int(x), int(y), self.radius * scale, self.color) # type: ignore


def plugin(window_name: str, width: int = 800, height: int = 600):
    def runner(world: World):
        ray.init_window(width, height, window_name)
        ray.set_target_fps(60)
        ray.set_exit_key(ray.KEY_F12) # type: ignore

        while not ray.window_should_close():
            ray.begin_drawing()
            ray.clear_background(ray.RAYWHITE) # type: ignore
            world.update()
            ray.end_drawing()

    def plugin(world: World):
        world.runner = runner

        @world.system # type: ignore
        @system(drawables=Query(draw=Component(Drawable), position=Component(Position)), camera=Single(camera=Component(Camera), position=Component(Position)))
        def draw(drawables, camera):
            [x, y] = [camera.position.x, camera.position.y]
            scale = 1

            [screen_x, screen_y] = [ray.get_screen_width() / 2, ray.get_screen_height() / 2]

            for bundle in drawables:
                drawable = bundle.draw
                position = bundle.position
                drawable.draw(position.x - x + screen_x, position.y - y + screen_y, scale)


    return plugin