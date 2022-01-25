# Copyright 2012-2020 Intel Corporation
#
# This software and the related documents are Intel copyrighted
# materials, and your use of them is governed by the express license
# under which they were provided to you (License). Unless the License
# provides otherwise, you may not use, modify, copy, publish,
# distribute, disclose or transmit this software or the related
# documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no
# express or implied warranties, other than those that are expressly
# stated in the License.

# OCL Work-Item Breakpoint Command

import inspect
import traceback
from threading import Lock

class OCLWIBreakpoint(gdb.Breakpoint):
    """ Breakpoint that stops on a specific OCL Work Item """

    eval_lock = Lock()

    def __init__(self, location, x, y, z, temporary):

        try:
            if 'temporary' in dict(inspect.getmembers(gdb.Breakpoint)):
                super(OCLWIBreakpoint, self).__init__(location, temporary=temporary)
            else: #old versions of gdb.Breakpoint cannot be temporary
                super(OCLWIBreakpoint, self).__init__(location)
        except RuntimeError as e:
            ### GDB crashes when asked to set a breakpoint in code that has
            ### been elimited due to dead-code-elimination (if the line number
            ### is at the end of the file.)
            print("WARNING: Unable to set OpenCL breakpoint at location " +
                  location + ". Reason: " + str(e))
            return

        self.gid_x = str(x)
        self.gid_y = str(y)
        self.gid_z = str(z)
        # TODO: remove
        print("OpenCL Breakpoint set at: " + location + " for work item (" +
              self.gid_x + ", " + self.gid_y + ", " + self.gid_z + ")")

        # According to the docs it should be possible to make a conditional
        # breakpoint in GDB by setting the 'condition' field. However,
        # we cannot directly set the breakpoint's condition field because
        # it prevents GDB from being able to insert the breakpoint as it
        # attempts to resolve the location during insertion, which may not
        # be possible because the breakpoint location could be in 
        # (not-yet-JITTed) code. The error message is:
        # "Error in re-setting breakpoing N: No source file named ...."
        # in GDB 7.3.1.
        #self.condition = "__ocl_dbg_gid0 == " + str(x) \
        #              + " && __ocl_dbg_gid1 == " + str(y) \
        #              + " && __ocl_dbg_gid2 == " + str(z)
        #print "OCL workitem breakpoint set at: " + location + " condition=" \
        #  + str(self.condition)


    def stop (self):
        if not self.location:
            return False

        cur_gid_x, cur_gid_y, cur_gid_z = None, None, None
        try:
            # Evaluate the inferior frame's hidden global id variables
            if all([self.gid_x == str(gdb.parse_and_eval("__ocl_dbg_gid0")),
                    self.gid_y == str(gdb.parse_and_eval("__ocl_dbg_gid1")),
                    self.gid_z == str(gdb.parse_and_eval("__ocl_dbg_gid2"))]):
                # OpenCL Breakpoint stops on the specified GID
                return True
        except gdb.error as e:
            print("WARNING: OpenCL Breakpoint unable to evaluate work-item ID." +
                  " Stopping at " + str(self.location) + ".")
            return True

        # OpenCL Breakpoint not stopping
        return False

class OCLBreakpointCommand(gdb.Command):
    """ Implements the ocl-break-workitem command """

    NAME = "ocl-break-workitem"
    CLASS = gdb.COMMAND_BREAKPOINTS

    def __init__(self):
        super(OCLBreakpointCommand, self).__init__(
            name=OCLBreakpointCommand.NAME,
            command_class=OCLBreakpointCommand.CLASS)
        self.breakpoints = []

    def usage(self):
        """ Returns usage string """
        return "Usage: " + OCLBreakpointCommand.NAME \
          + " <location> [gid_x [gid_y [gid_z [temporary]]]\n"

    def invoke(self, argument, from_tty):
        params = argument.rsplit(' ', 4)
        max_params = 5
        if len(params) == max_params and params[4] != 'temporary':
            params = argument.rsplit(' ', 3)
            max_params = 4
        if len(params) > max_params:
            print(self.usage())
            raise gdb.error("Too many parameters to "
                + OCLBreakpointCommand.NAME + ": " + str(params))

        params += [0] * 3
        params += ['']
        location = params[0]
        gid_x, gid_y, gid_z = params[1:4]
        temporary = (params[4] == 'temporary') if len(params) >= 5 else False

        b = OCLWIBreakpoint(location, gid_x, gid_y, gid_z, temporary)
        self.breakpoints.append(b)

    def complete(self, text, word):
        """ Return the special GDB constant to auto-complete locations """
        return gdb.COMPLETE_LOCATION

b = OCLBreakpointCommand()
