from pathlib import Path


class SD(type(Path())):
    pass


class Ext3(SD):
    isremote = False


class Fat32(SD):
    isremote = False


class CS(SD):
    isremote = True
