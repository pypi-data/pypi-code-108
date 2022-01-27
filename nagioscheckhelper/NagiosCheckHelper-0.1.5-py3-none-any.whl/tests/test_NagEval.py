from unittest import TestCase

from NagiosCheckHelper import NagErrors, NagEval

class TestNagEval_evalEnum(TestCase):

    def test_default(self):
        eo = NagErrors()
        ev = NagEval(eo)

        ev.evalEnum('Junk', defaultStatus='OK')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalEnum('Junk', defaultStatus='WARNING')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalEnum('Junk', defaultStatus='CRITICAL')
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalEnum('Junk', defaultStatus='UNKNOWN')
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

    def test_bin_value(self):
        eo = NagErrors()
        ev = NagEval(eo)

        ev.evalEnum('OKVal', okValues=['OKVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalEnum('WarningVal', warningValues=['WarningVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalEnum('CriticalVal', criticalValues=['CriticalVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalEnum('UnknownVal', unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalEnum('OKVal', okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalEnum('WarningVal', okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalEnum('CriticalVal', okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalEnum('UnknownVal', okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalEnum('Warning', warningValues=['Warning'], prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test value is Warning")

    def test_postfixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalEnum('Warning', warningValues=['Warning'], postfixText=" String")
        self.assertEqual(eo.warning[0], "value is Warning String")


class TestNagEval_evalListEnum(TestCase):

    def test_default(self):
        eo = NagErrors()
        ev = NagEval(eo)

        ev.evalListEnum(['Junk'], unknownValueStatus='OK')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalListEnum(['Junk'], unknownValueStatus='WARNING')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalListEnum(['Junk'], unknownValueStatus='CRITICAL')
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalListEnum(['Junk'], unknownValueStatus='UNKNOWN')
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

    def test_bin_value(self):
        eo = NagErrors()
        ev = NagEval(eo)

        ev.evalListEnum(['OKVal'], okValues=['OKVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalListEnum(['WarningVal'], warningValues=['WarningVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalListEnum(['CriticalVal'], criticalValues=['CriticalVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalListEnum(['UnknownVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum(['OKVal'], okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalListEnum(['WarningVal'], okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalListEnum(['CriticalVal'], okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalListEnum(['UnknownVal'], okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)
    
    def test_bin_valuelist(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum(['OKVal', 'OKVal', 'WarningVal', 'WarningVal', 'CriticalVal'], okValues=['OKVal'], warningValues=['WarningVal'], criticalValues=['CriticalVal'], unknownValues=['UnknownVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 2)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_unknownValues(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum(['junkVal'], unknownValueStatus="OK")
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

        ev.evalListEnum(['junkVal'], unknownValueStatus="WARNING")
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
        
        ev.evalListEnum(['junkVal'], unknownValueStatus="CRITICAL")
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)
        
        ev.evalListEnum(['junkVal'])
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)

    def test_emptyList(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum([], emptyStatus="OK")
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)
        ev.evalListEnum([], emptyStatus="WARNING")
        self.assertEqual(eo.warning[0], "list is Empty")
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_string(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum('WarningVal', warningValues=['WarningVal'])
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.warning[0], "value is WarningVal")
        self.assertEqual(eo.getExitCode(), 1)

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum(['Warning'], warningValues=['Warning'], prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test value is Warning")

    def test_postfixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListEnum(['Warning'], warningValues=['Warning'], postfixText=" String")
        self.assertEqual(eo.warning[0], "value is Warning String")


class TestNagEval_evalNumberAsc(TestCase):

    def test_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(20, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(45, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(55, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(-20, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_negative_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(-8, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(-3, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 2)

    def test_swappedTresholds(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(51, warningAbove=50, criticalAbove=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_numberUnits(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(45, warningAbove=40, numberUnits="sec")
        self.assertEqual(eo.warning[0], "45sec is > 40sec")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(45, warningAbove=40, prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test 45 is > 40")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberAsc(45, warningAbove=40, postfixText=" Units")
        self.assertEqual(eo.warning[0], "45 is > 40 Units")


class TestNagEval_evalListNumberAsc(TestCase):

    def test_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([20], warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([45], warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([55], warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([-20], warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_negative_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([-8], warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([-3], warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 2)

    def test_swappedTresholds(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([51], warningAbove=50, criticalAbove=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_numberUnits(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([45], warningAbove=40, numberUnits="sec")
        self.assertEqual(eo.warning[0], "45sec is > 40sec")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([45], warningAbove=40, prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test 45 is > 40")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([45], warningAbove=40, postfixText=" Units")
        self.assertEqual(eo.warning[0], "45 is > 40 Units")

    def test_bin_valuelist(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([5, 200, 52, 4000], warningAbove=100, criticalAbove=2000)
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)

    def test_emptyList(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc([], emptyStatus="OK")
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)
        ev.evalListNumberAsc([], emptyStatus="WARNING")
        self.assertEqual(eo.warning[0], "list is Empty")
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_string(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberAsc(50, warningAbove=25, criticalAbove=100)
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.warning[0], "50 is > 25")
        self.assertEqual(eo.getExitCode(), 1)


class TestNagEval_evalNumberDesc(TestCase):

    def test_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(20, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(45, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(55, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 0)

    def test_negative_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(-20, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_negative_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(-8, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(-3, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 0)

    def test_swappedTresholds(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(21, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_numberUnits(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(45, warningBelow=50, numberUnits="sec")
        self.assertEqual(eo.warning[0], "45sec is < 50sec")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(45, warningBelow=50, prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test 45 is < 50")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberDesc(45, warningBelow=50, postfixText=" Units")
        self.assertEqual(eo.warning[0], "45 is < 50 Units")


class TestNagEval_evalListNumberDesc(TestCase):

    def test_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([20], warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([45], warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([55], warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 0)

    def test_negative_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([-20], warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_negative_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([-8], warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([-3], warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 0)

    def test_swappedTresholds(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([21], warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_numberUnits(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([45], warningBelow=50, numberUnits="sec")
        self.assertEqual(eo.warning[0], "45sec is < 50sec")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([45], warningBelow=50, prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test 45 is < 50")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([45], warningBelow=50, postfixText=" Units")
        self.assertEqual(eo.warning[0], "45 is < 50 Units")

    def test_bin_valuelist(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([5, 200, 52, 4000], warningBelow=2000, criticalBelow=100)
        self.assertEqual(len(eo.critical), 2)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)

    def test_emptyList(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc([], emptyStatus="OK")
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)
        ev.evalListNumberDesc([], emptyStatus="WARNING")
        self.assertEqual(eo.warning[0], "list is Empty")
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_string(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalListNumberDesc(55, warningBelow=100, criticalBelow=50)
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.warning[0], "55 is < 100")
        self.assertEqual(eo.getExitCode(), 1)


class TestNagEval_evalNumberRange(TestCase):

    def test_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(20, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(55, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 0)

    def test_low2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(20, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_mid2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 1)

    def test_high2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(55, warningAbove=40, criticalAbove=50)
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_low_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(35, warningRange="30:40", criticalRange="20:50")
        self.assertEqual(eo.getExitCode(), 0)
    
    def test_mid_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningRange="30:40", criticalRange="20:50")
        self.assertEqual(eo.getExitCode(), 1)

    def test_high_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(55, warningRange="30:40", criticalRange="20:50")
        self.assertEqual(eo.getExitCode(), 2)
    
    def test_mid_range_desc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(25, warningRange="30:40", criticalRange="20:50")
        self.assertEqual(eo.getExitCode(), 1)

    def test_high_range_desc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(15, warningRange="30:40", criticalRange="20:50")
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_low(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-20, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_mid(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-8, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 1)

    def test_negative_high(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-3, warningBelow=-5, criticalBelow=-10)
        self.assertEqual(eo.getExitCode(), 0)

    def test_negative_low2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-20, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 0)

    def test_negative_mid2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-8, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 1)

    def test_negative_high2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-3, warningAbove=-10, criticalAbove=-5)
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_low_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-25, warningRange="-30:-20", criticalRange="-40:-10")
        self.assertEqual(eo.getExitCode(), 0)

    def test_negative_mid_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-35, warningRange="-30:-20", criticalRange="-40:-10")
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high_range_asc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-45, warningRange="-30:-20", criticalRange="-40:-10")
        self.assertEqual(eo.getExitCode(), 2)

    def test_negative_mid_range_desc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-15, warningRange="-30:-20", criticalRange="-40:-10")
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_negative_high_range_desc(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(-5, warningRange="-30:-20", criticalRange="-40:-10")
        self.assertEqual(eo.getExitCode(), 2)

    def test_swappedTresholds(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(21, warningBelow=50, criticalBelow=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_swappedTresholds2(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(51, warningAbove=50, criticalAbove=40)
        self.assertEqual(eo.getExitCode(), 2)

    def test_numberUnits(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningBelow=50, numberUnits="sec")
        self.assertEqual(eo.warning[0], "45sec is < 50sec")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningBelow=50, prefixText="Test ")
        self.assertEqual(eo.warning[0], "Test 45 is < 50")

    def test_prefixText(self):
        eo = NagErrors()
        ev = NagEval(eo)
        ev.evalNumberRange(45, warningBelow=50, postfixText=" Units")
        self.assertEqual(eo.warning[0], "45 is < 50 Units")
