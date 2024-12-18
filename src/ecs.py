from typing import Any, Protocol, TypeVar, Generic, Literal


Result = TypeVar("Result", covariant=True)

class Condition:
    def execute(self, entity):
       raise NotImplementedError(f"{self.__class__.__name__} must implement execute method")

class Entity(Condition):
    def __init__(self, condition):
        self.condition = condition

    def execute(self, entity) -> None | Any:
        if self.condition.execute(entity):
            return self
        return None

    def component(self, identifier) -> None | Any:
        return identifier.execute(self)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

C = TypeVar("C", bound=Condition)

class Query(Generic[C]):
    def __init__(self, arg: C):
        self.condition = arg

    def query(self, entities: dict[int, Any]) -> Any:
        result = {}
        for (id, entity) in entities.items():
            r = self.condition.execute(entity)
            if r is not None:
                result[id] = r
        return result


class Single(Generic[C]):
    def __init__(self, condition: C):
        self.condition = condition

    def query(self, entities: dict[int, Entity]) -> Any:
        for entity in entities.values():
            r = self.condition.execute(entity)
            if r:
                return r
        return None

class ECS:
    def __init__(self):
        self.entities = {}
        self.pre = []
        self.systems = []
        self.post = []
        self.id = 0

    def query(self, query: Query) -> list[Entity]:
        return query.query(self.entities)

    def spawn(self, value) -> int:
        if not isinstance(value, Entity):
            raise ValueError("value must be an instance of Entity")
        self.id += 1
        self.entities[self.id] = value
        return self.id

    def add_system(self, system):
        self.systems.append(system)
        return self

    def add_pre(self, system):
        self.pre.append(system)
        return self

    def add_post(self, system):
        self.post.append(system)
        return self

    def system(self, querys, kind: Literal["pre"] | Literal["normal"] | Literal["post"] = "normal"):
        def decorator(func):
            def wrapper(entities):
                if isinstance(querys, Query):
                    return func(querys.query(entities))
                elif isinstance(querys, Single):
                    r = querys.query(entities)
                    if r is not None:
                        return func(r)
                else:
                    kwargs = {}
                    for (name, query) in querys.items():
                        kwargs[name] = query.query(entities)
                        if kwargs[name] is None:
                            return
                    return func(**kwargs)
            if kind == "pre":
                self.add_pre(wrapper)
            elif kind == "normal":
                self.add_system(wrapper)
            elif kind == "post":
                self.add_post(wrapper)
            return wrapper
        return decorator

    def add_plugin(self, plugin):
        plugin.apply(self)
        return self

    def update(self):
        for system in self.pre:
            system(self.entities)

        for system in self.systems:
            system(self.entities)

        for system in self.post:
            system(self.entities)

    def remove(self, entity_id):
        del self.entities[entity_id]

    def get(self, entity_id):
        return self.entities[entity_id]

class Plugin:
    def apply(self, ecs):
        raise NotImplementedError("Plugin must implement apply method")

Name = TypeVar("Name", bound=str)
Type = TypeVar("Type", bound=type | None)

class Attr(Generic[Name], Condition):
    def __init__(self, name: Name):
        self.name = name

    def execute(self, entity):
        if not hasattr(entity, self.name):
            return None
        return getattr(entity, self.name)


class Has(Generic[Name], Condition):
    def __init__(self, name: Name):
        self.name = name

    def execute(self, entity):
        if not hasattr(entity, self.name):
            return None
        return Ref(entity, [self.name])

class Is(Generic[Type], Condition):
    def __init__(self, type):
        self.type = type

    def execute(self, entity):
        if not isinstance(entity, self.type):
            return None
        return entity

class Component(Generic[Type], Condition):
    def __init__(self, type):
        self.type = type

    def execute(self, entity):
        for (name, value) in entity.__dict__.items():
            if isinstance(value, self.type):
                return value
        return None

class And(Condition):
    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions

    def execute(self, entity):
        result = []
        for condition in self.conditions:
            r = condition.execute(entity)
            if r is None:
                return None
            result.append(r)
        return result

class Not(Generic[C], Condition):
    def __init__(self, condition: C):
        self.condition = condition

    def execute(self, entity):
        if self.condition.execute(entity) is None:
            return entity
        return None

class Ref:
    def __init__(self, origin, attrs):
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "attrs", attrs)
        object.__setattr__(self, "index", 0)

    def __setattr__(self, name, value):
        if name in object.__getattribute__(self, "attrs"):
            setattr(self.origin, name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name in object.__getattribute__(self, "attrs"):
            return getattr(self.origin, name)
        return object.__getattribute__(self, name)


    def merge(self, other):
        return Ref(self.origin, self.attrs + other.attrs)

    def __iter__(self):
        return self

    def __next__(self):
        if self.index == len(self.attrs):
            raise StopIteration
        v = self.attrs[self.index]
        self.index += 1
        return getattr(self.origin, v)

class Bundle(Entity):
    def __init__(self, **kwargs):
        for (name, value) in kwargs.items():
            setattr(self, name, value)
