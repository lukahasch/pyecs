import pyray as ray
from ecs import Query, Has, ECS, Entity, And, Component, Is, Bundle, Plugin, Attr, Single

class Object:
    def draw(self, x, y):
        raise NotImplementedError("Object must implement draw method")

class Circle(Object):
    def __init__(self, radius, color):
        self.radius = radius
        self.color = color

    def draw(self, x, y):
        ray.draw_circle(x, y, self.radius, self.color)

class Camera:
    pass

class Raylib(Plugin):
    def __init__(self, window_name, bg_color):
        self.window_name = window_name
        self.bg_color = bg_color

    def apply(self, ecs):
        ray.init_window(800, 600, self.window_name)
        ray.set_target_fps(60)

        @ecs.system({}, "pre")
        def clear():
            ray.begin_drawing()
            ray.clear_background(self.bg_color)

        @ecs.system({"e": Query(And([Attr("x"), Attr("y"), Component(Object)])), "camera": Single(And([Attr("x"), Attr("y"), Component(Camera)]))})
        def draw(e, camera):
            [camera_x, camera_y, _] = camera
            camera_x = camera_x - ray.get_screen_width() / 2
            camera_y = camera_y - ray.get_screen_height() / 2
            for [x, y, c] in e.values():
                c.draw(int(x - camera_x), int(y - camera_y))

        @ecs.system({}, "post")
        def display():
            ray.end_drawing()
