from ray.rllib.models import ModelCatalog

ENVS = {}
REWARDS = {}


def register_env(name: str):
    """Decorator for registering an env."""

    def decorator(cls):
        ENVS[name] = cls
        return cls

    return decorator


def register_reward(name: str):
    """Decorator for registering a reward."""

    def decorator(func):
        REWARDS[name] = func
        return func

    return decorator


def register_model(name: str):
    """Decorator for registering a model."""

    def decorator(cls):
        ModelCatalog.register_custom_model(name, cls)
        return cls

    return decorator


def create_reward(name):
    return REWARDS[name]
