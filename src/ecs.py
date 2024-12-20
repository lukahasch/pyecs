from typing import Callable, TypeVar, Generic, Any, Self

class Component:
    Result = TypeVar("Result")

    def __init__(self, type):
        self.type = type

    def __call__(self, entity: Any, id) -> 'Component.Result':
        for (k, v) in entity.__dict__.items():
            if isinstance(v, self.type):
                return v

C = TypeVar("C", bound=Component)

class Query(Generic[C]):
    Result = TypeVar("Result")

    def __init__(self, *args, **kwargs) -> None:
        if len(args) != 0 and len(kwargs) != 0:
            raise ValueError("Query can only have positional or keyword arguments, not both")
        if len(args) != 0:
            self.construct_from_list(args)
        elif len(kwargs) != 0:
            self.construct_from_dict(kwargs)

    Id = TypeVar("Id")

    def construct_from_dict(self, dict):
        def condition(entity: Any, id: Id) -> 'Component.Result':
            new = Bundle()
            for (k, v) in dict.items():
                v = v(entity, id)
                if v is None:
                    return None
                setattr(new, k, v)
            return new
        self.condition = condition

    def construct_from_list(self, list):
        def condition(entity: Any, id: Id) -> 'Component.Result':
            new_list = []
            for f in list:
                f = f(entity, id)
                if f is None:
                    return None
                new_list.append(f)
            return new_list
        self.condition = condition

    def execute(self, entity: Any, id) -> 'Component.Result':
        return self.condition(entity, id)

    def __call__(self, entity: Any, id) -> 'Component.Result':
        return self.execute(entity, id)

class Single(Generic[C]):
    Result = TypeVar("Result")

    def __init__(self, *args, **kwargs) -> None:
        if len(args) != 0 and len(kwargs) != 0:
            raise ValueError("Single can only have positional or keyword arguments, not both")
        if len(args) != 0:
            self.construct_from_list(args)
        elif len(kwargs) != 0:
            self.construct_from_dict(kwargs)

    def construct_from_dict(self, dict):
        def condition(entity: Any, id) -> 'Component.Result':
            new = Bundle()
            for (k, v) in dict.items():
                v = v(entity, id)
                if v is None:
                    return None
                setattr(new, k, v)
            return new
        self.condition = condition

    def construct_from_list(self, list):
        def condition(entity: Any, id) -> 'Component.Result':
            new_list = []
            for f in list:
                f = f(entity, id)
                if f is None:
                    return None
                new_list.append(f)
            return new_list
        self.condition = condition

    Id = TypeVar("Id")

    def execute(self, entities: dict[Id, Any]) -> Any:
        for (id, entity) in entities.items():
            result = self.condition(entity, id)
            if not result is None:
                return result
        return None

class Resource:
    def __init__(self, type: type):
        self.type = type

E = TypeVar("E")

class Id(Generic[E], Component):
    def __init__(self, id: int):
        self.id = id

class World:
    def __init__(self):
        self.entities: dict[Id, Any] = {}
        self.resources: dict[type, Any] = {}
        self.systems: list[Callable[[Self], None]] = []

        self.cid = 0

        self.runner: Callable[[Self], Any] = lambda x: None

    Spawn = TypeVar("Spawn")
    def spawn(self, entity: Spawn) -> Id[Spawn]:
        id = Id(self.cid)
        self.entities[id] = entity
        self.cid += 1
        return id

    def query(self, query: Query) -> "list[Query.Result]":
        return list(filter(lambda x: not x is None, [query.execute(entity, id) for (id, entity) in self.entities.items()]))

    def single(self, single: Single) -> "Single.Result":
        return single.execute(self.entities)

    def system(self, system: Callable[[Self], None]) -> Self:
        self.systems.append(system)
        return self

    def register(self, resource: Any) -> Self:
        self.resources[type(resource)] = resource
        return self

    def resource(self, type: type) -> Any:
        return self.resources[type]

    def plugin(self, plugin: Callable[[Self], None]) -> Self:
        plugin(self)
        return self

    def update(self):
        for system in self.systems:
            system(self)

    def run(self):
        return self.runner(self)

def system(*args, **kwargs):
    if len(args) != 0 and len(kwargs) != 0:
        raise ValueError("System can only have positional or keyword arguments, not both")
    def decorator(f):
        if len(args) != 0:
            return system_from_list(f, args)
        elif len(kwargs) != 0:
            return system_from_dict(f, kwargs)
        else:
            return f
    return decorator

def system_from_dict(f, dict):
    def wrapper(world):
        d = {}
        for (k, v) in dict.items():
            if isinstance(v, Resource):
                d[k] = world.resource(v.type)
            elif isinstance(v, Query):
                d[k] = world.query(v)
            elif isinstance(v, Single):
                d[k] = world.single(v)
            else:
                raise TypeError("Invalid argument type")
            if d[k] is None:
                return
        return f(**d)
    return wrapper

def system_from_list(f, list):
    def wrapper(world):
        l = []
        for v in list:
            if isinstance(v, Resource):
                l.append(world.resource(v.type))
            elif isinstance(v, Query):
                l.append(world.query(v))
            elif isinstance(v, Single):
                l.append(world.single(v))
            else:
                raise TypeError("Invalid argument type")
        return f(*l)
    return wrapper

class Bundle:
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    def from_dict(self, dict):
        for (k, v) in dict.items():
            setattr(self, k, v)

class Field(Component):
    def __init__(self, name: str, type: type | None = None):
        self.name = name
        self.type = type

    def __call__(self, entity: Any, id):
        if hasattr(entity, self.name):
            field = getattr(entity, self.name)
            if self.type is None or isinstance(field, self.type):
                return field
        return None

class Position:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, vx: float, vy: float):
        self.vx = vx
        self.vy = vy
