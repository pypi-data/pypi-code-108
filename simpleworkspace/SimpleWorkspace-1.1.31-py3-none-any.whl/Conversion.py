class Bytes:
    KB = 1000
    MB = KB * 1000
    GB = MB * 1000
    TB = GB * 1000

    def __init__(self):
        return

    @staticmethod
    def GetStringRepresentation(totBytes: int, prefix: str, precisionDecimals=2):
        """
        :param prefix: b, kb, mb, gb
        """
        if prefix == "b":
            return str(totBytes) + " B"
        elif prefix == "kb":
            return str(round(totBytes / Bytes.KB, precisionDecimals)) + " KB"
        elif prefix == "mb":
            return str(round(totBytes / Bytes.MB, precisionDecimals)) + " MB"
        elif prefix == "gb":
            return str(round(totBytes / Bytes.GB, precisionDecimals)) + " GB"
        else:
            raise Exception("Incorrect prefix!")


class Time:
    Minute = 60
    Hour = 60 * Minute
    Day = 24 * Hour
    Week = 7 * Day