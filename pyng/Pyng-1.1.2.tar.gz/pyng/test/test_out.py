#!/usr/bin/python
"""
    test_out.py                      Nat Goodspeed
    Copyright (C) 2015               Nat Goodspeed

NRG 2015-11-07
"""

import unittest
from pyng import out

class Buffer(object):
    def __init__(self, outlist):
        self.buffer = []
        self.outlist = outlist

    def write(self, item):
        self.buffer.append(item)

    def flush(self):
        self.outlist[:] = self.buffer
        self.buffer = []

class TestOut(unittest.TestCase):
    def setUp(self):
        pass

    def test_maybe_adapt(self):
        class Nothin(object):
            pass
        class JustWrite(Nothin):
            def write(self, item):
                pass
        class WriteFlush(JustWrite):
            def flush(self):
                pass
        def mywrite(item):
            pass
        def myflush():
            pass
        just_write = JustWrite()
        write_flush = WriteFlush()
        self.assert_(out.ofilter(write_flush).sink is write_flush)
        self.check_adapter_write(out.ofilter(just_write).sink, just_write.write)
        self.assertRaises(out.OutError, out.ofilter, Nothin())
        self.check_adapter_write(out.ofilter(write=mywrite).sink, mywrite)
        self.check_adapter_write_flush(out.ofilter(write=mywrite, flush=myflush).sink,
                                       mywrite, myflush)

    def check_adapter_write(self, sink, write):
        self.assert_(isinstance(sink, out.adapter))
        self.assert_(self.same_bound_method(sink.write, write))

    def check_adapter_write_flush(self, sink, write, flush):
        self.check_adapter_write(sink, write)
        self.assert_(self.same_bound_method(sink.flush, flush))

    def same_bound_method(self, left, right):
        if left is right:
            return True
        # The "is" test doesn't work when you assign an already-bound method
        # as an attribute of an existing object! You get a different instance
        # with the same im_class, im_self, im_func attributes. Test those.
        try:
            # Python 3
            return left.__self__.__class__ is right.__self__.__class__ \
               and left.__self__  is right.__self__ \
               and left.__func__  is right.__func__
        except AttributeError:
            # Python 2
            return left.im_class is right.im_class \
               and left.im_self  is right.im_self \
               and left.im_func  is right.im_func

    def test_buffer_lines(self):
        capture = []
        buff = out.buffer_lines(write=capture.append)
        # print >>buff, "This", "is", "a", "test"
        for item in (
            "This",
            " ",
            "is",
            " ",
            "a",
            " ",
            "test",
            "\n",
            ):
            buff.write(item)
        self.assertEqual(capture, ["This is a test"])

        fragments = (
            "first ",
            "line\nsecond line\nthird line\nfourth ",
            "line\nfifth ",
            "line\n",
            )
        # The simplest way to clear capture is to assign a new empty list. But
        # if we do that, we must also reinitialize buff, which holds the
        # append method for the previous list instance. Instead, clear capture
        # by deleting its contents.
        del capture[:]
        for item in fragments:
            buff.write(item)
        self.assertEqual(capture,
            [
            "first line",
            "second line",
            "third line",
            "fourth line",
            "fifth line",
            ])
        del capture[:]
        for item in fragments[:2]:
            buff.write(item)
        # At this point "fourth " should still be in the internal buffer,
        # rather than in the output list.
        self.assertEqual(capture,
            [
            "first line",
            "second line",
            "third line",
            ])
        buff.flush()
        # Flushed "fourth " to the output list.
        self.assertEqual(capture,
            [
            "first line",
            "second line",
            "third line",
            "fourth "
            ])
        del capture[:]
        # Normally we would expect to use "\n" or "\r\n" for eol, but for test
        # purposes, this is easier to eyeball.
        buff = out.buffer_lines(write=capture.append, eol="!")
        for item in fragments[:2]:
            buff.write(item)
        self.assertEqual(capture,
            [
            "first line!",
            "second line!",
            "third line!",
            ])
        del capture[:]
        buff = out.buffer_lines(Buffer(capture))
        for item in fragments[:2]:
            buff.write(item)
        # Because this new 'buff' instance uses Buffer as its sink, 'capture'
        # itself contains nothing yet.
        self.assertEqual(capture, [])
        buff.flush()
        # This tests that buffer_lines.flush() properly propagates the flush()
        # call through to its sink. Not only should we flush "fourth " to
        # Buffer, but Buffer.flush() should then populate capture.
        self.assertEqual(capture,
            [
            "first line",
            "second line",
            "third line",
            "fourth "
            ])

if __name__ == "__main__":
    unittest.main()
