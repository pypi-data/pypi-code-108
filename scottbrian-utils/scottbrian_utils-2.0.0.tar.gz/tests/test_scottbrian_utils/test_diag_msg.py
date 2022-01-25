"""test_diag_msg.py module."""

from datetime import datetime
# noinspection PyProtectedMember
from sys import _getframe
import sys  # noqa: F401

from typing import Any, cast, Deque, Final, List, NamedTuple, Optional, Union
# from typing import Text, TypeVar
# from typing_extensions import Final

import pytest
from collections import deque

from scottbrian_utils.diag_msg import get_caller_info
from scottbrian_utils.diag_msg import get_formatted_call_sequence
from scottbrian_utils.diag_msg import diag_msg
from scottbrian_utils.diag_msg import CallerInfo
from scottbrian_utils.diag_msg import diag_msg_datetime_fmt
from scottbrian_utils.diag_msg import get_formatted_call_seq_depth
from scottbrian_utils.diag_msg import diag_msg_caller_depth

########################################################################
# MyPy experiments
########################################################################
# AnyStr = TypeVar('AnyStr', Text, bytes)
#
# def concat(x: AnyStr, y: AnyStr) -> AnyStr:
#     return x + y
#
# x = concat('my', 'pie')
#
# reveal_type(x)
#
# class MyStr(str): ...
#
# x = concat(MyStr('apple'), MyStr('pie'))
#
# reveal_type(x)


########################################################################
# DiagMsgArgs NamedTuple
########################################################################
class DiagMsgArgs(NamedTuple):
    """Structure for the testing of various args for diag_msg."""
    arg_bits: int
    dt_format_arg: str
    depth_arg: int
    msg_arg: List[Union[str, int]]
    file_arg: str


########################################################################
# depth_arg fixture
########################################################################
depth_arg_list = [None, 0, 1, 2, 3]


@pytest.fixture(params=depth_arg_list)  # type: ignore
def depth_arg(request: Any) -> int:
    """Using different depth args.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# file_arg fixture
########################################################################
file_arg_list = [None, 'sys.stdout', 'sys.stderr']


@pytest.fixture(params=file_arg_list)  # type: ignore
def file_arg(request: Any) -> str:
    """Using different file arg.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


########################################################################
# latest_arg fixture
########################################################################
latest_arg_list = [None, 0, 1, 2, 3]


@pytest.fixture(params=latest_arg_list)  # type: ignore
def latest_arg(request: Any) -> Union[int, None]:
    """Using different depth args.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# msg_arg fixture
########################################################################
msg_arg_list = [[None],
                ['one-word'],
                ['two words'],
                ['three + four'],
                ['two', 'items'],
                ['three', 'items', 'for you'],
                ['this', 'has', 'number', 4],
                ['here', 'some', 'math', 4 + 1]]


@pytest.fixture(params=msg_arg_list)  # type: ignore
def msg_arg(request: Any) -> List[str]:
    """Using different message arg.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(List[str], request.param)


########################################################################
# seq_slice is used to get a contiguous section of the sequence string
# which is needed to verify get_formatted_call_seq invocations where
# latest is non-zero or depth is beyond our known call sequence (i.e.,
# the call seq string has system functions prior to calling the test
# case)
########################################################################
def seq_slice(call_seq: str,
              start: int = 0,
              end: Optional[int] = None
              ) -> str:
    """Return a reduced depth call sequence string.

    Args:
        call_seq: The call sequence string to slice
        start: Species the latest entry to return with zero being the
                 most recent
        end: Specifies one entry earlier than the earliest entry to
               return

    Returns:
          A slice of the input call sequence string
    """
    seq_items = call_seq.split(' -> ')

    # Note that we allow start and end to both be zero, in which case an
    # empty sequence is returned. Also note that the sequence is earlier
    # calls to later calls from left to right, so a start of zero means
    # the end of the sequence (the right most entry) and the end is the
    # depth, meaning how far to go left toward earlier entries. The
    # following code reverses the meaning of start and end so that we
    # can slice the sequence without having to first reverse it.

    adj_end = len(seq_items) - start
    assert 0 <= adj_end  # ensure not beyond number of items

    adj_start = 0 if end is None else len(seq_items) - end
    assert 0 <= adj_start  # ensure not beyond number of items

    ret_seq = ''
    arrow = ' -> '
    for i in range(adj_start, adj_end):
        if i == adj_end - 1:  # if last item
            arrow = ''
        ret_seq = f'{ret_seq}{seq_items[i]}{arrow}'

    return ret_seq


########################################################################
# get_exp_seq is a helper function used by many test cases
########################################################################
def get_exp_seq(exp_stack: Deque[CallerInfo],
                latest: int = 0,
                depth: Optional[int] = None
                ) -> str:
    """Return the expected call sequence string based on the exp_stack.

    Args:
        exp_stack: The expected stack as modified by each test case
        depth: The number of entries to build
        latest: Specifies where to start in the seq for the most recent
                  entry

    Returns:
          The call string that get_formatted_call_sequence is expected
           to return
    """
    if depth is None:
        depth = len(exp_stack) - latest
    exp_seq = ''
    arrow = ''
    for i, exp_info in enumerate(reversed(exp_stack)):
        if i < latest:
            continue
        if i == latest + depth:
            break
        if exp_info.func_name:
            dbl_colon = '::'
        else:
            dbl_colon = ''
        if exp_info.cls_name:
            dot = '.'
        else:
            dot = ''

        # # import inspect
        # print('exp_info.line_num:', i, ':', exp_info.line_num)
        # for j in range(5):
        #     frame = _getframe(j)
        #     print(frame.f_code.co_name, ':', frame.f_lineno)

        exp_seq = f'{exp_info.mod_name}{dbl_colon}' \
                  f'{exp_info.cls_name}{dot}{exp_info.func_name}:' \
                  f'{exp_info.line_num}{arrow}{exp_seq}'
        arrow = ' -> '

    return exp_seq


########################################################################
# verify_diag_msg is a helper function used by many test cases
########################################################################
def verify_diag_msg(exp_stack: Deque[CallerInfo],
                    before_time: datetime,
                    after_time: datetime,
                    capsys: pytest.CaptureFixture[str],
                    diag_msg_args: DiagMsgArgs) -> None:
    """Verify the captured msg is as expected.

    Args:
        exp_stack: The expected stack of callers
        before_time: The time just before issuing the diag_msg
        after_time: The time just after the diag_msg
        capsys: Pytest fixture that captures output
        diag_msg_args: Specifies the args used on the diag_msg
                         invocation

    """
    # We are about to format the before and after times to match the
    # precision of the diag_msg time. In doing so, we may end up with
    # the after time appearing to be earlier than the before time if the
    # times are very close to 23:59:59 if the format does not include
    # the date information (e.g., before_time ends up being
    # 23:59:59.999938 and after_time end up being 00:00:00.165). If this
    # happens, we can't reliably check the diag_msg time so we will
    # simply skip the check. The following assert proves only that the
    # times passed in are good to start with before we strip off any
    # resolution.
    # Note: changed the following from 'less than' to
    # 'less than or equal' because the times are apparently the
    # same on a faster machine (meaning the resolution of microseconds
    # is not enough)

    assert before_time <= after_time

    before_time = datetime.strptime(
        before_time.strftime(diag_msg_args.dt_format_arg),
        diag_msg_args.dt_format_arg)
    after_time = datetime.strptime(
        after_time.strftime(diag_msg_args.dt_format_arg),
        diag_msg_args.dt_format_arg)

    if diag_msg_args.file_arg == 'sys.stdout':
        cap_msg = capsys.readouterr().out
    else:  # must be stderr
        cap_msg = capsys.readouterr().err

    str_list = cap_msg.split()
    dt_format_split_list = diag_msg_args.dt_format_arg.split()
    msg_time_str = ''
    for i in range(len(dt_format_split_list)):
        msg_time_str = f'{msg_time_str}{str_list.pop(0)} '
    msg_time_str = msg_time_str.rstrip()
    msg_time = datetime.strptime(msg_time_str, diag_msg_args.dt_format_arg)

    # if safe to proceed with low resolution
    if before_time <= after_time:
        assert before_time <= msg_time <= after_time

    # build the expected call sequence string
    call_seq = ''
    for i in range(len(str_list)):
        word = str_list.pop(0)
        if i % 2 == 0:  # if even
            if ":" in word:  # if this is a call entry
                call_seq = f'{call_seq}{word}'
            else:  # not a call entry, must be first word of msg
                str_list.insert(0, word)  # put it back
                break  # we are done
        elif word == '->':  # odd and we have arrow
            call_seq = f'{call_seq} {word} '
        else:  # odd and no arrow (beyond call sequence)
            str_list.insert(0, word)  # put it back
            break  # we are done

    verify_call_seq(exp_stack=exp_stack,
                    call_seq=call_seq,
                    seq_depth=diag_msg_args.depth_arg)

    captured_msg = ''
    for i in range(len(str_list)):
        captured_msg = f'{captured_msg}{str_list[i]} '
    captured_msg = captured_msg.rstrip()

    check_msg = ''
    for i in range(len(diag_msg_args.msg_arg)):
        check_msg = f'{check_msg}{diag_msg_args.msg_arg[i]} '
    check_msg = check_msg.rstrip()

    assert captured_msg == check_msg


########################################################################
# verify_call_seq is a helper function used by many test cases
########################################################################
def verify_call_seq(exp_stack: Deque[CallerInfo],
                    call_seq: str,
                    seq_latest: Optional[int] = None,
                    seq_depth: Optional[int] = None) -> None:
    """Verify the captured msg is as expected.

    Args:
        exp_stack: The expected stack of callers
        call_seq: The call sequence from get_formatted_call_seq or from
                    diag_msg to check
        seq_latest: The value used for the get_formatted_call_seq latest
                      arg
        seq_depth: The value used for the get_formatted_call_seq depth
                     arg

    """
    # Note on call_seq_depth and exp_stack_depth: We need to test that
    # get_formatted_call_seq and diag_msg will correctly return the
    # entries on the real stack to the requested depth. The test cases
    # involve calling a sequence of functions so that we can grow the
    # stack with known entries and thus be able to verify them. The real
    # stack will also have entries for the system code prior to giving
    # control to the first test case. We need to be able to test the
    # depth specification on the get_formatted_call_seq and diag_msg,
    # and this may cause the call sequence to contain entries for the
    # system. The call_seq_depth is used to tell the verification code
    # to limit the check to the entries we know about and not the system
    # entries. The exp_stack_depth is also needed when we know we have
    # limited the get_formatted_call_seq or diag_msg in which case we
    # can't use the entire exp_stack.
    #
    # In the following table, the exp_stack depth is the number of
    # functions called, the get_formatted_call_seq latest and depth are
    # the values specified for the get_formatted_call_sequence latest
    # and depth args. The seq_slice latest and depth are the values to
    # use for the slice (remembering that the call_seq passed to
    # verify_call_seq may already be a slice of the real stack). Note
    # that values of 0 and None for latest and depth, respectively, mean
    # slicing in not needed. The get_exp_seq latest and depth specify
    # the slice of the exp_stack to use. Values of 0 and None here mean
    # no slicing is needed. Note also that from both seq_slice and
    # get_exp_seq, None for the depth arg means to return all of the
    # remaining entries after any latest slicing is done. Also, a
    # value of no-test means that verify_call_seq can not do a
    # verification since the call_seq is not  in the range of the
    # exp_stack.

    # gfcs = get_formatted_call_seq
    #
    # exp_stk | gfcs           | seq_slice         | get_exp_seq
    # depth   | latest | depth | start   |     end | latest  | depth
    # ------------------------------------------------------------------
    #       1 |      0       1 |       0 | None (1) |      0 | None (1)
    #       1 |      0       2 |       0 |       1  |      0 | None (1)
    #       1 |      0       3 |       0 |       1  |      0 | None (1)
    #       1 |      1       1 |            no-test |     no-test
    #       1 |      1       2 |            no-test |     no-test
    #       1 |      1       3 |            no-test |     no-test
    #       1 |      2       1 |            no-test |     no-test
    #       1 |      2       2 |            no-test |     no-test
    #       1 |      2       3 |            no-test |     no-test
    #       2 |      0       1 |       0 | None (1) |      0 |       1
    #       2 |      0       2 |       0 | None (2) |      0 | None (2)
    #       2 |      0       3 |       0 |       2  |      0 | None (2)
    #       2 |      1       1 |       0 | None (1) |      1 | None (1)
    #       2 |      1       2 |       0 |       1  |      1 | None (1)
    #       2 |      1       3 |       0 |       1  |      1 | None (1)
    #       2 |      2       1 |            no-test |     no-test
    #       2 |      2       2 |            no-test |     no-test
    #       2 |      2       3 |            no-test |     no-test
    #       3 |      0       1 |       0 | None (1) |      0 |       1
    #       3 |      0       2 |       0 | None (2) |      0 |       2
    #       3 |      0       3 |       0 | None (3) |      0 | None (3)
    #       3 |      1       1 |       0 | None (1) |      1 |       1
    #       3 |      1       2 |       0 | None (2) |      1 | None (2)
    #       3 |      1       3 |       0 |       2  |      1 | None (2)
    #       3 |      2       1 |       0 | None (1) |      2 | None (1)
    #       3 |      2       2 |       0 |       1  |      2 | None (1)
    #       3 |      2       3 |       0 |       1  |      2 | None (1)

    # The following assert checks to make sure the call_seq obtained by
    # the get_formatted_call_seq has the correct number of entries and
    # is formatted correctly with arrows by calling seq_slice with the
    # get_formatted_call_seq seq_depth. In this case, the slice returned
    # by seq_slice should be exactly the same as the input
    if seq_depth is None:
        seq_depth = get_formatted_call_seq_depth

    assert call_seq == seq_slice(call_seq=call_seq, end=seq_depth)

    if seq_latest is None:
        seq_latest = 0

    # if we have enough stack entries to test
    if seq_latest < len(exp_stack):
        if len(exp_stack) - seq_latest < seq_depth:  # if need to slice
            call_seq = seq_slice(call_seq=call_seq,
                                 end=len(exp_stack) - seq_latest)

        if len(exp_stack) <= seq_latest + seq_depth:
            assert call_seq == get_exp_seq(exp_stack=exp_stack,
                                           latest=seq_latest)
        else:
            assert call_seq == get_exp_seq(exp_stack=exp_stack,
                                           latest=seq_latest,
                                           depth=seq_depth)


