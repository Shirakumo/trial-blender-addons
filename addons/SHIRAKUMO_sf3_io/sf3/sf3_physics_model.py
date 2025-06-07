# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3PhysicsModel(ReadWriteKaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """

    class ShapeTypes(IntEnum):
        ellipsoid = 1
        box = 2
        cylinder = 3
        pill = 4
        mesh = 5
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.magic = self._io.read_bytes(10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, self._io, u"/seq/0")
        self.format_id = self._io.read_bytes(1)
        if not (self.format_id == b"\x06"):
            raise kaitaistruct.ValidationNotEqualError(b"\x06", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.physics_model = Sf3PhysicsModel.PhysicsModel(self._io, self, self._root)
        self.physics_model._read()


    def _fetch_instances(self):
        pass
        self.physics_model._fetch_instances()


    def _write__seq(self, io=None):
        super(Sf3PhysicsModel, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_bytes(self.format_id)
        self._io.write_u4le(self.checksum)
        self._io.write_bytes(self.null_terminator)
        self.physics_model._write__seq(self._io)


    def _check(self):
        pass
        if (len(self.magic) != 10):
            raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, None, u"/seq/0")
        if (len(self.format_id) != 1):
            raise kaitaistruct.ConsistencyError(u"format_id", len(self.format_id), 1)
        if not (self.format_id == b"\x06"):
            raise kaitaistruct.ValidationNotEqualError(b"\x06", self.format_id, None, u"/seq/1")
        if (len(self.null_terminator) != 1):
            raise kaitaistruct.ConsistencyError(u"null_terminator", len(self.null_terminator), 1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, None, u"/seq/3")
        if self.physics_model._root != self._root:
            raise kaitaistruct.ConsistencyError(u"physics_model", self.physics_model._root, self._root)
        if self.physics_model._parent != self:
            raise kaitaistruct.ConsistencyError(u"physics_model", self.physics_model._parent, self)

    class PhysicsModel(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.mass = self._io.read_f4le()
            self.tensor = []
            for i in range(9):
                self.tensor.append(self._io.read_f4le())

            self.shape_count = self._io.read_u2le()
            self.shapes = []
            for i in range(self.shape_count):
                _t_shapes = Sf3PhysicsModel.Shape(self._io, self, self._root)
                _t_shapes._read()
                self.shapes.append(_t_shapes)



        def _fetch_instances(self):
            pass
            for i in range(len(self.tensor)):
                pass

            for i in range(len(self.shapes)):
                pass
                self.shapes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.PhysicsModel, self)._write__seq(io)
            self._io.write_f4le(self.mass)
            for i in range(len(self.tensor)):
                pass
                self._io.write_f4le(self.tensor[i])

            self._io.write_u2le(self.shape_count)
            for i in range(len(self.shapes)):
                pass
                self.shapes[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.tensor) != 9):
                raise kaitaistruct.ConsistencyError(u"tensor", len(self.tensor), 9)
            for i in range(len(self.tensor)):
                pass

            if (len(self.shapes) != self.shape_count):
                raise kaitaistruct.ConsistencyError(u"shapes", len(self.shapes), self.shape_count)
            for i in range(len(self.shapes)):
                pass
                if self.shapes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"shapes", self.shapes[i]._root, self._root)
                if self.shapes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"shapes", self.shapes[i]._parent, self)



    class Cylinder(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bottom_radius = self._io.read_f4le()
            self.top_radius = self._io.read_f4le()
            self.height = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Cylinder, self)._write__seq(io)
            self._io.write_f4le(self.bottom_radius)
            self._io.write_f4le(self.top_radius)
            self._io.write_f4le(self.height)


        def _check(self):
            pass


    class Ellipsoid(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.width = self._io.read_f4le()
            self.height = self._io.read_f4le()
            self.depth = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Ellipsoid, self)._write__seq(io)
            self._io.write_f4le(self.width)
            self._io.write_f4le(self.height)
            self._io.write_f4le(self.depth)


        def _check(self):
            pass


    class Mesh(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vertex_count = self._io.read_u2le()
            self.vertices = []
            for i in range((self.vertex_count * 3)):
                self.vertices.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.vertices)):
                pass



        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Mesh, self)._write__seq(io)
            self._io.write_u2le(self.vertex_count)
            for i in range(len(self.vertices)):
                pass
                self._io.write_f4le(self.vertices[i])



        def _check(self):
            pass
            if (len(self.vertices) != (self.vertex_count * 3)):
                raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), (self.vertex_count * 3))
            for i in range(len(self.vertices)):
                pass



    class Pill(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bottom_radius = self._io.read_f4le()
            self.top_radius = self._io.read_f4le()
            self.height = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Pill, self)._write__seq(io)
            self._io.write_f4le(self.bottom_radius)
            self._io.write_f4le(self.top_radius)
            self._io.write_f4le(self.height)


        def _check(self):
            pass


    class Box(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.width = self._io.read_f4le()
            self.height = self._io.read_f4le()
            self.depth = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Box, self)._write__seq(io)
            self._io.write_f4le(self.width)
            self._io.write_f4le(self.height)
            self._io.write_f4le(self.depth)


        def _check(self):
            pass


    class Shape(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.transform = []
            for i in range(16):
                self.transform.append(self._io.read_f4le())

            self.shape_type = KaitaiStream.resolve_enum(Sf3PhysicsModel.ShapeTypes, self._io.read_u1())
            _on = self.shape_type
            if _on == Sf3PhysicsModel.ShapeTypes.ellipsoid:
                pass
                self.data = Sf3PhysicsModel.Ellipsoid(self._io, self, self._root)
                self.data._read()
            elif _on == Sf3PhysicsModel.ShapeTypes.pill:
                pass
                self.data = Sf3PhysicsModel.Pill(self._io, self, self._root)
                self.data._read()
            elif _on == Sf3PhysicsModel.ShapeTypes.box:
                pass
                self.data = Sf3PhysicsModel.Box(self._io, self, self._root)
                self.data._read()
            elif _on == Sf3PhysicsModel.ShapeTypes.mesh:
                pass
                self.data = Sf3PhysicsModel.Mesh(self._io, self, self._root)
                self.data._read()
            elif _on == Sf3PhysicsModel.ShapeTypes.cylinder:
                pass
                self.data = Sf3PhysicsModel.Cylinder(self._io, self, self._root)
                self.data._read()


        def _fetch_instances(self):
            pass
            for i in range(len(self.transform)):
                pass

            _on = self.shape_type
            if _on == Sf3PhysicsModel.ShapeTypes.ellipsoid:
                pass
                self.data._fetch_instances()
            elif _on == Sf3PhysicsModel.ShapeTypes.pill:
                pass
                self.data._fetch_instances()
            elif _on == Sf3PhysicsModel.ShapeTypes.box:
                pass
                self.data._fetch_instances()
            elif _on == Sf3PhysicsModel.ShapeTypes.mesh:
                pass
                self.data._fetch_instances()
            elif _on == Sf3PhysicsModel.ShapeTypes.cylinder:
                pass
                self.data._fetch_instances()


        def _write__seq(self, io=None):
            super(Sf3PhysicsModel.Shape, self)._write__seq(io)
            for i in range(len(self.transform)):
                pass
                self._io.write_f4le(self.transform[i])

            self._io.write_u1(int(self.shape_type))
            _on = self.shape_type
            if _on == Sf3PhysicsModel.ShapeTypes.ellipsoid:
                pass
                self.data._write__seq(self._io)
            elif _on == Sf3PhysicsModel.ShapeTypes.pill:
                pass
                self.data._write__seq(self._io)
            elif _on == Sf3PhysicsModel.ShapeTypes.box:
                pass
                self.data._write__seq(self._io)
            elif _on == Sf3PhysicsModel.ShapeTypes.mesh:
                pass
                self.data._write__seq(self._io)
            elif _on == Sf3PhysicsModel.ShapeTypes.cylinder:
                pass
                self.data._write__seq(self._io)


        def _check(self):
            pass
            if (len(self.transform) != 16):
                raise kaitaistruct.ConsistencyError(u"transform", len(self.transform), 16)
            for i in range(len(self.transform)):
                pass

            _on = self.shape_type
            if _on == Sf3PhysicsModel.ShapeTypes.ellipsoid:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)
            elif _on == Sf3PhysicsModel.ShapeTypes.pill:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)
            elif _on == Sf3PhysicsModel.ShapeTypes.box:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)
            elif _on == Sf3PhysicsModel.ShapeTypes.mesh:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)
            elif _on == Sf3PhysicsModel.ShapeTypes.cylinder:
                pass
                if self.data._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                if self.data._parent != self:
                    raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)



