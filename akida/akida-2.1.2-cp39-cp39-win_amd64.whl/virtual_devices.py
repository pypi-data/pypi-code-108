from .core import Device, HwVersion, NSoC_v2, NP


def AKD1000():
    """Returns a virtual device for an AKD1000 NSoC.

    This function returns a virtual device for the Brainchip's AKD1000
    NSoC.

    Returns:
        :obj:`Device`: a virtual device.

    """
    dma_event = NP.Ident(3, 1, 0)
    dma_conf = NP.Ident(3, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(2, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(2, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 1, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(3, 1, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(3, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(3, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(3, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 1, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 1), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 2), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 1, 3), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(4, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(4, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(4, 5, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 2, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 2, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 3, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 4, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 4, 3), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(5, 5, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(5, 5, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]
    mesh = NP.Mesh(dma_event, dma_conf, nps)
    return Device(NSoC_v2, mesh)


def TwoNodesIP():
    """Returns a virtual device for a two nodes Akida IP.

    Returns:
        :obj:`Device`: a virtual device.

    """
    hw_version = HwVersion(0xBC, 0xA1, 3, 0)
    dma_event = NP.Ident(1, 1, 0)
    dma_conf = NP.Ident(1, 1, 1)
    nps = [
        NP.Info(NP.Ident(1, 2, 0), {NP.Type.CNP1, NP.Type.FNP2}),
        NP.Info(NP.Ident(1, 2, 1), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 2), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 2, 3), {NP.Type.CNP1}),
        NP.Info(NP.Ident(1, 3, 0), {NP.Type.CNP1, NP.Type.FNP3}),
        NP.Info(NP.Ident(1, 3, 1), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 2), {NP.Type.CNP1, NP.Type.CNP2}),
        NP.Info(NP.Ident(1, 3, 3), {NP.Type.CNP1, NP.Type.CNP2})
    ]
    mesh = NP.Mesh(dma_event, dma_conf, nps)
    return Device(hw_version, mesh)