########################################################################
# update stack with new line number
########################################################################
def update_stack(exp_stack: Deque[CallerInfo],
                 line_num: int,
                 add: int) -> None:
    """Update the stack line number.

    Args:
        exp_stack: The expected stack of callers
        line_num: the new line number to replace the one in the stack
        add: number to add to line_num for python version 3.6 and 3.7
    """
    caller_info = exp_stack.pop()
    if sys.version_info[0] >= 4 or sys.version_info[1] >= 8:
        caller_info = caller_info._replace(line_num=line_num)
    else:
        caller_info = caller_info._replace(line_num=line_num + add)
    exp_stack.append(caller_info)


########################################################################
# Class to test get call sequence
########################################################################
class TestCallSeq:
    """Class the test get_formatted_call_sequence."""
    ####################################################################
    # Basic test for get_formatted_call_seq
    ####################################################################
    def test_get_call_seq_basic(self) -> None:
        """Test basic get formatted call sequence function."""
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='test_get_call_seq_basic',
                                     line_num=420)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=479, add=0)
        call_seq = get_formatted_call_sequence()

        verify_call_seq(exp_stack=exp_stack, call_seq=call_seq)

    ####################################################################
    # Test with latest and depth parms with stack of 1
    ####################################################################
    def test_get_call_seq_with_parms(self,
                                     latest_arg: Optional[int] = None,
                                     depth_arg: Optional[int] = None
                                     ) -> None:
        """Test get_formatted_call_seq with parms at depth 1.

        Args:
            latest_arg: pytest fixture that specifies how far back into
                          the stack to go for the most recent entry
            depth_arg: pytest fixture that specifies how many entries to
                         get

        """
        print('sys.version_info[0]:', sys.version_info[0])
        print('sys.version_info[1]:', sys.version_info[1])
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='test_get_call_seq_with_parms',
                                     line_num=449)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=510, add=0)
        call_seq = ''
        if latest_arg is None and depth_arg is None:
            call_seq = get_formatted_call_sequence()
        elif latest_arg is None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=513, add=0)
            call_seq = get_formatted_call_sequence(depth=depth_arg)
        elif latest_arg is not None and depth_arg is None:
            update_stack(exp_stack=exp_stack, line_num=516, add=0)
            call_seq = get_formatted_call_sequence(latest=latest_arg)
        elif latest_arg is not None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=519, add=1)
            call_seq = get_formatted_call_sequence(latest=latest_arg,
                                                   depth=depth_arg)
        verify_call_seq(exp_stack=exp_stack,
                        call_seq=call_seq,
                        seq_latest=latest_arg,
                        seq_depth=depth_arg)

        update_stack(exp_stack=exp_stack, line_num=527, add=2)
        self.get_call_seq_depth_2(exp_stack=exp_stack,
                                  latest_arg=latest_arg,
                                  depth_arg=depth_arg)

    ####################################################################
    # Test with latest and depth parms with stack of 2
    ####################################################################
    def get_call_seq_depth_2(self,
                             exp_stack: Deque[CallerInfo],
                             latest_arg: Optional[int] = None,
                             depth_arg: Optional[int] = None
                             ) -> None:
        """Test get_formatted_call_seq at depth 2.

        Args:
            exp_stack: The expected stack of callers
            latest_arg: pytest fixture that specifies how far back into
                          the stack to go for the most recent entry
            depth_arg: pytest fixture that specifies how many entries to
                                get

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='get_call_seq_depth_2',
                                     line_num=494)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=557, add=0)
        call_seq = ''
        if latest_arg is None and depth_arg is None:
            call_seq = get_formatted_call_sequence()
        elif latest_arg is None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=560, add=0)
            call_seq = get_formatted_call_sequence(depth=depth_arg)
        elif latest_arg is not None and depth_arg is None:
            update_stack(exp_stack=exp_stack, line_num=563, add=0)
            call_seq = get_formatted_call_sequence(latest=latest_arg)
        elif latest_arg is not None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=566, add=1)
            call_seq = get_formatted_call_sequence(latest=latest_arg,
                                                   depth=depth_arg)
        verify_call_seq(exp_stack=exp_stack,
                        call_seq=call_seq,
                        seq_latest=latest_arg,
                        seq_depth=depth_arg)

        update_stack(exp_stack=exp_stack, line_num=574, add=2)
        self.get_call_seq_depth_3(exp_stack=exp_stack,
                                  latest_arg=latest_arg,
                                  depth_arg=depth_arg)

        exp_stack.pop()  # return with correct stack

    ####################################################################
    # Test with latest and depth parms with stack of 3
    ####################################################################
    def get_call_seq_depth_3(self,
                             exp_stack: Deque[CallerInfo],
                             latest_arg: Optional[int] = None,
                             depth_arg: Optional[int] = None
                             ) -> None:
        """Test get_formatted_call_seq at depth 3.

        Args:
            exp_stack: The expected stack of callers
            latest_arg: pytest fixture that specifies how far back into
                          the stack to go for the most recent entry
            depth_arg: pytest fixture that specifies how many entries to
                         get

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='get_call_seq_depth_3',
                                     line_num=541)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=606, add=0)
        call_seq = ''
        if latest_arg is None and depth_arg is None:
            call_seq = get_formatted_call_sequence()
        elif latest_arg is None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=609, add=0)
            call_seq = get_formatted_call_sequence(depth=depth_arg)
        elif latest_arg is not None and depth_arg is None:
            update_stack(exp_stack=exp_stack, line_num=612, add=0)
            call_seq = get_formatted_call_sequence(latest=latest_arg)
        elif latest_arg is not None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=615, add=1)
            call_seq = get_formatted_call_sequence(latest=latest_arg,
                                                   depth=depth_arg)
        verify_call_seq(exp_stack=exp_stack,
                        call_seq=call_seq,
                        seq_latest=latest_arg,
                        seq_depth=depth_arg)

        update_stack(exp_stack=exp_stack, line_num=623, add=2)
        self.get_call_seq_depth_4(exp_stack=exp_stack,
                                  latest_arg=latest_arg,
                                  depth_arg=depth_arg)

        exp_stack.pop()  # return with correct stack

    ####################################################################
    # Test with latest and depth parms with stack of 4
    ####################################################################
    def get_call_seq_depth_4(self,
                             exp_stack: Deque[CallerInfo],
                             latest_arg: Optional[int] = None,
                             depth_arg: Optional[int] = None
                             ) -> None:
        """Test get_formatted_call_seq at depth 4.

        Args:
            exp_stack: The expected stack of callers
            latest_arg: pytest fixture that specifies how far back into
                          the stack to go for the most recent entry
            depth_arg: pytest fixture that specifies how many entries to
                         get

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='get_call_seq_depth_4',
                                     line_num=588)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=655, add=0)
        call_seq = ''
        if latest_arg is None and depth_arg is None:
            call_seq = get_formatted_call_sequence()
        elif latest_arg is None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=658, add=0)
            call_seq = get_formatted_call_sequence(depth=depth_arg)
        elif latest_arg is not None and depth_arg is None:
            update_stack(exp_stack=exp_stack, line_num=661, add=0)
            call_seq = get_formatted_call_sequence(latest=latest_arg)
        elif latest_arg is not None and depth_arg is not None:
            update_stack(exp_stack=exp_stack, line_num=664, add=1)
            call_seq = get_formatted_call_sequence(latest=latest_arg,
                                                   depth=depth_arg)
        verify_call_seq(exp_stack=exp_stack,
                        call_seq=call_seq,
                        seq_latest=latest_arg,
                        seq_depth=depth_arg)

        exp_stack.pop()  # return with correct stack

    ####################################################################
    # Verify we can run off the end of the stack
    ####################################################################
    def test_get_call_seq_full_stack(self) -> None:
        """Test to ensure we can run the entire stack."""
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestCallSeq',
                                     func_name='test_get_call_seq_full_stack',
                                     line_num=620)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=688, add=1)
        num_items = 0
        new_count = 1
        while num_items + 1 == new_count:
            call_seq = get_formatted_call_sequence(latest=0,
                                                   depth=new_count)
            call_seq_list = call_seq.split()
            # The call_seq_list will have x call items and x-1 arrows,
            # so the following code will calculate the number of items
            # by adding 1 more arrow and dividing the sum by 2
            num_items = (len(call_seq_list) + 1)//2
            verify_call_seq(exp_stack=exp_stack,
                            call_seq=call_seq,
                            seq_latest=0,
                            seq_depth=num_items)
            new_count += 1

        assert new_count > 2  # make sure we tried more than 1


########################################################################
# TestDiagMsg class
########################################################################
class TestDiagMsg:
    """Class to test msg_diag."""
    DT1: Final = 0b00001000
    DEPTH1: Final = 0b00000100
    MSG1: Final = 0b00000010
    FILE1: Final = 0b00000001

    DT0_DEPTH0_MSG0_FILE0: Final = 0b00000000
    DT0_DEPTH0_MSG0_FILE1: Final = 0b00000001
    DT0_DEPTH0_MSG1_FILE0: Final = 0b00000010
    DT0_DEPTH0_MSG1_FILE1: Final = 0b00000011
    DT0_DEPTH1_MSG0_FILE0: Final = 0b00000100
    DT0_DEPTH1_MSG0_FILE1: Final = 0b00000101
    DT0_DEPTH1_MSG1_FILE0: Final = 0b00000110
    DT0_DEPTH1_MSG1_FILE1: Final = 0b00000111
    DT1_DEPTH0_MSG0_FILE0: Final = 0b00001000
    DT1_DEPTH0_MSG0_FILE1: Final = 0b00001001
    DT1_DEPTH0_MSG1_FILE0: Final = 0b00001010
    DT1_DEPTH0_MSG1_FILE1: Final = 0b00001011
    DT1_DEPTH1_MSG0_FILE0: Final = 0b00001100
    DT1_DEPTH1_MSG0_FILE1: Final = 0b00001101
    DT1_DEPTH1_MSG1_FILE0: Final = 0b00001110
    DT1_DEPTH1_MSG1_FILE1: Final = 0b00001111

    ####################################################################
    # Get the arg specifications for diag_msg
    ####################################################################
    @staticmethod
    def get_diag_msg_args(*,
                          dt_format_arg: Optional[str] = None,
                          depth_arg: Optional[int] = None,
                          msg_arg: Optional[List[Union[str, int]]] = None,
                          file_arg: Optional[str] = None
                          ) -> DiagMsgArgs:
        """Static method get_arg_flags.

        Args:
            dt_format_arg: dt_format arg to use for diag_msg
            depth_arg: depth arg to use for diag_msg
            msg_arg: message to specify on the diag_msg
            file_arg: file arg to use (stdout or stderr) on diag_msg

        Returns:
              the expected results based on the args
        """
        a_arg_bits = TestDiagMsg.DT0_DEPTH0_MSG0_FILE0

        a_dt_format_arg = diag_msg_datetime_fmt
        if dt_format_arg is not None:
            a_arg_bits = a_arg_bits | TestDiagMsg.DT1
            a_dt_format_arg = dt_format_arg

        a_depth_arg = diag_msg_caller_depth
        if depth_arg is not None:
            a_arg_bits = a_arg_bits | TestDiagMsg.DEPTH1
            a_depth_arg = depth_arg

        a_msg_arg: List[Union[str, int]] = ['']
        if msg_arg is not None:
            a_arg_bits = a_arg_bits | TestDiagMsg.MSG1
            a_msg_arg = msg_arg

        a_file_arg = 'sys.stdout'
        if file_arg is not None:
            a_arg_bits = a_arg_bits | TestDiagMsg.FILE1
            a_file_arg = file_arg

        return DiagMsgArgs(arg_bits=a_arg_bits,
                           dt_format_arg=a_dt_format_arg,
                           depth_arg=a_depth_arg,
                           msg_arg=a_msg_arg,
                           file_arg=a_file_arg)

    ####################################################################
    # Basic diag_msg test
    ####################################################################
    def test_diag_msg_basic(self,
                            capsys: pytest.CaptureFixture[str]) -> None:
        """Test various combinations of msg_diag.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestDiagMsg',
                                     func_name='test_diag_msg_basic',
                                     line_num=727)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=799, add=0)
        before_time = datetime.now()
        diag_msg()
        after_time = datetime.now()

        diag_msg_args = self.get_diag_msg_args()
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

    ####################################################################
    # diag_msg with parms
    ####################################################################
    def test_diag_msg_with_parms(self,
                                 capsys: pytest.CaptureFixture[str],
                                 dt_format_arg: str,
                                 depth_arg: int,
                                 msg_arg: List[Union[str, int]],
                                 file_arg: str) -> None:
        """Test various combinations of msg_diag.

        Args:
            capsys: pytest fixture that captures output
            dt_format_arg: pytest fixture for datetime format
            depth_arg: pytest fixture for number of call seq entries
            msg_arg: pytest fixture for messages
            file_arg: pytest fixture for different print file types

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestDiagMsg',
                                     func_name='test_diag_msg_with_parms',
                                     line_num=768)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=841, add=0)
        diag_msg_args = self.get_diag_msg_args(dt_format_arg=dt_format_arg,
                                               depth_arg=depth_arg,
                                               msg_arg=msg_arg,
                                               file_arg=file_arg)
        before_time = datetime.now()
        if diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE0:
            diag_msg()
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=844, add=0)
            diag_msg(file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=847, add=0)
            diag_msg(*diag_msg_args.msg_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=850, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=854, add=0)
            diag_msg(depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=857, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=861, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=865, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=870, add=0)
            diag_msg(dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=873, add=1)
            diag_msg(dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=877, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=881, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=886, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=890, add=2)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg),
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=895, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=900, add=3)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))

        after_time = datetime.now()

        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        update_stack(exp_stack=exp_stack, line_num=914, add=2)
        self.diag_msg_depth_2(exp_stack=exp_stack,
                              capsys=capsys,
                              diag_msg_args=diag_msg_args)

    ####################################################################
    # Depth 2 test
    ####################################################################
    def diag_msg_depth_2(self,
                         exp_stack: Deque[CallerInfo],
                         capsys: pytest.CaptureFixture[str],
                         diag_msg_args: DiagMsgArgs) -> None:
        """Test msg_diag with two callers in the sequence.

        Args:
            exp_stack: The expected stack as modified by each test case
            capsys: pytest fixture that captures output
            diag_msg_args: Specifies the args to use on the diag_msg
                             invocation

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestDiagMsg',
                                     func_name='diag_msg_depth_2',
                                     line_num=867)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=942, add=0)
        before_time = datetime.now()
        if diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE0:
            diag_msg()
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=945, add=0)
            diag_msg(file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=948, add=0)
            diag_msg(*diag_msg_args.msg_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=951, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=955, add=0)
            diag_msg(depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=958, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=962, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=966, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=971, add=0)
            diag_msg(dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=974, add=1)
            diag_msg(dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=978, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=982, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=987, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=991, add=2)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg),
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=996, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1001, add=3)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))

        after_time = datetime.now()

        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        update_stack(exp_stack=exp_stack, line_num=1015, add=2)
        self.diag_msg_depth_3(exp_stack=exp_stack,
                              capsys=capsys,
                              diag_msg_args=diag_msg_args)

        exp_stack.pop()  # return with correct stack

    ####################################################################
    # Depth 3 test
    ####################################################################
    def diag_msg_depth_3(self,
                         exp_stack: Deque[CallerInfo],
                         capsys: pytest.CaptureFixture[str],
                         diag_msg_args: DiagMsgArgs) -> None:
        """Test msg_diag with three callers in the sequence.

        Args:
            exp_stack: The expected stack as modified by each test case
            capsys: pytest fixture that captures output
            diag_msg_args: Specifies the args to use on the diag_msg
                             invocation

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestDiagMsg',
                                     func_name='diag_msg_depth_3',
                                     line_num=968)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=1045, add=0)
        before_time = datetime.now()
        if diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE0:
            diag_msg()
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1048, add=0)
            diag_msg(file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1051, add=0)
            diag_msg(*diag_msg_args.msg_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1054, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1058, add=0)
            diag_msg(depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1061, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1065, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT0_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1069, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1074, add=0)
            diag_msg(dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1077, add=1)
            diag_msg(dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1081, add=1)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH0_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1085, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1090, add=1)
            diag_msg(depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG0_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1094, add=2)
            diag_msg(depth=diag_msg_args.depth_arg,
                     file=eval(diag_msg_args.file_arg),
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE0:
            update_stack(exp_stack=exp_stack, line_num=1099, add=2)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg)
        elif diag_msg_args.arg_bits == TestDiagMsg.DT1_DEPTH1_MSG1_FILE1:
            update_stack(exp_stack=exp_stack, line_num=1104, add=3)
            diag_msg(*diag_msg_args.msg_arg,
                     depth=diag_msg_args.depth_arg,
                     dt_format=diag_msg_args.dt_format_arg,
                     file=eval(diag_msg_args.file_arg))

        after_time = datetime.now()

        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        exp_stack.pop()  # return with correct stack


########################################################################
# The functions and classes below handle various combinations of cases
# where one function calls another up to a level of 5 functions deep.
# The first caller can be at the module level (i.e., script level), or a
# module function, class method, static method, or class method. The
# second and subsequent callers can be any but the module level caller.
# The following grouping shows the possibilities:
# {mod, func, method, static_method, cls_method}
#       -> {func, method, static_method, cls_method}
#
########################################################################
# func 0
########################################################################
def test_func_get_caller_info_0(capsys: pytest.CaptureFixture[str]) -> None:
    """Module level function 0 to test get_caller_info.

    Args:
        capsys: Pytest fixture that captures output
    """
    exp_stack: Deque[CallerInfo] = deque()
    exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                 cls_name='',
                                 func_name='test_func_get_caller_info_0',
                                 line_num=1071)
    exp_stack.append(exp_caller_info)
    update_stack(exp_stack=exp_stack, line_num=1149, add=0)
    for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
        try:
            frame = _getframe(i)
            caller_info = get_caller_info(frame)
        finally:
            del frame
        assert caller_info == expected_caller_info

    # test call sequence
    update_stack(exp_stack=exp_stack, line_num=1156, add=0)
    call_seq = get_formatted_call_sequence(depth=1)

    assert call_seq == get_exp_seq(exp_stack=exp_stack)

    # test diag_msg
    update_stack(exp_stack=exp_stack, line_num=1163, add=0)
    before_time = datetime.now()
    diag_msg('message 0', 0, depth=1)
    after_time = datetime.now()

    diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                  msg_arg=['message 0', 0])
    verify_diag_msg(exp_stack=exp_stack,
                    before_time=before_time,
                    after_time=after_time,
                    capsys=capsys,
                    diag_msg_args=diag_msg_args)

    # call module level function
    update_stack(exp_stack=exp_stack, line_num=1176, add=0)
    func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

    # call method
    cls_get_caller_info1 = ClassGetCallerInfo1()
    update_stack(exp_stack=exp_stack, line_num=1181, add=0)
    cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack, capsys=capsys)

    # call static method
    update_stack(exp_stack=exp_stack, line_num=1185, add=0)
    cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack, capsys=capsys)

    # call class method
    update_stack(exp_stack=exp_stack, line_num=1189, add=0)
    ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack, capsys=capsys)

    # call overloaded base class method
    update_stack(exp_stack=exp_stack, line_num=1193, add=1)
    cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class static method
    update_stack(exp_stack=exp_stack, line_num=1198, add=1)
    cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class class method
    update_stack(exp_stack=exp_stack, line_num=1203, add=1)
    ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                             capsys=capsys)

    # call subclass method
    cls_get_caller_info1s = ClassGetCallerInfo1S()
    update_stack(exp_stack=exp_stack, line_num=1209, add=1)
    cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass static method
    update_stack(exp_stack=exp_stack, line_num=1214, add=1)
    cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass class method
    update_stack(exp_stack=exp_stack, line_num=1219, add=1)
    ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                             capsys=capsys)

    # call overloaded subclass method
    update_stack(exp_stack=exp_stack, line_num=1224, add=1)
    cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass static method
    update_stack(exp_stack=exp_stack, line_num=1229, add=1)
    cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass class method
    update_stack(exp_stack=exp_stack, line_num=1234, add=1)
    ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call base method from subclass method
    update_stack(exp_stack=exp_stack, line_num=1239, add=1)
    cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base static method from subclass static method
    update_stack(exp_stack=exp_stack, line_num=1244, add=1)
    cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base class method from subclass class method
    update_stack(exp_stack=exp_stack, line_num=1249, add=1)
    ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                              capsys=capsys)

    ####################################################################
    # Inner class defined inside function test_func_get_caller_info_0
    ####################################################################
    class Inner:
        """Inner class for testing with inner class."""

        def __init__(self) -> None:
            """Initialize Inner class object."""
            self.var2 = 2

        def g1(self,
               exp_stack_g: Deque[CallerInfo],
               capsys_g: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g1',
                                           line_num=1197)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=1282, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=1289, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=1297, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=1311, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_g, line_num=1316, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=1321, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=1326, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=1331, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=1336, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=1341, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_g, line_num=1347, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1352, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1357, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1362, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1367, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1372, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1377, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1382, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1387, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

        @staticmethod
        def g2_static(exp_stack_g: Deque[CallerInfo],
                      capsys_g: Optional[Any]) -> None:
            """Inner static method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g2_static',
                                           line_num=1197)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=1412, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=1419, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=1427, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=1441, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_g, line_num=1446, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=1451, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=1456, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=1461, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=1466, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=1471, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_g, line_num=1477, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1482, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1487, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1492, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1497, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1502, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1507, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1512, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1517, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

        @classmethod
        def g3_class(cls,
                     exp_stack_g: Deque[CallerInfo],
                     capsys_g: Optional[Any]) -> None:
            """Inner class method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g3_class',
                                           line_num=1197)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=1543, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=1550, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=1558, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=1572, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_g, line_num=1577, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=1582, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=1587, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=1592, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=1597, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=1602, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_g, line_num=1608, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1613, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1618, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1623, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1628, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1633, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=1638, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=1643, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=1648, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

    class Inherit(Inner):
        """Inherit class for testing inner class."""

        def __init__(self) -> None:
            """Initialize Inherit object."""
            super().__init__()
            self.var3 = 3

        def h1(self,
               exp_stack_h: Deque[CallerInfo],
               capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h1',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=1681, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=1688, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=1696, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=1710, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_h, line_num=1715, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=1720, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=1725, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=1730, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=1735, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=1740, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_h, line_num=1746, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1751, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1756, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=1761, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1766, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1771, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=1776, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1781, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1786, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

        @staticmethod
        def h2_static(exp_stack_h: Deque[CallerInfo],
                      capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h2_static',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=1811, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=1818, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=1826, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=1840, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_h, line_num=1845, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=1850, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=1855, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=1860, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=1865, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=1870, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_h, line_num=1876, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1881, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1886, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=1891, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1896, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1901, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=1906, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=1911, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=1916, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

        @classmethod
        def h3_class(cls,
                     exp_stack_h: Deque[CallerInfo],
                     capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h3_class',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=1942, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=1949, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=1957, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=1971, add=0)
            func_get_caller_info_1(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info1 = ClassGetCallerInfo1()
            update_stack(exp_stack=exp_stack_h, line_num=1976, add=1)
            cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=1981, add=1)
            cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=1986, add=1)
            ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=1991, add=1)
            cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=1996, add=1)
            cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=2001, add=1)
            ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info1s = ClassGetCallerInfo1S()
            update_stack(exp_stack=exp_stack_h, line_num=2007, add=1)
            cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2012, add=1)
            cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2017, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2022, add=1)
            cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2027, add=1)
            cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2032, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2037, add=1)
            cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2042, add=1)
            cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2047, add=1)
            ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

    a_inner = Inner()
    # call Inner method
    update_stack(exp_stack=exp_stack, line_num=2055, add=0)
    a_inner.g1(exp_stack_g=exp_stack, capsys_g=capsys)

    update_stack(exp_stack=exp_stack, line_num=2058, add=0)
    a_inner.g2_static(exp_stack_g=exp_stack, capsys_g=capsys)

    update_stack(exp_stack=exp_stack, line_num=2061, add=0)
    a_inner.g3_class(exp_stack_g=exp_stack, capsys_g=capsys)

    a_inherit = Inherit()

    update_stack(exp_stack=exp_stack, line_num=2066, add=0)
    a_inherit.h1(exp_stack_h=exp_stack, capsys_h=capsys)

    update_stack(exp_stack=exp_stack, line_num=2069, add=0)
    a_inherit.h2_static(exp_stack_h=exp_stack, capsys_h=capsys)

    update_stack(exp_stack=exp_stack, line_num=2072, add=0)
    a_inherit.h3_class(exp_stack_h=exp_stack, capsys_h=capsys)

    exp_stack.pop()


########################################################################
# func 1
########################################################################
def func_get_caller_info_1(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
    """Module level function 1 to test get_caller_info.

    Args:
        exp_stack: The expected call stack
        capsys: Pytest fixture that captures output

    """
    exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                 cls_name='',
                                 func_name='func_get_caller_info_1',
                                 line_num=1197)
    exp_stack.append(exp_caller_info)
    update_stack(exp_stack=exp_stack, line_num=2098, add=0)
    for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
        try:
            frame = _getframe(i)
            caller_info = get_caller_info(frame)
        finally:
            del frame
        assert caller_info == expected_caller_info

    # test call sequence
    update_stack(exp_stack=exp_stack, line_num=2105, add=0)
    call_seq = get_formatted_call_sequence(depth=len(exp_stack))

    assert call_seq == get_exp_seq(exp_stack=exp_stack)

    # test diag_msg
    if capsys:  # if capsys, test diag_msg
        update_stack(exp_stack=exp_stack, line_num=2113, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

    # call module level function
    update_stack(exp_stack=exp_stack, line_num=2126, add=0)
    func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

    # call method
    cls_get_caller_info2 = ClassGetCallerInfo2()
    update_stack(exp_stack=exp_stack, line_num=2131, add=0)
    cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack, capsys=capsys)

    # call static method
    update_stack(exp_stack=exp_stack, line_num=2135, add=0)
    cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack, capsys=capsys)

    # call class method
    update_stack(exp_stack=exp_stack, line_num=2139, add=0)
    ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack, capsys=capsys)

    # call overloaded base class method
    update_stack(exp_stack=exp_stack, line_num=2143, add=1)
    cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class static method
    update_stack(exp_stack=exp_stack, line_num=2148, add=1)
    cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class class method
    update_stack(exp_stack=exp_stack, line_num=2153, add=1)
    ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                             capsys=capsys)

    # call subclass method
    cls_get_caller_info2s = ClassGetCallerInfo2S()
    update_stack(exp_stack=exp_stack, line_num=2159, add=1)
    cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass static method
    update_stack(exp_stack=exp_stack, line_num=2164, add=1)
    cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass class method
    update_stack(exp_stack=exp_stack, line_num=2169, add=1)
    ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                             capsys=capsys)

    # call overloaded subclass method
    update_stack(exp_stack=exp_stack, line_num=2174, add=1)
    cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass static method
    update_stack(exp_stack=exp_stack, line_num=2179, add=1)
    cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass class method
    update_stack(exp_stack=exp_stack, line_num=2184, add=1)
    ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call base method from subclass method
    update_stack(exp_stack=exp_stack, line_num=2189, add=1)
    cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base static method from subclass static method
    update_stack(exp_stack=exp_stack, line_num=2194, add=1)
    cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base class method from subclass class method
    update_stack(exp_stack=exp_stack, line_num=2199, add=1)
    ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                              capsys=capsys)

    ####################################################################
    # Inner class defined inside function test_func_get_caller_info_0
    ####################################################################
    class Inner:
        """Inner class for testing with inner class."""
        def __init__(self) -> None:
            """Initialize Inner class object."""
            self.var2 = 2

        def g1(self,
               exp_stack_g: Deque[CallerInfo],
               capsys_g: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g1',
                                           line_num=1197)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=2231, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=2238, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=2246, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=2260, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_g, line_num=2265, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=2270, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=2275, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=2280, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=2285, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=2290, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_g, line_num=2296, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2301, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2306, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2311, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2316, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2321, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2326, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2331, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2336, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

        @staticmethod
        def g2_static(exp_stack_g: Deque[CallerInfo],
                      capsys_g: Optional[Any]) -> None:
            """Inner static method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g2_static',
                                           line_num=2297)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=2361, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=2368, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=2376, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=2390, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_g, line_num=2395, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=2400, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=2405, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=2410, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=2415, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=2420, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_g, line_num=2426, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2431, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2436, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2441, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2446, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2451, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2456, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2461, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2466, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

        @classmethod
        def g3_class(cls,
                     exp_stack_g: Deque[CallerInfo],
                     capsys_g: Optional[Any]) -> None:
            """Inner class method to test diag msg.

            Args:
                exp_stack_g: The expected call stack
                capsys_g: Pytest fixture that captures output

            """
            exp_caller_info_g = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inner',
                                           func_name='g3_class',
                                           line_num=2197)
            exp_stack_g.append(exp_caller_info_g)
            update_stack(exp_stack=exp_stack_g, line_num=2492, add=0)
            for i_g, expected_caller_info_g in enumerate(
                    list(reversed(exp_stack_g))):
                try:
                    frame_g = _getframe(i_g)
                    caller_info_g = get_caller_info(frame_g)
                finally:
                    del frame_g
                assert caller_info_g == expected_caller_info_g

            # test call sequence
            update_stack(exp_stack=exp_stack_g, line_num=2499, add=0)
            call_seq_g = get_formatted_call_sequence(depth=len(exp_stack_g))

            assert call_seq_g == get_exp_seq(exp_stack=exp_stack_g)

            # test diag_msg
            if capsys_g:  # if capsys_g, test diag_msg
                update_stack(exp_stack=exp_stack_g, line_num=2507, add=0)
                before_time_g = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_g))
                after_time_g = datetime.now()

                diag_msg_args_g = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_g),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_g,
                                before_time=before_time_g,
                                after_time=after_time_g,
                                capsys=capsys_g,
                                diag_msg_args=diag_msg_args_g)

            # call module level function
            update_stack(exp_stack=exp_stack_g, line_num=2521, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_g, capsys=capsys_g)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_g, line_num=2526, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call static method
            update_stack(exp_stack=exp_stack_g, line_num=2531, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_g,
                                                    capsys=capsys_g)

            # call class method
            update_stack(exp_stack=exp_stack_g, line_num=2536, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_g,
                                                   capsys=capsys_g)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_g, line_num=2541, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_g, line_num=2546, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_g, line_num=2551, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_g, line_num=2557, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2562, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2567, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_g,
                                                     capsys=capsys_g)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2572, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2577, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2582, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_g, line_num=2587, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_g, line_num=2592, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_g,
                                                       capsys=capsys_g)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_g, line_num=2597, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_g,
                                                      capsys=capsys_g)

            exp_stack.pop()

    class Inherit(Inner):
        """Inherit class for testing inner class."""
        def __init__(self) -> None:
            """Initialize Inherit object."""
            super().__init__()
            self.var3 = 3

        def h1(self,
               exp_stack_h: Deque[CallerInfo],
               capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h1',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=2629, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=2636, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=2644, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=2658, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_h, line_num=2663, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=2668, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=2673, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=2678, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=2683, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=2688, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_h, line_num=2694, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2699, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2704, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2709, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2714, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2719, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2724, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2729, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2734, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

        @staticmethod
        def h2_static(exp_stack_h: Deque[CallerInfo],
                      capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h2_static',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=2759, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=2766, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=2774, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=2788, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_h, line_num=2793, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=2798, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=2803, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=2808, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=2813, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=2818, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_h, line_num=2824, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2829, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2834, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2839, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2844, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2849, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2854, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2859, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2864, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

        @classmethod
        def h3_class(cls,
                     exp_stack_h: Deque[CallerInfo],
                     capsys_h: Optional[Any]) -> None:
            """Inner method to test diag msg.

            Args:
                exp_stack_h: The expected call stack
                capsys_h: Pytest fixture that captures output

            """
            exp_caller_info_h = CallerInfo(mod_name='test_diag_msg.py',
                                           cls_name='Inherit',
                                           func_name='h3_class',
                                           line_num=1197)
            exp_stack_h.append(exp_caller_info_h)
            update_stack(exp_stack=exp_stack_h, line_num=2890, add=0)
            for i_h, expected_caller_info_h in enumerate(
                    list(reversed(exp_stack_h))):
                try:
                    frame_h = _getframe(i_h)
                    caller_info_h = get_caller_info(frame_h)
                finally:
                    del frame_h
                assert caller_info_h == expected_caller_info_h

            # test call sequence
            update_stack(exp_stack=exp_stack_h, line_num=2897, add=0)
            call_seq_h = get_formatted_call_sequence(depth=len(exp_stack_h))

            assert call_seq_h == get_exp_seq(exp_stack=exp_stack_h)

            # test diag_msg
            if capsys_h:  # if capsys_h, test diag_msg
                update_stack(exp_stack=exp_stack_h, line_num=2905, add=0)
                before_time_h = datetime.now()
                diag_msg('message 1', 1, depth=len(exp_stack_h))
                after_time_h = datetime.now()

                diag_msg_args_h = TestDiagMsg.get_diag_msg_args(
                    depth_arg=len(exp_stack_h),
                    msg_arg=['message 1', 1])
                verify_diag_msg(exp_stack=exp_stack_h,
                                before_time=before_time_h,
                                after_time=after_time_h,
                                capsys=capsys_h,
                                diag_msg_args=diag_msg_args_h)

            # call module level function
            update_stack(exp_stack=exp_stack_h, line_num=2919, add=0)
            func_get_caller_info_2(exp_stack=exp_stack_h, capsys=capsys_h)

            # call method
            cls_get_caller_info2 = ClassGetCallerInfo2()
            update_stack(exp_stack=exp_stack_h, line_num=2924, add=1)
            cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call static method
            update_stack(exp_stack=exp_stack_h, line_num=2929, add=1)
            cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack_h,
                                                    capsys=capsys_h)

            # call class method
            update_stack(exp_stack=exp_stack_h, line_num=2934, add=1)
            ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack_h,
                                                   capsys=capsys_h)

            # call overloaded base class method
            update_stack(exp_stack=exp_stack_h, line_num=2939, add=1)
            cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class static method
            update_stack(exp_stack=exp_stack_h, line_num=2944, add=1)
            cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call overloaded base class class method
            update_stack(exp_stack=exp_stack_h, line_num=2949, add=1)
            ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call subclass method
            cls_get_caller_info2s = ClassGetCallerInfo2S()
            update_stack(exp_stack=exp_stack_h, line_num=2955, add=1)
            cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2960, add=1)
            cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2965, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack_h,
                                                     capsys=capsys_h)

            # call overloaded subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2970, add=1)
            cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2975, add=1)
            cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call overloaded subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2980, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            # call base method from subclass method
            update_stack(exp_stack=exp_stack_h, line_num=2985, add=1)
            cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base static method from subclass static method
            update_stack(exp_stack=exp_stack_h, line_num=2990, add=1)
            cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack_h,
                                                       capsys=capsys_h)

            # call base class method from subclass class method
            update_stack(exp_stack=exp_stack_h, line_num=2995, add=1)
            ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack_h,
                                                      capsys=capsys_h)

            exp_stack.pop()

    a_inner = Inner()
    # call Inner method
    update_stack(exp_stack=exp_stack, line_num=3003, add=0)
    a_inner.g1(exp_stack_g=exp_stack, capsys_g=capsys)

    update_stack(exp_stack=exp_stack, line_num=3006, add=0)
    a_inner.g2_static(exp_stack_g=exp_stack, capsys_g=capsys)

    update_stack(exp_stack=exp_stack, line_num=3009, add=0)
    a_inner.g3_class(exp_stack_g=exp_stack, capsys_g=capsys)

    a_inherit = Inherit()

    update_stack(exp_stack=exp_stack, line_num=3014, add=0)
    a_inherit.h1(exp_stack_h=exp_stack, capsys_h=capsys)

    update_stack(exp_stack=exp_stack, line_num=3017, add=0)
    a_inherit.h2_static(exp_stack_h=exp_stack, capsys_h=capsys)

    update_stack(exp_stack=exp_stack, line_num=3020, add=0)
    a_inherit.h3_class(exp_stack_h=exp_stack, capsys_h=capsys)

    exp_stack.pop()


