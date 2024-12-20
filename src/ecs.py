from typing import Callable, TypeVar, Generic, Any, Self

class Component:
    Result = TypeVar("Result")

    def __init__(self, type):
        self.type = type

    def __call__(self, entity: Any, id) -> 'Component.Result':
        for (k, v) in entity.__dict__():
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
            new_dict = {}
            for (k, v) in dict.items():
                v = v(entity, id)
                if v is None:
                    return None
                new_dict[k] = v
            return new_dict
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
        def condition(entity: Any) -> 'Component.Result':
            new_dict = {}
            for (k, v) in dict.items():
                v = v(entity)
                if v is None:
                    return None
                new_dict[k] = v
            return new_dict
        self.condition = condition

    def construct_from_list(self, list):
        def condition(entity: Any) -> 'Component.Result':
            new_list = []
            for f in list:
                f = f(entity)
                if f is None:
                    return None
                new_list.append(f)
            return new_list
        self.condition = condition

    Id = TypeVar("Id")

    def execute(self, entities: dict[Id, Any]) -> Any:
        for entity in entities.values():
            result = self.condition(entity)
            if not result is None:
                return result
        return None

E = TypeVar("E")

class Id(Generic[E], Component):
    def __init__(self, id: int):
        self.id = id

class World:
    def __init__(self):
        self.entities: dict[Id, Any] = {}
        self.resources: dict[tuple[str, type], Any] = {}
        self.systems: list[Callable[[Self], None]] = []

        self.cid = 0

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

    def system(self, system: Callable[[Self], None]):
        self.systems.append(system)

    def register(self, name: str, resource: Any) -> None:
        self.resources[(name, type(resource))] = resource

    def resource(self, name: str, type: type) -> Any:
        return self.resources[(name, type)]

    def update(self):
        for system in self.systems:
            system(self)

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
