# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from . import kaitaistruct
from .kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3Model(KaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """
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
        if not self.format_id == b"\x05":
            raise kaitaistruct.ValidationNotEqualError(b"\x05", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not self.null_terminator == b"\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.model = Sf3Model.Model(self._io, self, self._root)

    class Model(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.format = Sf3Model.VertexFormat(self._io, self, self._root)
            self.material_type = Sf3Model.MaterialType(self._io, self, self._root)
            self.material_size = self._io.read_u4le()
            self.material = Sf3Model.Material(self._io, self, self._root)
            self.vertex_data = Sf3Model.VertexData(self._io, self, self._root)


    class VertexFormat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u1()

        @property
        def has_position(self):
            if hasattr(self, '_m_has_position'):
                return self._m_has_position

            self._m_has_position = 0 != (self.raw & 1)
            return getattr(self, '_m_has_position', None)

        @property
        def has_tangent(self):
            if hasattr(self, '_m_has_tangent'):
                return self._m_has_tangent

            self._m_has_tangent = 0 != (self.raw & 16)
            return getattr(self, '_m_has_tangent', None)

        @property
        def has_color(self):
            if hasattr(self, '_m_has_color'):
                return self._m_has_color

            self._m_has_color = 0 != (self.raw & 4)
            return getattr(self, '_m_has_color', None)

        @property
        def has_normal(self):
            if hasattr(self, '_m_has_normal'):
                return self._m_has_normal

            self._m_has_normal = 0 != (self.raw & 8)
            return getattr(self, '_m_has_normal', None)

        @property
        def has_uv(self):
            if hasattr(self, '_m_has_uv'):
                return self._m_has_uv

            self._m_has_uv = 0 != (self.raw & 2)
            return getattr(self, '_m_has_uv', None)


    class VertexData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.face_count = self._io.read_u4le()
            self.faces = []
            for i in range(self.face_count):
                self.faces.append(self._io.read_u4le())

            self.vertex_count = self._io.read_u4le()
            self.vertices = []
            for i in range(self.vertex_count):
                self.vertices.append(self._io.read_f4le())



    class MaterialType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u1()

        @property
        def material_count(self):
            if hasattr(self, '_m_material_count'):
                return self._m_material_count

            self._m_material_count = (((((((((self.raw >> 0) & (1 + (self.raw >> 1))) & (1 + (self.raw >> 2))) & (1 + (self.raw >> 3))) & (1 + (self.raw >> 4))) & (1 + (self.raw >> 5))) & (1 + (self.raw >> 6))) & (1 + (self.raw >> 7))) & 1)
            return getattr(self, '_m_material_count', None)

        @property
        def has_occlusion(self):
            if hasattr(self, '_m_has_occlusion'):
                return self._m_has_occlusion

            self._m_has_occlusion = 0 != (self.raw & 32)
            return getattr(self, '_m_has_occlusion', None)

        @property
        def has_roughness(self):
            if hasattr(self, '_m_has_roughness'):
                return self._m_has_roughness

            self._m_has_roughness = 0 != (self.raw & 16)
            return getattr(self, '_m_has_roughness', None)

        @property
        def has_metallic(self):
            if hasattr(self, '_m_has_metallic'):
                return self._m_has_metallic

            self._m_has_metallic = 0 != (self.raw & 4)
            return getattr(self, '_m_has_metallic', None)

        @property
        def has_specular(self):
            if hasattr(self, '_m_has_specular'):
                return self._m_has_specular

            self._m_has_specular = 0 != (self.raw & 64)
            return getattr(self, '_m_has_specular', None)

        @property
        def has_normal(self):
            if hasattr(self, '_m_has_normal'):
                return self._m_has_normal

            self._m_has_normal = 0 != (self.raw & 2)
            return getattr(self, '_m_has_normal', None)

        @property
        def has_emission(self):
            if hasattr(self, '_m_has_emission'):
                return self._m_has_emission

            self._m_has_emission = 0 != (self.raw & 128)
            return getattr(self, '_m_has_emission', None)

        @property
        def has_albedo(self):
            if hasattr(self, '_m_has_albedo'):
                return self._m_has_albedo

            self._m_has_albedo = 0 != (self.raw & 1)
            return getattr(self, '_m_has_albedo', None)

        @property
        def has_metalness(self):
            if hasattr(self, '_m_has_metalness'):
                return self._m_has_metalness

            self._m_has_metalness = 0 != (self.raw & 8)
            return getattr(self, '_m_has_metalness', None)


    class Material(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.textures = []
            for i in range(self._parent.material_type.material_count):
                self.textures.append(Sf3Model.String2(self._io, self, self._root))



    class String2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len = self._io.read_u2le()
            self.value = (self._io.read_bytes(self.len)).decode(u"UTF-8")