########################################################################
# func 2
########################################################################
def func_get_caller_info_2(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
    """Module level function 1 to test get_caller_info.

    Args:
        exp_stack: The expected call stack
        capsys: Pytest fixture that captures output

    """
    exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                 cls_name='',
                                 func_name='func_get_caller_info_2',
                                 line_num=1324)
    exp_stack.append(exp_caller_info)
    update_stack(exp_stack=exp_stack, line_num=3046, add=0)
    for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
        try:
            frame = _getframe(i)
            caller_info = get_caller_info(frame)
        finally:
            del frame
        assert caller_info == expected_caller_info

    # test call sequence
    update_stack(exp_stack=exp_stack, line_num=3053, add=0)
    call_seq = get_formatted_call_sequence(depth=len(exp_stack))

    assert call_seq == get_exp_seq(exp_stack=exp_stack)

    # test diag_msg
    if capsys:  # if capsys, test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3061, add=0)
        before_time = datetime.now()
        diag_msg('message 2', 2, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 2', 2])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

    # call module level function
    update_stack(exp_stack=exp_stack, line_num=3074, add=0)
    func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

    # call method
    cls_get_caller_info3 = ClassGetCallerInfo3()
    update_stack(exp_stack=exp_stack, line_num=3079, add=0)
    cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack, capsys=capsys)

    # call static method
    update_stack(exp_stack=exp_stack, line_num=3083, add=0)
    cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack, capsys=capsys)

    # call class method
    update_stack(exp_stack=exp_stack, line_num=3087, add=0)
    ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack, capsys=capsys)

    # call overloaded base class method
    update_stack(exp_stack=exp_stack, line_num=3091, add=1)
    cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class static method
    update_stack(exp_stack=exp_stack, line_num=3096, add=1)
    cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call overloaded base class class method
    update_stack(exp_stack=exp_stack, line_num=3101, add=1)
    ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                             capsys=capsys)

    # call subclass method
    cls_get_caller_info3s = ClassGetCallerInfo3S()
    update_stack(exp_stack=exp_stack, line_num=3107, add=1)
    cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass static method
    update_stack(exp_stack=exp_stack, line_num=3112, add=1)
    cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                              capsys=capsys)

    # call subclass class method
    update_stack(exp_stack=exp_stack, line_num=3117, add=1)
    ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                             capsys=capsys)

    # call overloaded subclass method
    update_stack(exp_stack=exp_stack, line_num=3122, add=1)
    cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass static method
    update_stack(exp_stack=exp_stack, line_num=3127, add=1)
    cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                               capsys=capsys)

    # call overloaded subclass class method
    update_stack(exp_stack=exp_stack, line_num=3132, add=1)
    ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                              capsys=capsys)

    # call base method from subclass method
    update_stack(exp_stack=exp_stack, line_num=3137, add=1)
    cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base static method from subclass static method
    update_stack(exp_stack=exp_stack, line_num=3142, add=1)
    cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                               capsys=capsys)

    # call base class method from subclass class method
    update_stack(exp_stack=exp_stack, line_num=3147, add=1)
    ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                              capsys=capsys)

    exp_stack.pop()


