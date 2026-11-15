from .bomber import Bomber
from .coler import Coler
from .invy import Invy
from .rabbit import Rabbit
from .rower import Rower
from .spider import Spider

from .enemy_base import Enemy


ENEMY_CLASS_MAP = {
    cls.enemy_id: cls
    for cls in Enemy.__subclasses__()
}