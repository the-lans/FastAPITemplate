from enum import auto, IntFlag


class FieldHidden(IntFlag):
    NOT = 0
    READ = auto()
    EDIT = auto()
    INIT = auto()
    FULL = READ | EDIT | INIT
    WRITE = EDIT | INIT