########################################################################
# func 3
########################################################################
def func_get_caller_info_3(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
    """Module level function 1 to test get_caller_info.

    Args:
        exp_stack: The expected call stack
        capsys: Pytest fixture that captures output

    """
    exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                 cls_name='',
                                 func_name='func_get_caller_info_3',
                                 line_num=1451)
    exp_stack.append(exp_caller_info)
    update_stack(exp_stack=exp_stack, line_num=3174, add=0)
    for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
        try:
            frame = _getframe(i)
            caller_info = get_caller_info(frame)
        finally:
            del frame
        assert caller_info == expected_caller_info

    # test call sequence
    update_stack(exp_stack=exp_stack, line_num=3181, add=0)
    call_seq = get_formatted_call_sequence(depth=len(exp_stack))

    assert call_seq == get_exp_seq(exp_stack=exp_stack)

    # test diag_msg
    if capsys:  # if capsys, test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3189, add=0)
        before_time = datetime.now()
        diag_msg('message 2', 2, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 2', 2])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

    exp_stack.pop()


########################################################################
# Classes
########################################################################
########################################################################
# Class 0
########################################################################
class TestClassGetCallerInfo0:
    """Class to get caller info 0."""

    ####################################################################
    # Class 0 Method 1
    ####################################################################
    def test_get_caller_info_m0(self,
                                capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info method 1.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_m0',
                                     line_num=1509)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3233, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3240, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3247, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3260, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3265, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3270, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3275, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3280, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3285, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3290, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3296, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3301, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3306, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3311, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3316, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3321, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=3326, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=3331, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=3336, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 2
    ####################################################################
    def test_get_caller_info_helper(self,
                                    capsys: pytest.CaptureFixture[str]
                                    ) -> None:
        """Get capsys for static methods.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_helper',
                                     line_num=1635)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3360, add=0)
        self.get_caller_info_s0(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=3362, add=1)
        TestClassGetCallerInfo0.get_caller_info_s0(exp_stack=exp_stack,
                                                   capsys=capsys)

        update_stack(exp_stack=exp_stack, line_num=3366, add=0)
        self.get_caller_info_s0bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=3368, add=1)
        TestClassGetCallerInfo0.get_caller_info_s0bt(exp_stack=exp_stack,
                                                     capsys=capsys)

    @staticmethod
    def get_caller_info_s0(exp_stack: Deque[CallerInfo],
                           capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info static method 0.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='get_caller_info_s0',
                                     line_num=1664)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3390, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3397, add=0)
        call_seq = get_formatted_call_sequence(depth=2)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3404, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=2)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=2,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3417, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3422, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3427, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3432, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3437, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3442, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3447, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3453, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3458, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3463, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3468, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3473, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3478, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=3483, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=3488, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=3493, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 3
    ####################################################################
    @classmethod
    def test_get_caller_info_c0(cls,
                                capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info class method 0.

        Args:
            capsys: Pytest fixture that captures output
        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_c0',
                                     line_num=1792)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3519, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3526, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3533, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3546, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3551, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3556, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3561, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3566, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3571, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3576, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3582, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3587, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3592, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3597, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3602, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3607, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=3612, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=3617, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=3622, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 4
    ####################################################################
    def test_get_caller_info_m0bo(self,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_m0bo',
                                     line_num=1920)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3648, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3655, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3662, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3675, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3680, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3685, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3690, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3695, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3700, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3705, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3711, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3716, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3721, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3726, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3731, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3736, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=3741, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=3746, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=3751, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 5
    ####################################################################
    @staticmethod
    def test_get_caller_info_s0bo(capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded static method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_s0bo',
                                     line_num=2048)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3777, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3784, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3791, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3804, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3809, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3814, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3819, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3824, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3829, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3834, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3840, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3845, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3850, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3855, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3860, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3865, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=3870, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=3875, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=3880, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 6
    ####################################################################
    @classmethod
    def test_get_caller_info_c0bo(cls,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded class method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_c0bo',
                                     line_num=2177)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=3907, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=3914, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=3921, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=3934, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=3939, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=3944, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=3949, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=3954, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=3959, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=3964, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=3970, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=3975, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=3980, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=3985, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=3990, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=3995, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4000, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4005, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4010, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 7
    ####################################################################
    def test_get_caller_info_m0bt(self,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_m0bt',
                                     line_num=2305)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4036, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4043, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4050, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4063, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4068, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4073, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4078, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4083, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4088, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4093, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4099, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4104, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4109, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4114, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4119, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4124, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4129, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4134, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4139, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s0bt(exp_stack: Deque[CallerInfo],
                             capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded static method 0.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='get_caller_info_s0bt',
                                     line_num=2434)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4166, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4173, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4180, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4193, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4198, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4203, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4208, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4213, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4218, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4223, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4229, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4234, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4239, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4244, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4249, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4254, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4259, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4264, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4269, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0 Method 9
    ####################################################################
    @classmethod
    def test_get_caller_info_c0bt(cls,
                                  exp_stack: Optional[Deque[CallerInfo]],
                                  capsys: pytest.CaptureFixture[str]
                                  ) -> None:
        """Get caller info overloaded class method 0.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        if not exp_stack:
            exp_stack = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0',
                                     func_name='test_get_caller_info_c0bt',
                                     line_num=2567)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4300, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4307, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4314, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=len(exp_stack))
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=len(exp_stack),
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4327, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4332, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4337, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4342, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4347, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4352, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4357, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4363, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4368, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4373, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4378, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4383, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4388, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4393, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4398, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4403, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 0S
########################################################################
class TestClassGetCallerInfo0S(TestClassGetCallerInfo0):
    """Subclass to get caller info0."""

    ####################################################################
    # Class 0S Method 1
    ####################################################################
    def test_get_caller_info_m0s(self,
                                 capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info method 0.

        Args:
            capsys: Pytest fixture that captures output
        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_m0s',
                                     line_num=2701)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4435, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4442, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4449, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4462, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4467, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4472, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4477, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4482, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4487, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4492, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4498, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4503, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4508, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4513, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4518, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4523, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4528, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4533, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4538, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 2
    ####################################################################
    @staticmethod
    def test_get_caller_info_s0s(capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info static method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_s0s',
                                     line_num=2829)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4564, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4571, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4578, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4591, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4596, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4601, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4606, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4611, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4616, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4621, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4627, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4632, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4637, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4642, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4647, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4652, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4657, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4662, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4667, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 3
    ####################################################################
    @classmethod
    def test_get_caller_info_c0s(cls,
                                 capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info class method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_c0s',
                                     line_num=2958)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4694, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4701, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4708, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4721, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4726, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4731, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4736, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4741, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4746, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4751, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4757, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4762, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4767, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4772, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4777, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4782, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4787, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4792, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4797, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 4
    ####################################################################
    def test_get_caller_info_m0bo(self,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_m0bo',
                                     line_num=3086)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4823, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4830, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4837, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4850, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4855, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4860, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4865, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4870, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=4875, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=4880, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=4886, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=4891, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=4896, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=4901, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=4906, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=4911, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=4916, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=4921, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=4926, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 5
    ####################################################################
    @staticmethod
    def test_get_caller_info_s0bo(capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded static method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_s0bo',
                                     line_num=3214)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=4952, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=4959, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=4966, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=4979, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=4984, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=4989, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=4994, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=4999, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5004, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5009, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=5015, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5020, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5025, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5030, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5035, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5040, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5045, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5050, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5055, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 6
    ####################################################################
    @classmethod
    def test_get_caller_info_c0bo(cls,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded class method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_c0bo',
                                     line_num=3343)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5082, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5089, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=5096, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5109, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=5114, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5119, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5124, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5129, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5134, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5139, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=5145, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5150, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5155, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5160, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5165, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5170, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5175, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5180, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5185, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 7
    ####################################################################
    def test_get_caller_info_m0sb(self,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_m0sb',
                                     line_num=3471)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5211, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5218, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=5225, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call base class normal method target
        update_stack(exp_stack=exp_stack, line_num=5238, add=0)
        self.test_get_caller_info_m0bt(capsys=capsys)
        tst_cls_get_caller_info0 = TestClassGetCallerInfo0()
        update_stack(exp_stack=exp_stack, line_num=5241, add=0)
        tst_cls_get_caller_info0.test_get_caller_info_m0bt(capsys=capsys)
        tst_cls_get_caller_info0s = TestClassGetCallerInfo0S()
        update_stack(exp_stack=exp_stack, line_num=5244, add=0)
        tst_cls_get_caller_info0s.test_get_caller_info_m0bt(capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=5248, add=0)
        self.get_caller_info_s0bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5250, add=0)
        super().get_caller_info_s0bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5252, add=1)
        TestClassGetCallerInfo0.get_caller_info_s0bt(exp_stack=exp_stack,
                                                     capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5255, add=1)
        TestClassGetCallerInfo0S.get_caller_info_s0bt(exp_stack=exp_stack,
                                                      capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=5260, add=0)
        super().test_get_caller_info_c0bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5262, add=1)
        TestClassGetCallerInfo0.test_get_caller_info_c0bt(exp_stack=exp_stack,
                                                          capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5265, add=1)
        TestClassGetCallerInfo0S.test_get_caller_info_c0bt(exp_stack=exp_stack,
                                                           capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5270, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=5275, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5280, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5285, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5290, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5295, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5300, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=5306, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5311, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5316, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5321, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5326, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5331, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5336, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5341, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5346, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 8
    ####################################################################
    @staticmethod
    def test_get_caller_info_s0sb(capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded static method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_s0sb',
                                     line_num=3631)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5372, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5379, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=5386, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call base class normal method target
        tst_cls_get_caller_info0 = TestClassGetCallerInfo0()
        update_stack(exp_stack=exp_stack, line_num=5400, add=0)
        tst_cls_get_caller_info0.test_get_caller_info_m0bt(capsys=capsys)
        tst_cls_get_caller_info0s = TestClassGetCallerInfo0S()
        update_stack(exp_stack=exp_stack, line_num=5403, add=0)
        tst_cls_get_caller_info0s.test_get_caller_info_m0bt(capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=5407, add=1)
        TestClassGetCallerInfo0.get_caller_info_s0bt(exp_stack=exp_stack,
                                                     capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5410, add=1)
        TestClassGetCallerInfo0S.get_caller_info_s0bt(exp_stack=exp_stack,
                                                      capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=5415, add=1)
        TestClassGetCallerInfo0.test_get_caller_info_c0bt(exp_stack=exp_stack,
                                                          capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5418, add=1)
        TestClassGetCallerInfo0S.test_get_caller_info_c0bt(exp_stack=exp_stack,
                                                           capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5423, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=5428, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5433, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5438, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5443, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5448, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5453, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=5459, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5464, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5469, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5474, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5479, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5484, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5489, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5494, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5499, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 0S Method 9
    ####################################################################
    @classmethod
    def test_get_caller_info_c0sb(cls,
                                  capsys: pytest.CaptureFixture[str]) -> None:
        """Get caller info overloaded class method 0.

        Args:
            capsys: Pytest fixture that captures output

        """
        exp_stack: Deque[CallerInfo] = deque()
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='TestClassGetCallerInfo0S',
                                     func_name='test_get_caller_info_c0sb',
                                     line_num=3784)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5526, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5533, add=0)
        call_seq = get_formatted_call_sequence(depth=1)

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        # test diag_msg
        update_stack(exp_stack=exp_stack, line_num=5540, add=0)
        before_time = datetime.now()
        diag_msg('message 1', 1, depth=1)
        after_time = datetime.now()

        diag_msg_args = TestDiagMsg.get_diag_msg_args(depth_arg=1,
                                                      msg_arg=['message 1', 1])
        verify_diag_msg(exp_stack=exp_stack,
                        before_time=before_time,
                        after_time=after_time,
                        capsys=capsys,
                        diag_msg_args=diag_msg_args)

        # call base class normal method target
        tst_cls_get_caller_info0 = TestClassGetCallerInfo0()
        update_stack(exp_stack=exp_stack, line_num=5554, add=0)
        tst_cls_get_caller_info0.test_get_caller_info_m0bt(capsys=capsys)
        tst_cls_get_caller_info0s = TestClassGetCallerInfo0S()
        update_stack(exp_stack=exp_stack, line_num=5557, add=0)
        tst_cls_get_caller_info0s.test_get_caller_info_m0bt(capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=5561, add=1)
        cls.get_caller_info_s0bt(exp_stack=exp_stack,
                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5564, add=0)
        super().get_caller_info_s0bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5566, add=1)
        TestClassGetCallerInfo0.get_caller_info_s0bt(exp_stack=exp_stack,
                                                     capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=5569, add=1)
        TestClassGetCallerInfo0S.get_caller_info_s0bt(exp_stack=exp_stack,
                                                      capsys=capsys)
        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5573, add=0)
        func_get_caller_info_1(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=5578, add=1)
        cls_get_caller_info1.get_caller_info_m1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5583, add=1)
        cls_get_caller_info1.get_caller_info_s1(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5588, add=1)
        ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5593, add=1)
        cls_get_caller_info1.get_caller_info_m1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5598, add=1)
        cls_get_caller_info1.get_caller_info_s1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5603, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=5609, add=1)
        cls_get_caller_info1s.get_caller_info_m1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5614, add=1)
        cls_get_caller_info1s.get_caller_info_s1s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5619, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5624, add=1)
        cls_get_caller_info1s.get_caller_info_m1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5629, add=1)
        cls_get_caller_info1s.get_caller_info_s1bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5634, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5639, add=1)
        cls_get_caller_info1s.get_caller_info_m1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5644, add=1)
        cls_get_caller_info1s.get_caller_info_s1sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5649, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 1
