# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from . import kaitaistruct
from .kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3Image(KaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """

    class Layouts(Enum):
        v = 1
        va = 2
        rgb = 3
        rgba = 4
        av = 18
        bgr = 19
        abgr = 20
        argb = 36
        bgra = 52
        cmyk = 68
        kmyc = 84

    class Formats(Enum):
        int8 = 1
        int16 = 2
        int32 = 4
        int64 = 8
        uint8 = 17
        uint16 = 18
        uint32 = 20
        uint64 = 24
        float16 = 34
        float32 = 36
        float64 = 40
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
        if not self.format_id == b"\x03":
            raise kaitaistruct.ValidationNotEqualError(b"\x03", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not self.null_terminator == b"\x00":
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.image = Sf3Image.Image(self._io, self, self._root)

    class Image(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.depth = self._io.read_u4le()
            self.channel_format = KaitaiStream.resolve_enum(Sf3Image.Layouts, self._io.read_u1())
            self.format = KaitaiStream.resolve_enum(Sf3Image.Formats, self._io.read_u1())
            self.samples = []
            for i in range((((self.depth * self.height) * self.width) * self.channel_count)):
                _on = self.format
                if _on == Sf3Image.Formats.uint16:
                    self.samples.append(self._io.read_u2le())
                elif _on == Sf3Image.Formats.uint64:
                    self.samples.append(self._io.read_u8le())
                elif _on == Sf3Image.Formats.int16:
                    self.samples.append(self._io.read_s2le())
                elif _on == Sf3Image.Formats.uint32:
                    self.samples.append(self._io.read_u4le())
                elif _on == Sf3Image.Formats.float16:
                    self.samples.append(Sf3Image.F2(self._io, self, self._root))
                elif _on == Sf3Image.Formats.int8:
                    self.samples.append(self._io.read_s1())
                elif _on == Sf3Image.Formats.float32:
                    self.samples.append(self._io.read_f4le())
                elif _on == Sf3Image.Formats.uint8:
                    self.samples.append(self._io.read_u1())
                elif _on == Sf3Image.Formats.float64:
                    self.samples.append(self._io.read_f8le())
                elif _on == Sf3Image.Formats.int64:
                    self.samples.append(self._io.read_s8le())
                elif _on == Sf3Image.Formats.int32:
                    self.samples.append(self._io.read_s4le())


        @property
        def channel_count(self):
            if hasattr(self, '_m_channel_count'):
                return self._m_channel_count

            self._m_channel_count = (self.channel_format.value & 15)
            return getattr(self, '_m_channel_count', None)


    class F2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bits = self._io.read_u2le()



