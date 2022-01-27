def np_info_repr(self):
    data = "<akida.NP.Info"
    data += ", ident=" + str(self.ident)
    data += ", types=" + str(self.types) + ">"
    return data


def np_mesh_repr(self):
    data = "<akida.NP.Mesh"
    data += ", dma_event=" + str(self.dma_event)
    data += ", dma_conf=" + str(self.dma_conf)
    data += ", nps=" + str(self.nps) + ">"
    return data


def np_mapping_repr(self):
    return "<akida.NP.Mapping" + \
            ", ident=" + str(self.ident) + \
            ", type=" + str(self.type) + \
            ", filters=" + str(self.filters) + \
            ", single_buffer=" + str(self.single_buffer) + ">"