########################################################################
class ClassGetCallerInfo1:
    """Class to get caller info1."""

    def __init__(self) -> None:
        """The initialization."""
        self.var1 = 1

    ####################################################################
    # Class 1 Method 1
    ####################################################################
    def get_caller_info_m1(self,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_m1',
                                     line_num=3945)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5688, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5695, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=5702, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5717, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=5722, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5727, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5732, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5737, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5742, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5747, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=5753, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5758, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5763, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5768, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5773, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5778, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5783, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5788, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5793, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s1(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_s1',
                                     line_num=4076)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5820, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5827, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=5834, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5849, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=5854, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5859, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5864, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=5869, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=5874, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=5879, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=5885, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=5890, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=5895, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=5900, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=5905, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=5910, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=5915, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=5920, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=5925, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c1(cls,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_c1',
                                     line_num=4207)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=5952, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=5959, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=5966, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=5981, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=5986, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=5991, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=5996, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6001, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6006, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6011, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6017, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6022, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6027, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6032, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6037, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6042, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6047, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6052, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6057, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 4
    ####################################################################
    def get_caller_info_m1bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_m1bo',
                                     line_num=4338)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6084, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6091, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6098, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6113, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6118, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6123, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6128, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6133, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6138, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6143, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6149, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6154, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6159, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6164, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6169, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6174, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6179, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6184, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6189, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s1bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_s1bo',
                                     line_num=4469)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6216, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6223, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6230, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6245, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6250, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6255, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6260, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6265, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6270, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6275, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6281, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6286, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6291, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6296, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6301, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6306, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6311, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6316, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6321, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c1bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_c1bo',
                                     line_num=4601)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6349, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6356, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6363, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6378, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6383, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6388, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6393, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6398, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6403, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6408, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6414, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6419, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6424, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6429, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6434, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6439, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6444, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6449, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6454, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 7
    ####################################################################
    def get_caller_info_m1bt(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_m1bt',
                                     line_num=4733)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6482, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6489, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6496, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6511, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6516, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6521, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6526, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6531, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6536, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6541, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6547, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6552, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6557, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6562, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6567, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6572, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6577, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6582, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6587, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s1bt(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_s1bt',
                                     line_num=4864)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6614, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6621, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6628, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6643, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6648, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6653, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6658, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6663, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6668, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6673, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6679, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6684, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6689, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6694, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6699, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6704, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6709, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6714, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6719, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1 Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c1bt(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1',
                                     func_name='get_caller_info_c1bt',
                                     line_num=4996)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6747, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6754, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6761, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6776, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6781, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6786, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6791, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6796, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6801, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6806, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6812, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6817, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6822, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6827, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6832, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6837, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6842, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6847, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6852, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 1S
