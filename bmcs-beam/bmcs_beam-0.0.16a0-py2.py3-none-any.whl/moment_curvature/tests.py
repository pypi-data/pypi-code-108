import traits.api as tr


class TestFirst(tr.HasTraits):
    test_first_var = tr.String('test_first!')


class Test(tr.HasTraits):
    test_first = tr.Instance(TestFirst, ())
    test_var = tr.String('test!')


class BeamDesign(tr.HasTraits):
    test = tr.Instance(Test, ())
    name = tr.String('homam')


class MomentCurvature(tr.HasTraits):
    beam_design = tr.Instance(BeamDesign, ())

    # Use PrototypedFrom only when the prototyped object is a class (The prototyped attribute behaves similarly
    # to a delegated attribute, until it is explicitly changed; from that point forward, the prototyped attribute
    # changes independently from its prototype.)
    # test = tr.PrototypedFrom('beam_design', 'test')
    test = tr.DelegatesTo('beam_design')

    test_first = tr.PrototypedFrom('test', 'test_first')

    # def _test_default(self):
    #     return self.beam_design.test

    test_var = tr.DelegatesTo('test')
    name = tr.DelegatesTo('beam_design')
    test_first_var = tr.DelegatesTo('test_first')


if __name__ == '__main__':
    test = Test(test_var='test1')
    bd = BeamDesign(name='asdasd', test=test)
    mc = MomentCurvature(beam_design = bd)
    print(mc.test.test_var)
    # print(mc.name)
    # print(mc.test_first_var)

    # mc = MomentCurvature(bbb=25)
    #
    # print(mc.bbb)
