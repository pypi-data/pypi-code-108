import py_fort_hermes as fh


def CheckVersion(version):
    if version not in {(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)}:
        raise fh.InternalError(fh.ErrorCode.FH_STREAM_WRONG_VERSION,
                               "unsupported version %d.%d" % (version[0], version[1]))


def CheckFileHeader(header):
    CheckVersion((header.version.vmajor, header.version.vminor))
    if header.type != fh.Header.File:
        raise fh.InternalError(fh.ErrorCode.FH_STREAM_NO_HEADER,
                               "wrong header type")
    if header.width == 0:
        raise fh.InternalError(fh.ErrorCode.FH_STREAM_NO_HEADER,
                               "missing width")
    if header.height == 0:
        raise fh.InternalError(fh.ErrorCode.FH_STREAM_NO_HEADER,
                               "missing height")


def CheckNetworkHeader(header):
    CheckVersion((header.version.vmajor, header.version.vminor))
    if header.type != fh.Header.Network:
        raise fh.InternalError(fh.ErrorCode.FH_STREAM_NO_HEADER,
                               "wrong header type")