########################################################################
class ClassGetCallerInfo1S(ClassGetCallerInfo1):
    """Subclass to get caller info1."""

    def __init__(self) -> None:
        """The initialization for subclass 1."""
        super().__init__()
        self.var2 = 2

    ####################################################################
    # Class 1S Method 1
    ####################################################################
    def get_caller_info_m1s(self,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_m1s',
                                     line_num=5139)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=6891, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=6898, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=6905, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=6920, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=6925, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=6930, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=6935, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=6940, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=6945, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=6950, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=6956, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=6961, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=6966, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=6971, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=6976, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=6981, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=6986, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=6991, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=6996, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s1s(exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_s1s',
                                     line_num=5270)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7023, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7030, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7037, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7052, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7057, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7062, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7067, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7072, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7077, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7082, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7088, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7093, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7098, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7103, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7108, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7113, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7118, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7123, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7128, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c1s(cls,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_c1s',
                                     line_num=5402)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7156, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7163, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7170, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7185, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7190, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7195, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7200, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7205, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7210, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7215, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7221, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7226, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7231, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7236, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7241, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7246, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7251, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7256, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7261, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 4
    ####################################################################
    def get_caller_info_m1bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_m1bo',
                                     line_num=5533)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7288, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7295, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7302, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7317, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7322, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7327, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7332, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7337, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7342, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7347, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7353, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7358, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7363, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7368, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7373, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7378, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7383, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7388, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7393, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s1bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_s1bo',
                                     line_num=5664)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7420, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7427, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7434, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7449, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7454, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7459, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7464, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7469, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7474, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7479, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7485, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7490, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7495, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7500, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7505, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7510, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7515, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7520, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7525, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c1bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_c1bo',
                                     line_num=5796)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7553, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7560, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7567, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7582, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7587, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7592, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7597, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7602, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7607, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7612, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7618, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7623, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7628, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7633, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7638, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7643, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7648, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7653, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7658, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 7
    ####################################################################
    def get_caller_info_m1sb(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_m1sb',
                                     line_num=5927)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7685, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7692, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7699, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        update_stack(exp_stack=exp_stack, line_num=7714, add=0)
        self.get_caller_info_m1bt(exp_stack=exp_stack, capsys=capsys)
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=7717, add=1)
        cls_get_caller_info1.get_caller_info_m1bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=7721, add=1)
        cls_get_caller_info1s.get_caller_info_m1bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=7726, add=0)
        self.get_caller_info_s1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7728, add=0)
        super().get_caller_info_s1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7730, add=1)
        ClassGetCallerInfo1.get_caller_info_s1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7733, add=1)
        ClassGetCallerInfo1S.get_caller_info_s1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=7738, add=0)
        super().get_caller_info_c1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7740, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7743, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7748, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7753, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7758, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7763, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7768, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7773, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7778, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7784, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7789, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7794, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7799, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7804, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7809, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7814, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7819, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7824, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s1sb(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_s1sb',
                                     line_num=6092)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=7851, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=7858, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=7865, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=7881, add=1)
        cls_get_caller_info1.get_caller_info_m1bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=7885, add=1)
        cls_get_caller_info1s.get_caller_info_m1bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=7890, add=1)
        ClassGetCallerInfo1.get_caller_info_s1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7893, add=1)
        ClassGetCallerInfo1S.get_caller_info_s1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=7898, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=7901, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=7906, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=7911, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=7916, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=7921, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=7926, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=7931, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=7936, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=7942, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=7947, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=7952, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=7957, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=7962, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=7967, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=7972, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=7977, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=7982, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 1S Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c1sb(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 1.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo1S',
                                     func_name='get_caller_info_c1sb',
                                     line_num=6250)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8010, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8017, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8024, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info1 = ClassGetCallerInfo1()
        update_stack(exp_stack=exp_stack, line_num=8040, add=1)
        cls_get_caller_info1.get_caller_info_m1bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info1s = ClassGetCallerInfo1S()
        update_stack(exp_stack=exp_stack, line_num=8044, add=1)
        cls_get_caller_info1s.get_caller_info_m1bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=8049, add=1)
        cls.get_caller_info_s1bt(exp_stack=exp_stack,
                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8052, add=0)
        super().get_caller_info_s1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8054, add=1)
        ClassGetCallerInfo1.get_caller_info_s1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8057, add=1)
        ClassGetCallerInfo1S.get_caller_info_s1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=8062, add=0)
        cls.get_caller_info_c1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8064, add=0)
        super().get_caller_info_c1bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8066, add=1)
        ClassGetCallerInfo1.get_caller_info_c1bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=8069, add=1)
        ClassGetCallerInfo1S.get_caller_info_c1bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8074, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=8079, add=1)
        cls_get_caller_info2.get_caller_info_m2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8084, add=1)
        cls_get_caller_info2.get_caller_info_s2(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8089, add=1)
        ClassGetCallerInfo2.get_caller_info_c2(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8094, add=1)
        cls_get_caller_info2.get_caller_info_m2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8099, add=1)
        cls_get_caller_info2.get_caller_info_s2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8104, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=8110, add=1)
        cls_get_caller_info2s.get_caller_info_m2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8115, add=1)
        cls_get_caller_info2s.get_caller_info_s2s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8120, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8125, add=1)
        cls_get_caller_info2s.get_caller_info_m2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8130, add=1)
        cls_get_caller_info2s.get_caller_info_s2bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8135, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8140, add=1)
        cls_get_caller_info2s.get_caller_info_m2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8145, add=1)
        cls_get_caller_info2s.get_caller_info_s2sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8150, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 2
