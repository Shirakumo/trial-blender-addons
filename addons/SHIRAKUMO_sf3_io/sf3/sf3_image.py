# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

from . import kaitaistruct
from .kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sf3Image(ReadWriteKaitaiStruct):
    """
    .. seealso::
       Source - https://shirakumo.org/docs/sf3
    """

    class Layouts(IntEnum):
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

    class Formats(IntEnum):
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
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.magic = self._io.read_bytes(10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, self._io, u"/seq/0")
        self.format_id = self._io.read_bytes(1)
        if not (self.format_id == b"\x03"):
            raise kaitaistruct.ValidationNotEqualError(b"\x03", self.format_id, self._io, u"/seq/1")
        self.checksum = self._io.read_u4le()
        self.null_terminator = self._io.read_bytes(1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, self._io, u"/seq/3")
        self.image = Sf3Image.Image(self._io, self, self._root)
        self.image._read()


    def _fetch_instances(self):
        pass
        self.image._fetch_instances()


    def _write__seq(self, io=None):
        super(Sf3Image, self)._write__seq(io)
        self._io.write_bytes(self.magic)
        self._io.write_bytes(self.format_id)
        self._io.write_u4le(self.checksum)
        self._io.write_bytes(self.null_terminator)
        self.image._write__seq(self._io)


    def _check(self):
        pass
        if (len(self.magic) != 10):
            raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 10)
        if not (self.magic == b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A"):
            raise kaitaistruct.ValidationNotEqualError(b"\x81\x53\x46\x33\x00\xE0\xD0\x0D\x0A\x0A", self.magic, None, u"/seq/0")
        if (len(self.format_id) != 1):
            raise kaitaistruct.ConsistencyError(u"format_id", len(self.format_id), 1)
        if not (self.format_id == b"\x03"):
            raise kaitaistruct.ValidationNotEqualError(b"\x03", self.format_id, None, u"/seq/1")
        if (len(self.null_terminator) != 1):
            raise kaitaistruct.ConsistencyError(u"null_terminator", len(self.null_terminator), 1)
        if not (self.null_terminator == b"\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x00", self.null_terminator, None, u"/seq/3")
        if self.image._root != self._root:
            raise kaitaistruct.ConsistencyError(u"image", self.image._root, self._root)
        if self.image._parent != self:
            raise kaitaistruct.ConsistencyError(u"image", self.image._parent, self)

    class Image(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

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
                    pass
                    self.samples.append(self._io.read_u2le())
                elif _on == Sf3Image.Formats.uint64:
                    pass
                    self.samples.append(self._io.read_u8le())
                elif _on == Sf3Image.Formats.int16:
                    pass
                    self.samples.append(self._io.read_s2le())
                elif _on == Sf3Image.Formats.uint32:
                    pass
                    self.samples.append(self._io.read_u4le())
                elif _on == Sf3Image.Formats.float16:
                    pass
                    _t_samples = Sf3Image.F2(self._io, self, self._root)
                    _t_samples._read()
                    self.samples.append(_t_samples)
                elif _on == Sf3Image.Formats.int8:
                    pass
                    self.samples.append(self._io.read_s1())
                elif _on == Sf3Image.Formats.float32:
                    pass
                    self.samples.append(self._io.read_f4le())
                elif _on == Sf3Image.Formats.uint8:
                    pass
                    self.samples.append(self._io.read_u1())
                elif _on == Sf3Image.Formats.float64:
                    pass
                    self.samples.append(self._io.read_f8le())
                elif _on == Sf3Image.Formats.int64:
                    pass
                    self.samples.append(self._io.read_s8le())
                elif _on == Sf3Image.Formats.int32:
                    pass
                    self.samples.append(self._io.read_s4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.samples)):
                pass
                _on = self.format
                if _on == Sf3Image.Formats.uint16:
                    pass
                elif _on == Sf3Image.Formats.uint64:
                    pass
                elif _on == Sf3Image.Formats.int16:
                    pass
                elif _on == Sf3Image.Formats.uint32:
                    pass
                elif _on == Sf3Image.Formats.float16:
                    pass
                    self.samples[i]._fetch_instances()
                elif _on == Sf3Image.Formats.int8:
                    pass
                elif _on == Sf3Image.Formats.float32:
                    pass
                elif _on == Sf3Image.Formats.uint8:
                    pass
                elif _on == Sf3Image.Formats.float64:
                    pass
                elif _on == Sf3Image.Formats.int64:
                    pass
                elif _on == Sf3Image.Formats.int32:
                    pass



        def _write__seq(self, io=None):
            super(Sf3Image.Image, self)._write__seq(io)
            self._io.write_u4le(self.width)
            self._io.write_u4le(self.height)
            self._io.write_u4le(self.depth)
            self._io.write_u1(int(self.channel_format))
            self._io.write_u1(int(self.format))
            for i in range(len(self.samples)):
                pass
                _on = self.format
                if _on == Sf3Image.Formats.uint16:
                    pass
                    self._io.write_u2le(self.samples[i])
                elif _on == Sf3Image.Formats.uint64:
                    pass
                    self._io.write_u8le(self.samples[i])
                elif _on == Sf3Image.Formats.int16:
                    pass
                    self._io.write_s2le(self.samples[i])
                elif _on == Sf3Image.Formats.uint32:
                    pass
                    self._io.write_u4le(self.samples[i])
                elif _on == Sf3Image.Formats.float16:
                    pass
                    self.samples[i]._write__seq(self._io)
                elif _on == Sf3Image.Formats.int8:
                    pass
                    self._io.write_s1(self.samples[i])
                elif _on == Sf3Image.Formats.float32:
                    pass
                    self._io.write_f4le(self.samples[i])
                elif _on == Sf3Image.Formats.uint8:
                    pass
                    self._io.write_u1(self.samples[i])
                elif _on == Sf3Image.Formats.float64:
                    pass
                    self._io.write_f8le(self.samples[i])
                elif _on == Sf3Image.Formats.int64:
                    pass
                    self._io.write_s8le(self.samples[i])
                elif _on == Sf3Image.Formats.int32:
                    pass
                    self._io.write_s4le(self.samples[i])



        def _check(self):
            pass
            if (len(self.samples) != (((self.depth * self.height) * self.width) * self.channel_count)):
                raise kaitaistruct.ConsistencyError(u"samples", len(self.samples), (((self.depth * self.height) * self.width) * self.channel_count))
            for i in range(len(self.samples)):
                pass
                _on = self.format
                if _on == Sf3Image.Formats.uint16:
                    pass
                elif _on == Sf3Image.Formats.uint64:
                    pass
                elif _on == Sf3Image.Formats.int16:
                    pass
                elif _on == Sf3Image.Formats.uint32:
                    pass
                elif _on == Sf3Image.Formats.float16:
                    pass
                    if self.samples[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"samples", self.samples[i]._root, self._root)
                    if self.samples[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"samples", self.samples[i]._parent, self)
                elif _on == Sf3Image.Formats.int8:
                    pass
                elif _on == Sf3Image.Formats.float32:
                    pass
                elif _on == Sf3Image.Formats.uint8:
                    pass
                elif _on == Sf3Image.Formats.float64:
                    pass
                elif _on == Sf3Image.Formats.int64:
                    pass
                elif _on == Sf3Image.Formats.int32:
                    pass


        @property
        def channel_count(self):
            if hasattr(self, '_m_channel_count'):
                return self._m_channel_count

            self._m_channel_count = (int(self.channel_format) & 15)
            return getattr(self, '_m_channel_count', None)

        def _invalidate_channel_count(self):
            del self._m_channel_count

    class F2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.bits = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sf3Image.F2, self)._write__seq(io)
            self._io.write_u2le(self.bits)


        def _check(self):
            pass



