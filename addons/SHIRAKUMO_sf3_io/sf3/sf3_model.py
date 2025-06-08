# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

from . import kaitaistruct
from .kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3Model(ReadWriteKaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.magic = self._io.read_bytes(10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, self._io, u"/seq/0")
        self.format_id = self._io.read_bytes(1)
        if not (self.format_id == b"\x05"):
            raise kaitaistruct.ValidationNotEqualError(b"\x05", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.model = Sf3Model.Model(self._io, self, self._root)
        self.model._read()


    def _fetch_instances(self):
        pass
        self.model._fetch_instances()


    def _write__seq(self, io=None):
        super(Sf3Model, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_bytes(self.format_id)
        self._io.write_u4le(self.checksum)
        self._io.write_bytes(self.null_terminator)
        self.model._write__seq(self._io)


    def _check(self):
        pass
        if (len(self.magic) != 10):
            raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, None, u"/seq/0")
        if (len(self.format_id) != 1):
            raise kaitaistruct.ConsistencyError(u"format_id", len(self.format_id), 1)
        if not (self.format_id == b"\x05"):
            raise kaitaistruct.ValidationNotEqualError(b"\x05", self.format_id, None, u"/seq/1")
        if (len(self.null_terminator) != 1):
            raise kaitaistruct.ConsistencyError(u"null_terminator", len(self.null_terminator), 1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, None, u"/seq/3")
        if self.model._root != self._root:
            raise kaitaistruct.ConsistencyError(u"model", self.model._root, self._root)
        if self.model._parent != self:
            raise kaitaistruct.ConsistencyError(u"model", self.model._parent, self)

    class Model(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.format = Sf3Model.VertexFormat(self._io, self, self._root)
            self.format._read()
            self.material_type = Sf3Model.MaterialType(self._io, self, self._root)
            self.material_type._read()
            self.material_size = self._io.read_u4le()
            self.material = Sf3Model.Material(self._io, self, self._root)
            self.material._read()
            self.vertex_data = Sf3Model.VertexData(self._io, self, self._root)
            self.vertex_data._read()


        def _fetch_instances(self):
            pass
            self.format._fetch_instances()
            self.material_type._fetch_instances()
            self.material._fetch_instances()
            self.vertex_data._fetch_instances()


        def _write__seq(self, io=None):
            super(Sf3Model.Model, self)._write__seq(io)
            self.format._write__seq(self._io)
            self.material_type._write__seq(self._io)
            self._io.write_u4le(self.material_size)
            self.material._write__seq(self._io)
            self.vertex_data._write__seq(self._io)


        def _check(self):
            pass
            if self.format._root != self._root:
                raise kaitaistruct.ConsistencyError(u"format", self.format._root, self._root)
            if self.format._parent != self:
                raise kaitaistruct.ConsistencyError(u"format", self.format._parent, self)
            if self.material_type._root != self._root:
                raise kaitaistruct.ConsistencyError(u"material_type", self.material_type._root, self._root)
            if self.material_type._parent != self:
                raise kaitaistruct.ConsistencyError(u"material_type", self.material_type._parent, self)
            if self.material._root != self._root:
                raise kaitaistruct.ConsistencyError(u"material", self.material._root, self._root)
            if self.material._parent != self:
                raise kaitaistruct.ConsistencyError(u"material", self.material._parent, self)
            if self.vertex_data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"vertex_data", self.vertex_data._root, self._root)
            if self.vertex_data._parent != self:
                raise kaitaistruct.ConsistencyError(u"vertex_data", self.vertex_data._parent, self)


    class VertexFormat(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.raw = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3Model.VertexFormat, self)._write__seq(io)
            self._io.write_u1(self.raw)


        def _check(self):
            pass

        @property
        def has_position(self):
            if hasattr(self, '_m_has_position'):
                return self._m_has_position

            self._m_has_position = (0 != (self.raw & 1))
            return getattr(self, '_m_has_position', None)

        def _invalidate_has_position(self):
            del self._m_has_position
        @property
        def vertex_stride(self):
            if hasattr(self, '_m_vertex_stride'):
                return self._m_vertex_stride

            self._m_vertex_stride = (((((((self.raw >> 0) & 1) * 3) + (((self.raw >> 1) & 1) * 2)) + (((self.raw >> 2) & 1) * 3)) + (((self.raw >> 3) & 1) * 3)) + (((self.raw >> 4) & 1) * 3))
            return getattr(self, '_m_vertex_stride', None)

        def _invalidate_vertex_stride(self):
            del self._m_vertex_stride
        @property
        def has_tangent(self):
            if hasattr(self, '_m_has_tangent'):
                return self._m_has_tangent

            self._m_has_tangent = (0 != (self.raw & 16))
            return getattr(self, '_m_has_tangent', None)

        def _invalidate_has_tangent(self):
            del self._m_has_tangent
        @property
        def has_color(self):
            if hasattr(self, '_m_has_color'):
                return self._m_has_color

            self._m_has_color = (0 != (self.raw & 4))
            return getattr(self, '_m_has_color', None)

        def _invalidate_has_color(self):
            del self._m_has_color
        @property
        def has_normal(self):
            if hasattr(self, '_m_has_normal'):
                return self._m_has_normal

            self._m_has_normal = (0 != (self.raw & 8))
            return getattr(self, '_m_has_normal', None)

        def _invalidate_has_normal(self):
            del self._m_has_normal
        @property
        def has_uv(self):
            if hasattr(self, '_m_has_uv'):
                return self._m_has_uv

            self._m_has_uv = (0 != (self.raw & 2))
            return getattr(self, '_m_has_uv', None)

        def _invalidate_has_uv(self):
            del self._m_has_uv

    class VertexData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.face_count = self._io.read_u4le()
            self.faces = []
            for i in range(self.face_count):
                self.faces.append(self._io.read_u4le())

            self.vertex_count = self._io.read_u4le()
            self.vertices = []
            for i in range(self.vertex_count):
                self.vertices.append(self._io.read_f4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.faces)):
                pass

            for i in range(len(self.vertices)):
                pass



        def _write__seq(self, io=None):
            super(Sf3Model.VertexData, self)._write__seq(io)
            self._io.write_u4le(self.face_count)
            for i in range(len(self.faces)):
                pass
                self._io.write_u4le(self.faces[i])

            self._io.write_u4le(self.vertex_count)
            for i in range(len(self.vertices)):
                pass
                self._io.write_f4le(self.vertices[i])



        def _check(self):
            pass
            if (len(self.faces) != self.face_count):
                raise kaitaistruct.ConsistencyError(u"faces", len(self.faces), self.face_count)
            for i in range(len(self.faces)):
                pass

            if (len(self.vertices) != self.vertex_count):
                raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.vertex_count)
            for i in range(len(self.vertices)):
                pass



    class MaterialType(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.raw = self._io.read_u1()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3Model.MaterialType, self)._write__seq(io)
            self._io.write_u1(self.raw)


        def _check(self):
            pass

        @property
        def material_count(self):
            if hasattr(self, '_m_material_count'):
                return self._m_material_count

            self._m_material_count = (((((((((self.raw >> 0) & 1) + ((self.raw >> 1) & 1)) + ((self.raw >> 2) & 1)) + ((self.raw >> 3) & 1)) + ((self.raw >> 4) & 1)) + ((self.raw >> 5) & 1)) + ((self.raw >> 6) & 1)) + ((self.raw >> 7) & 1))
            return getattr(self, '_m_material_count', None)

        def _invalidate_material_count(self):
            del self._m_material_count
        @property
        def has_occlusion(self):
            if hasattr(self, '_m_has_occlusion'):
                return self._m_has_occlusion

            self._m_has_occlusion = (0 != (self.raw & 32))
            return getattr(self, '_m_has_occlusion', None)

        def _invalidate_has_occlusion(self):
            del self._m_has_occlusion
        @property
        def has_roughness(self):
            if hasattr(self, '_m_has_roughness'):
                return self._m_has_roughness

            self._m_has_roughness = (0 != (self.raw & 16))
            return getattr(self, '_m_has_roughness', None)

        def _invalidate_has_roughness(self):
            del self._m_has_roughness
        @property
        def has_metallic(self):
            if hasattr(self, '_m_has_metallic'):
                return self._m_has_metallic

            self._m_has_metallic = (0 != (self.raw & 4))
            return getattr(self, '_m_has_metallic', None)

        def _invalidate_has_metallic(self):
            del self._m_has_metallic
        @property
        def has_specular(self):
            if hasattr(self, '_m_has_specular'):
                return self._m_has_specular

            self._m_has_specular = (0 != (self.raw & 64))
            return getattr(self, '_m_has_specular', None)

        def _invalidate_has_specular(self):
            del self._m_has_specular
        @property
        def has_normal(self):
            if hasattr(self, '_m_has_normal'):
                return self._m_has_normal

            self._m_has_normal = (0 != (self.raw & 2))
            return getattr(self, '_m_has_normal', None)

        def _invalidate_has_normal(self):
            del self._m_has_normal
        @property
        def has_emission(self):
            if hasattr(self, '_m_has_emission'):
                return self._m_has_emission

            self._m_has_emission = (0 != (self.raw & 128))
            return getattr(self, '_m_has_emission', None)

        def _invalidate_has_emission(self):
            del self._m_has_emission
        @property
        def has_albedo(self):
            if hasattr(self, '_m_has_albedo'):
                return self._m_has_albedo

            self._m_has_albedo = (0 != (self.raw & 1))
            return getattr(self, '_m_has_albedo', None)

        def _invalidate_has_albedo(self):
            del self._m_has_albedo
        @property
        def has_metalness(self):
            if hasattr(self, '_m_has_metalness'):
                return self._m_has_metalness

            self._m_has_metalness = (0 != (self.raw & 8))
            return getattr(self, '_m_has_metalness', None)

        def _invalidate_has_metalness(self):
            del self._m_has_metalness

    class Material(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.textures = []
            for i in range(self._parent.material_type.material_count):
                _t_textures = Sf3Model.String2(self._io, self, self._root)
                _t_textures._read()
                self.textures.append(_t_textures)



        def _fetch_instances(self):
            pass
            for i in range(len(self.textures)):
                pass
                self.textures[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Sf3Model.Material, self)._write__seq(io)
            for i in range(len(self.textures)):
                pass
                self.textures[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.textures) != self._parent.material_type.material_count):
                raise kaitaistruct.ConsistencyError(u"textures", len(self.textures), self._parent.material_type.material_count)
            for i in range(len(self.textures)):
                pass
                if self.textures[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"textures", self.textures[i]._root, self._root)
                if self.textures[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"textures", self.textures[i]._parent, self)



    class String2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.len = self._io.read_u2le()
            self.value = (self._io.read_bytes(self.len)).decode("UTF-8")


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3Model.String2, self)._write__seq(io)
            self._io.write_u2le(self.len)
            self._io.write_bytes((self.value).encode(u"UTF-8"))


        def _check(self):
            pass
            if (len((self.value).encode(u"UTF-8")) != self.len):
                raise kaitaistruct.ConsistencyError(u"value", len((self.value).encode(u"UTF-8")), self.len)