########################################################################
class ClassGetCallerInfo2:
    """Class to get caller info2."""

    def __init__(self) -> None:
        """The initialization."""
        self.var1 = 1

    ####################################################################
    # Class 2 Method 1
    ####################################################################
    def get_caller_info_m2(self,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_m2',
                                     line_num=6428)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8189, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8196, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8203, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8218, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8223, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8228, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8233, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8238, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8243, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8248, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8254, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8259, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8264, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8269, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8274, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8279, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8284, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8289, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8294, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s2(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_s2',
                                     line_num=6559)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8321, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8328, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8335, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8350, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8355, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8360, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8365, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8370, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8375, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8380, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8386, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8391, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8396, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8401, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8406, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8411, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8416, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8421, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8426, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c2(cls,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_c2',
                                     line_num=6690)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8453, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8460, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8467, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8482, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8487, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8492, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8497, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8502, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8507, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8512, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8518, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8523, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8528, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8533, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8538, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8543, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8548, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8553, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8558, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 4
    ####################################################################
    def get_caller_info_m2bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_m2bo',
                                     line_num=6821)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8585, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8592, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8599, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8614, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8619, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8624, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8629, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8634, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8639, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8644, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8650, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8655, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8660, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8665, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8670, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8675, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8680, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8685, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8690, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s2bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_s2bo',
                                     line_num=6952)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8717, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8724, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8731, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8746, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8751, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8756, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8761, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8766, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8771, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8776, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8782, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8787, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8792, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8797, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8802, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8807, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8812, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8817, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8822, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c2bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_c2bo',
                                     line_num=7084)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8850, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8857, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8864, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=8879, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=8884, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=8889, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=8894, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=8899, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=8904, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=8909, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=8915, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=8920, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=8925, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=8930, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=8935, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=8940, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=8945, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=8950, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=8955, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 7
    ####################################################################
    def get_caller_info_m2bt(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_m2bt',
                                     line_num=7216)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=8983, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=8990, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=8997, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9012, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9017, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9022, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9027, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9032, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9037, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9042, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9048, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9053, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9058, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9063, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9068, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9073, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9078, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9083, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9088, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s2bt(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_s2bt',
                                     line_num=7347)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9115, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9122, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9129, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9144, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9149, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9154, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9159, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9164, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9169, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9174, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9180, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9185, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9190, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9195, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9200, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9205, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9210, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9215, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9220, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2 Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c2bt(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2',
                                     func_name='get_caller_info_c2bt',
                                     line_num=7479)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9248, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9255, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9262, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9277, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9282, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9287, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9292, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9297, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9302, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9307, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9313, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9318, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9323, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9328, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9333, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9338, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9343, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9348, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9353, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 2S
