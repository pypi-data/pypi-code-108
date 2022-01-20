class Tu:
    def __init__(self, src):
        self._src = src
        self._tgt = None
        self._segs = []
        self._seg_mask = ""

    def get_src(self):
        return self._src

    src = property(get_src)

    def get_tgt(self):
        if self._tgt is None:
            if not self._segs:
                self._tgt = self._src
            else:
                tgts = []
                for seg in self._segs:
                    tgts.append(seg.tgt)
                self._tgt = self._seg_mask.format(*tgts)
        return self._tgt

    tgt = property(get_tgt)

    def get_tgt_as_seg_with_white(self):
        if not self._segs:
            return [self._src]
        first_occurence = "@"
        mask = self._seg_mask.replace("{}", first_occurence, 1)
        mask = mask.replace("{}", "|{}")
        mask = mask.replace(first_occurence, "{}")
        masks = mask.split("|")
        segs_with_white = []
        for i, seg in enumerate(self._segs):
            segs_with_white.append(masks[i].format(seg.tgt))
        return segs_with_white

    def get_segs(self):
        return self._segs

    def set_segs_and_mask(self, segs, seg_mask):
        self._segs = segs
        self._seg_mask = seg_mask

    segs = property(get_segs)

    def get_seg_mask(self):
        return self._seg_mask

    seg_mask = property(get_seg_mask)
