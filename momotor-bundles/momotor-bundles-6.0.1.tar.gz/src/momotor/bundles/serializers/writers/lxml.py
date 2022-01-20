try:
    from xsdata.formats.dataclass.serializers.writers import LxmlEventWriter

except ImportError:
    LxmlBundleEventWriter = None

else:
    class LxmlBundleEventWriter(LxmlEventWriter):
        pass