########################################################################
class ClassGetCallerInfo2S(ClassGetCallerInfo2):
    """Subclass to get caller info2."""

    def __init__(self) -> None:
        """The initialization for subclass 2."""
        super().__init__()
        self.var2 = 2

    ####################################################################
    # Class 2S Method 1
    ####################################################################
    def get_caller_info_m2s(self,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_m2s',
                                     line_num=7622)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9392, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9399, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9406, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9421, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9426, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9431, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9436, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9441, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9446, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9451, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9457, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9462, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9467, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9472, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9477, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9482, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9487, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9492, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9497, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s2s(exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_s2s',
                                     line_num=7753)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9524, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9531, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9538, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9553, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9558, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9563, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9568, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9573, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9578, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9583, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9589, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9594, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9599, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9604, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9609, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9614, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9619, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9624, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9629, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c2s(cls,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_c2s',
                                     line_num=7885)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9657, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9664, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9671, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9686, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9691, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9696, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9701, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9706, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9711, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9716, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9722, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9727, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9732, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9737, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9742, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9747, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9752, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9757, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9762, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 4
    ####################################################################
    def get_caller_info_m2bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_m2bo',
                                     line_num=8016)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9789, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9796, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9803, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9818, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9823, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9828, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9833, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9838, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9843, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9848, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9854, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9859, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9864, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=9869, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=9874, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=9879, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=9884, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=9889, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=9894, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s2bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_s2bo',
                                     line_num=8147)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=9921, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=9928, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=9935, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=9950, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=9955, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=9960, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=9965, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=9970, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=9975, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=9980, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=9986, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=9991, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=9996, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=10001, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=10006, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=10011, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=10016, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=10021, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=10026, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c2bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_c2bo',
                                     line_num=8279)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10054, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10061, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10068, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=10083, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=10088, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=10093, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=10098, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=10103, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=10108, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=10113, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=10119, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=10124, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=10129, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=10134, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=10139, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=10144, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=10149, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=10154, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=10159, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 7
    ####################################################################
    def get_caller_info_m2sb(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_m2sb',
                                     line_num=8410)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10186, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10193, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10200, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        update_stack(exp_stack=exp_stack, line_num=10215, add=0)
        self.get_caller_info_m2bt(exp_stack=exp_stack, capsys=capsys)
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=10218, add=1)
        cls_get_caller_info2.get_caller_info_m2bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=10222, add=1)
        cls_get_caller_info2s.get_caller_info_m2bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=10227, add=0)
        self.get_caller_info_s2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10229, add=0)
        super().get_caller_info_s2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10231, add=1)
        ClassGetCallerInfo2.get_caller_info_s2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10234, add=1)
        ClassGetCallerInfo2S.get_caller_info_s2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=10239, add=0)
        super().get_caller_info_c2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10241, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10244, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=10249, add=0)
        func_get_caller_info_2(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=10254, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=10259, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=10264, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=10269, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=10274, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=10279, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=10285, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=10290, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=10295, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=10300, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=10305, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=10310, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=10315, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=10320, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=10325, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s2sb(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_s2sb',
                                     line_num=8575)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10352, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10359, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10366, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=10382, add=1)
        cls_get_caller_info2.get_caller_info_m2bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=10386, add=1)
        cls_get_caller_info2s.get_caller_info_m2bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=10391, add=1)
        ClassGetCallerInfo2.get_caller_info_s2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10394, add=1)
        ClassGetCallerInfo2S.get_caller_info_s2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=10399, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10402, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=10407, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=10412, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=10417, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=10422, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=10427, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=10432, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=10437, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=10443, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=10448, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=10453, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=10458, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=10463, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=10468, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=10473, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=10478, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=10483, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 2S Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c2sb(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 2.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo2S',
                                     func_name='get_caller_info_c2sb',
                                     line_num=8733)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10511, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10518, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10525, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info2 = ClassGetCallerInfo2()
        update_stack(exp_stack=exp_stack, line_num=10541, add=1)
        cls_get_caller_info2.get_caller_info_m2bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info2s = ClassGetCallerInfo2S()
        update_stack(exp_stack=exp_stack, line_num=10545, add=1)
        cls_get_caller_info2s.get_caller_info_m2bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=10550, add=1)
        cls.get_caller_info_s2bt(exp_stack=exp_stack,
                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10553, add=0)
        super().get_caller_info_s2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10555, add=1)
        ClassGetCallerInfo2.get_caller_info_s2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10558, add=1)
        ClassGetCallerInfo2S.get_caller_info_s2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=10563, add=0)
        cls.get_caller_info_c2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10565, add=0)
        super().get_caller_info_c2bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10567, add=1)
        ClassGetCallerInfo2.get_caller_info_c2bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=10570, add=1)
        ClassGetCallerInfo2S.get_caller_info_c2bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call module level function
        update_stack(exp_stack=exp_stack, line_num=10575, add=0)
        func_get_caller_info_3(exp_stack=exp_stack, capsys=capsys)

        # call method
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=10580, add=1)
        cls_get_caller_info3.get_caller_info_m3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call static method
        update_stack(exp_stack=exp_stack, line_num=10585, add=1)
        cls_get_caller_info3.get_caller_info_s3(exp_stack=exp_stack,
                                                capsys=capsys)

        # call class method
        update_stack(exp_stack=exp_stack, line_num=10590, add=1)
        ClassGetCallerInfo3.get_caller_info_c3(exp_stack=exp_stack,
                                               capsys=capsys)

        # call overloaded base class method
        update_stack(exp_stack=exp_stack, line_num=10595, add=1)
        cls_get_caller_info3.get_caller_info_m3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class static method
        update_stack(exp_stack=exp_stack, line_num=10600, add=1)
        cls_get_caller_info3.get_caller_info_s3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call overloaded base class class method
        update_stack(exp_stack=exp_stack, line_num=10605, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bo(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call subclass method
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=10611, add=1)
        cls_get_caller_info3s.get_caller_info_m3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass static method
        update_stack(exp_stack=exp_stack, line_num=10616, add=1)
        cls_get_caller_info3s.get_caller_info_s3s(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call subclass class method
        update_stack(exp_stack=exp_stack, line_num=10621, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3s(exp_stack=exp_stack,
                                                 capsys=capsys)

        # call overloaded subclass method
        update_stack(exp_stack=exp_stack, line_num=10626, add=1)
        cls_get_caller_info3s.get_caller_info_m3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass static method
        update_stack(exp_stack=exp_stack, line_num=10631, add=1)
        cls_get_caller_info3s.get_caller_info_s3bo(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call overloaded subclass class method
        update_stack(exp_stack=exp_stack, line_num=10636, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bo(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base method from subclass method
        update_stack(exp_stack=exp_stack, line_num=10641, add=1)
        cls_get_caller_info3s.get_caller_info_m3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base static method from subclass static method
        update_stack(exp_stack=exp_stack, line_num=10646, add=1)
        cls_get_caller_info3s.get_caller_info_s3sb(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class method from subclass class method
        update_stack(exp_stack=exp_stack, line_num=10651, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3sb(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# Class 3
########################################################################
class ClassGetCallerInfo3:
    """Class to get caller info3."""

    def __init__(self) -> None:
        """The initialization."""
        self.var1 = 1

    ####################################################################
    # Class 3 Method 1
    ####################################################################
    def get_caller_info_m3(self,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_m3',
                                     line_num=8911)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10690, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10697, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10704, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s3(exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_s3',
                                     line_num=8961)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10741, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10748, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10755, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c3(cls,
                           exp_stack: Deque[CallerInfo],
                           capsys: Optional[Any]) -> None:
        """Get caller info class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_c3',
                                     line_num=9011)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10792, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10799, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10806, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 4
    ####################################################################
    def get_caller_info_m3bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_m3bo',
                                     line_num=9061)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10843, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10850, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10857, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s3bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_s3bo',
                                     line_num=9111)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10894, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10901, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10908, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c3bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_c3bo',
                                     line_num=9162)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10946, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=10953, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=10960, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 7
    ####################################################################
    def get_caller_info_m3bt(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_m3bt',
                                     line_num=9213)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=10998, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11005, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11012, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s3bt(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_s3bt',
                                     line_num=9263)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11049, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11056, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11063, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3 Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c3bt(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3',
                                     func_name='get_caller_info_c3bt',
                                     line_num=9314)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11101, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11108, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11115, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()


########################################################################
# Class 3S
########################################################################
class ClassGetCallerInfo3S(ClassGetCallerInfo3):
    """Subclass to get caller info3."""

    def __init__(self) -> None:
        """The initialization for subclass 3."""
        super().__init__()
        self.var2 = 2

    ####################################################################
    # Class 3S Method 1
    ####################################################################
    def get_caller_info_m3s(self,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output
        """
        self.var1 += 1
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_m3s',
                                     line_num=9376)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11164, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11171, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11178, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 2
    ####################################################################
    @staticmethod
    def get_caller_info_s3s(exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_s3s',
                                     line_num=9426)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11215, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11222, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11229, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 3
    ####################################################################
    @classmethod
    def get_caller_info_c3s(cls,
                            exp_stack: Deque[CallerInfo],
                            capsys: Optional[Any]) -> None:
        """Get caller info class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_c3s',
                                     line_num=9477)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11267, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11274, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11281, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 4
    ####################################################################
    def get_caller_info_m3bo(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_m3bo',
                                     line_num=9527)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11318, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11325, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11332, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 5
    ####################################################################
    @staticmethod
    def get_caller_info_s3bo(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_s3bo',
                                     line_num=9577)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11369, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11376, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11383, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 6
    ####################################################################
    @classmethod
    def get_caller_info_c3bo(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_c3bo',
                                     line_num=9628)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11421, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11428, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11435, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 7
    ####################################################################
    def get_caller_info_m3sb(self,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_m3sb',
                                     line_num=9678)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11472, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11479, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11486, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        update_stack(exp_stack=exp_stack, line_num=11501, add=0)
        self.get_caller_info_m3bt(exp_stack=exp_stack, capsys=capsys)
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=11504, add=1)
        cls_get_caller_info3.get_caller_info_m3bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=11508, add=1)
        cls_get_caller_info3s.get_caller_info_m3bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=11513, add=0)
        self.get_caller_info_s3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11515, add=0)
        super().get_caller_info_s3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11517, add=1)
        ClassGetCallerInfo3.get_caller_info_s3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11520, add=1)
        ClassGetCallerInfo3S.get_caller_info_s3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=11525, add=0)
        super().get_caller_info_c3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11527, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11530, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 8
    ####################################################################
    @staticmethod
    def get_caller_info_s3sb(exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded static method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_s3sb',
                                     line_num=9762)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11557, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11564, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11571, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=11587, add=1)
        cls_get_caller_info3.get_caller_info_m3bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=11591, add=1)
        cls_get_caller_info3s.get_caller_info_m3bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=11596, add=1)
        ClassGetCallerInfo3.get_caller_info_s3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11599, add=1)
        ClassGetCallerInfo3S.get_caller_info_s3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=11604, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11607, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()

    ####################################################################
    # Class 3S Method 9
    ####################################################################
    @classmethod
    def get_caller_info_c3sb(cls,
                             exp_stack: Deque[CallerInfo],
                             capsys: Optional[Any]) -> None:
        """Get caller info overloaded class method 3.

        Args:
            exp_stack: The expected call stack
            capsys: Pytest fixture that captures output

        """
        exp_caller_info = CallerInfo(mod_name='test_diag_msg.py',
                                     cls_name='ClassGetCallerInfo3S',
                                     func_name='get_caller_info_c3sb',
                                     line_num=9839)
        exp_stack.append(exp_caller_info)
        update_stack(exp_stack=exp_stack, line_num=11635, add=0)
        for i, expected_caller_info in enumerate(list(reversed(exp_stack))):
            try:
                frame = _getframe(i)
                caller_info = get_caller_info(frame)
            finally:
                del frame
            assert caller_info == expected_caller_info

        # test call sequence
        update_stack(exp_stack=exp_stack, line_num=11642, add=0)
        call_seq = get_formatted_call_sequence(depth=len(exp_stack))

        assert call_seq == get_exp_seq(exp_stack=exp_stack)

        if capsys:  # if capsys, test diag_msg
            update_stack(exp_stack=exp_stack, line_num=11649, add=0)
            before_time = datetime.now()
            diag_msg('message 1', 1, depth=len(exp_stack))
            after_time = datetime.now()

            diag_msg_args = TestDiagMsg.get_diag_msg_args(
                depth_arg=len(exp_stack),
                msg_arg=['message 1', 1])

            verify_diag_msg(exp_stack=exp_stack,
                            before_time=before_time,
                            after_time=after_time,
                            capsys=capsys,
                            diag_msg_args=diag_msg_args)

        # call base class normal method target
        cls_get_caller_info3 = ClassGetCallerInfo3()
        update_stack(exp_stack=exp_stack, line_num=11665, add=1)
        cls_get_caller_info3.get_caller_info_m3bt(exp_stack=exp_stack,
                                                  capsys=capsys)
        cls_get_caller_info3s = ClassGetCallerInfo3S()
        update_stack(exp_stack=exp_stack, line_num=11669, add=1)
        cls_get_caller_info3s.get_caller_info_m3bt(exp_stack=exp_stack,
                                                   capsys=capsys)

        # call base class static method target
        update_stack(exp_stack=exp_stack, line_num=11674, add=1)
        cls.get_caller_info_s3bt(exp_stack=exp_stack,
                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11677, add=0)
        super().get_caller_info_s3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11679, add=1)
        ClassGetCallerInfo3.get_caller_info_s3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11682, add=1)
        ClassGetCallerInfo3S.get_caller_info_s3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        # call base class class method target
        update_stack(exp_stack=exp_stack, line_num=11687, add=0)
        cls.get_caller_info_c3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11689, add=0)
        super().get_caller_info_c3bt(exp_stack=exp_stack, capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11691, add=1)
        ClassGetCallerInfo3.get_caller_info_c3bt(exp_stack=exp_stack,
                                                 capsys=capsys)
        update_stack(exp_stack=exp_stack, line_num=11694, add=1)
        ClassGetCallerInfo3S.get_caller_info_c3bt(exp_stack=exp_stack,
                                                  capsys=capsys)

        exp_stack.pop()


########################################################################
# following tests needs to be at module level (i.e., script form)
########################################################################

########################################################################
# test get_caller_info from module (script) level
########################################################################
exp_stack0: Deque[CallerInfo] = deque()
exp_caller_info0 = CallerInfo(mod_name='test_diag_msg.py',
                              cls_name='',
                              func_name='',
                              line_num=9921)

exp_stack0.append(exp_caller_info0)
update_stack(exp_stack=exp_stack0, line_num=11718, add=0)
for i0, expected_caller_info0 in enumerate(list(reversed(exp_stack0))):
    try:
        frame0 = _getframe(i0)
        caller_info0 = get_caller_info(frame0)
    finally:
        del frame0
    assert caller_info0 == expected_caller_info0

########################################################################
# test get_formatted_call_sequence from module (script) level
########################################################################
update_stack(exp_stack=exp_stack0, line_num=11727, add=0)
call_seq0 = get_formatted_call_sequence(depth=1)

assert call_seq0 == get_exp_seq(exp_stack=exp_stack0)

########################################################################
# test diag_msg from module (script) level
# note that this is just a smoke test and is only visually verified
########################################################################
diag_msg()  # basic, empty msg
diag_msg('hello')
diag_msg(depth=2)
diag_msg('hello2', depth=3)
diag_msg(depth=4, end='\n\n')
diag_msg('hello3', depth=5, end='\n\n')

# call module level function
update_stack(exp_stack=exp_stack0, line_num=11744, add=0)
func_get_caller_info_1(exp_stack=exp_stack0, capsys=None)

# call method
cls_get_caller_info01 = ClassGetCallerInfo1()
update_stack(exp_stack=exp_stack0, line_num=11749, add=0)
cls_get_caller_info01.get_caller_info_m1(exp_stack=exp_stack0, capsys=None)

# call static method
update_stack(exp_stack=exp_stack0, line_num=11753, add=0)
cls_get_caller_info01.get_caller_info_s1(exp_stack=exp_stack0, capsys=None)

# call class method
update_stack(exp_stack=exp_stack0, line_num=11757, add=0)
ClassGetCallerInfo1.get_caller_info_c1(exp_stack=exp_stack0, capsys=None)

# call overloaded base class method
update_stack(exp_stack=exp_stack0, line_num=11761, add=0)
cls_get_caller_info01.get_caller_info_m1bo(exp_stack=exp_stack0, capsys=None)

# call overloaded base class static method
update_stack(exp_stack=exp_stack0, line_num=11765, add=0)
cls_get_caller_info01.get_caller_info_s1bo(exp_stack=exp_stack0, capsys=None)

# call overloaded base class class method
update_stack(exp_stack=exp_stack0, line_num=11769, add=0)
ClassGetCallerInfo1.get_caller_info_c1bo(exp_stack=exp_stack0, capsys=None)

# call subclass method
cls_get_caller_info01S = ClassGetCallerInfo1S()
update_stack(exp_stack=exp_stack0, line_num=11774, add=0)
cls_get_caller_info01S.get_caller_info_m1s(exp_stack=exp_stack0, capsys=None)

# call subclass static method
update_stack(exp_stack=exp_stack0, line_num=11778, add=0)
cls_get_caller_info01S.get_caller_info_s1s(exp_stack=exp_stack0, capsys=None)

# call subclass class method
update_stack(exp_stack=exp_stack0, line_num=11782, add=0)
ClassGetCallerInfo1S.get_caller_info_c1s(exp_stack=exp_stack0, capsys=None)

# call overloaded subclass method
update_stack(exp_stack=exp_stack0, line_num=11786, add=0)
cls_get_caller_info01S.get_caller_info_m1bo(exp_stack=exp_stack0, capsys=None)

# call overloaded subclass static method
update_stack(exp_stack=exp_stack0, line_num=11790, add=0)
cls_get_caller_info01S.get_caller_info_s1bo(exp_stack=exp_stack0, capsys=None)

# call overloaded subclass class method
update_stack(exp_stack=exp_stack0, line_num=11794, add=0)
ClassGetCallerInfo1S.get_caller_info_c1bo(exp_stack=exp_stack0, capsys=None)

# call base method from subclass method
update_stack(exp_stack=exp_stack0, line_num=11798, add=0)
cls_get_caller_info01S.get_caller_info_m1sb(exp_stack=exp_stack0, capsys=None)

# call base static method from subclass static method
update_stack(exp_stack=exp_stack0, line_num=11802, add=0)
cls_get_caller_info01S.get_caller_info_s1sb(exp_stack=exp_stack0, capsys=None)

# call base class method from subclass class method
update_stack(exp_stack=exp_stack0, line_num=11806, add=0)
ClassGetCallerInfo1S.get_caller_info_c1sb(exp_stack=exp_stack0, capsys=None)
