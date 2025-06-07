# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from . import kaitaistruct
from .kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3PhysicsModel(KaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """

    class ShapeTypes(Enum):
        ellipsoid = 1
        box = 2
        cylinder = 3
        pill = 4
        mesh = 5
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(10)
        if not self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A":
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, self._io, u"/seq/0")
        self.format_id = self._io.read_bytes(1)
        if not self.format_id == b"\x06":
            raise kaitaistruct.ValidationNotEqualError(b"\x06", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not self.null_terminator == b"\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.physics_model = Sf3PhysicsModel.PhysicsModel(self._io, self, self._root)

    class PhysicsModel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mass = self._io.read_f4le()
            self.tensor = []
            for i in range(9):
                self.tensor.append(self._io.read_f4le())

            self.shape_count = self._io.read_u2le()
            self.shapes = []
            for i in range(self.shape_count):
                self.shapes.append(Sf3PhysicsModel.Shape(self._io, self, self._root))



    class Cylinder(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bottom_radius = self._io.read_f4le()
            self.top_radius = self._io.read_f4le()
            self.height = self._io.read_f4le()


    class Ellipsoid(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_f4le()
            self.height = self._io.read_f4le()
            self.depth = self._io.read_f4le()


    class Mesh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_count = self._io.read_u2le()
            self.vertices = []
            for i in range((self.vertex_count * 3)):
                self.vertices.append(self._io.read_f4le())



    class Pill(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bottom_radius = self._io.read_f4le()
            self.top_radius = self._io.read_f4le()
            self.height = self._io.read_f4le()


    class Box(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_f4le()
            self.height = self._io.read_f4le()
            self.depth = self._io.read_f4le()


    class Shape(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.transform = []
            for i in range(16):
                self.transform.append(self._io.read_f4le())

            self.shape_type = KaitaiStream.resolve_enum(Sf3PhysicsModel.ShapeTypes, self._io.read_u1())
            _on = self.shape_type
            if _on == Sf3PhysicsModel.ShapeTypes.ellipsoid:
                self.data = Sf3PhysicsModel.Ellipsoid(self._io, self, self._root)
            elif _on == Sf3PhysicsModel.ShapeTypes.pill:
                self.data = Sf3PhysicsModel.Pill(self._io, self, self._root)
            elif _on == Sf3PhysicsModel.ShapeTypes.box:
                self.data = Sf3PhysicsModel.Box(self._io, self, self._root)
            elif _on == Sf3PhysicsModel.ShapeTypes.mesh:
                self.data = Sf3PhysicsModel.Mesh(self._io, self, self._root)
            elif _on == Sf3PhysicsModel.ShapeTypes.cylinder:
                self.data = Sf3PhysicsModel.Cylinder(self._io, self, self._root)



