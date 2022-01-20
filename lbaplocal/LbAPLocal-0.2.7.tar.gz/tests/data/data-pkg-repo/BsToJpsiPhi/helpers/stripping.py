from __future__ import print_function

from Configurables import (
    DaVinci,
    GaudiSequencer,
    EventNodeKiller,
    ProcStatusCheck
)
from StrippingConf.Configuration import (
    StrippingConf,
    StrippingStream
)
from StrippingSettings.Utils import strippingConfiguration
from StrippingArchive.Utils import buildStreams
from StrippingArchive import strippingArchive

from DSTWriters.microdstelements import *
from DSTWriters.Configuration import (
    SelDSTWriter,
    stripDSTStreamConf,
    stripDSTElements
)

STRIPPING_VERSIONS = {
    '2011': 'Stripping21r1',
    '2012': 'Stripping21',
    '2015': 'Stripping24r1',
    '2016': 'Stripping28r1',
    '2017': 'Stripping29r2',
    '2018': 'Stripping34'
}

def stripping(data_type, stripping_line):
    # kill the banks
    event_node_killer = EventNodeKiller('StripKiller')
    event_node_killer.Nodes = ['/Event/AllStreams', '/Event/Strip']

    # figure out stripping version from the year
    stripping_version = STRIPPING_VERSIONS[data_type]
    # build streams
    streams = buildStreams(stripping=strippingConfiguration(stripping_version),
                           archive=strippingArchive(stripping_version))
    # declare your custom stream
    custom_stream = StrippingStream('AllStreams')
    custom_line = 'Stripping'+stripping_line

    for stream in streams:
        for sline in stream.lines:
            if sline.name() == custom_line:
                sline._prescale = 1.0
                custom_stream.appendLines([sline])

    filterBadEvents = ProcStatusCheck()

    # configure your custom stream
    sc = StrippingConf(Streams=[custom_stream],
                       MaxCandidates=2000,
                       AcceptBadEvents=False,
                       BadEventSelection=filterBadEvents)

    enablePacking = False

    SelDSTWriterElements = {'default': stripDSTElements(pack=enablePacking)}

    SelDSTWriterConf = {'default': stripDSTStreamConf(pack=enablePacking,
                                                      selectiveRawEvent=True,
                                                      fileExtension='.anaprod_bstojpsiphi.ldst')}

    dstWriter = SelDSTWriter('MyDSTWriter',
                             StreamConf=SelDSTWriterConf,
                             MicroDSTElements=SelDSTWriterElements,
                             OutputFileSuffix='',
                             SelectionSequences=sc.activeStreams()
                             )

    DaVinci().ProductionType = 'Stripping'
    seq = GaudiSequencer('TupleSeq')
    seq.IgnoreFilterPassed = True
    seq.Members += [event_node_killer, sc.sequence()] + [dstWriter.sequence()]

    # This is a hack to work around https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC/merge_requests/736/
    if getattr(stripping, 'NEED_FILENAME_PATCH', True):
        import atexit
        atexit.register(fix_filenames)
        stripping.NEED_FILENAME_PATCH = False

    return seq


def fix_filenames():
    """This is a hack to work around https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC/merge_requests/736/"""
    import glob
    import os
    for fn in glob.glob('*.anaprod_bstojpsiphi.ldst'):
        print('Renaming', fn, 'to', fn.lower())
        os.rename(fn, fn.lower())

        for xml_fn in glob.glob('summaryDaVinci_*.xml'):
            print('Fixing XML in', xml_fn)
            with open(xml_fn, 'rt') as fp:
                xml = fp.read()
            xml = xml.replace(fn, fn.lower())
            with open(xml_fn, 'wt') as fp:
                fp.write(xml)

        print('Fixing pool_xml_catalog.xml')
        with open('pool_xml_catalog.xml', 'rt') as fp:
            xml = fp.read()
        xml = xml.replace(fn, fn.lower())
        with open('pool_xml_catalog.xml', 'wt') as fp:
            fp.write(xml)
