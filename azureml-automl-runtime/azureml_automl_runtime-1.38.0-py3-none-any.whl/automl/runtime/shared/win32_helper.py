# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""win32_helper.py, Helper code that wraps the Win32 API using ctypes."""
from typing import Any, cast, Dict, List, Optional, Tuple, TypeVar
import platform
import sys

from azureml.automl.core.shared._error_response_constants import ErrorCodes


if sys.platform == 'win32':
    # See https://stackoverflow.com/a/12578715/1502893
    IS_64_BIT = '64' in platform.machine()

    import ctypes
    from ctypes import windll
    from ctypes import wintypes
    from azureml.automl.core.shared.exceptions import ClientException

    # Defining types not found in wintypes here for convenience
    SIZE_T = ctypes.c_size_t
    ULONG_PTR = ctypes.c_uint64 if IS_64_BIT else ctypes.c_uint32
    DWORD64 = ctypes.c_int64

    JobInfoStruct = TypeVar('JobInfoStruct', bound=ctypes.Structure)

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        """Process memory counters class."""

        _fields_ = [('cb', wintypes.DWORD),
                    ('PageFaultCount', wintypes.DWORD),
                    ('PeakWorkingSetSize', wintypes.WPARAM),
                    ('WorkingSetSize', wintypes.WPARAM),
                    ('QuotaPeakPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaPeakNonPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaNonPagedPoolUsage', wintypes.WPARAM),
                    ('PagefileUsage', wintypes.WPARAM),
                    ('PeakPagefileUsage', wintypes.WPARAM),
                    ('PrivateUsage', wintypes.WPARAM)]

    class IO_COUNTERS(ctypes.Structure):
        """IO counters class."""

        _fields_ = [('ReadOperationCount', wintypes.ULARGE_INTEGER),
                    ('WriteOperationCount', wintypes.ULARGE_INTEGER),
                    ('OtherOperationCount', wintypes.ULARGE_INTEGER),
                    ('ReadTransferCount', wintypes.ULARGE_INTEGER),
                    ('WriteTransferCount', wintypes.ULARGE_INTEGER),
                    ('OtherTransferCount', wintypes.ULARGE_INTEGER)]

    class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
        """Basic accounting information class."""

        _fields_ = [('TotalUserTime', wintypes.LARGE_INTEGER),
                    ('TotalKernelTime', wintypes.LARGE_INTEGER),
                    ('ThisPeriodTotalUserTime', wintypes.LARGE_INTEGER),
                    ('ThisPeriodTotalKernelTime', wintypes.LARGE_INTEGER),
                    ('TotalPageFaultCount', wintypes.DWORD),
                    ('TotalProcesses', wintypes.DWORD),
                    ('ActiveProcesses', wintypes.DWORD),
                    ('TotalTerminatedProcesses', wintypes.DWORD)]

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        """
        Basic limit information class. Processes exceeding specified limits are killed.

        Use in conjunction with SetInformationJobObject and QueryInformationJobObject API calls. Refer to MSDN
        documentation for usage information.
        """

        class ValidLimitFlags:
            """Enum class for specifying limit settings."""

            LimitActiveProcess = 0x8
            LimitAffinity = 0x10
            LimitBreakawayOk = 0x800
            LimitDieOnUnhandledException = 0x400
            LimitJobMemory = 0x200
            LimitJobTime = 0x4
            LimitKillOnJobClose = 0x2000
            LimitPreserveJobTime = 0x40
            LimitPriorityClass = 0x20
            LimitProcessMemory = 0x100
            LimitProcessTime = 0x2
            LimitSchedulingClass = 0x80
            LimitSilentBreakawayOk = 0x1000
            LimitSubsetAffinity = 0x4000
            LimitWorkingset = 0x1

        _fields_ = [('PerProcessUserTimeLimit', wintypes.LARGE_INTEGER),
                    ('PerJobUserTimeLimit', wintypes.LARGE_INTEGER),
                    ('LimitFlags', wintypes.DWORD),                         # Use ValidLimitFlags
                    ('MinimumWorkingSetSize', SIZE_T),
                    ('MaximumWorkingSetSize', SIZE_T),
                    ('ActiveProcessLimit', wintypes.DWORD),
                    ('Affinity', ULONG_PTR),
                    ('PriorityClass', wintypes.DWORD),
                    ('SchedulingClass', wintypes.DWORD)]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        """
        Extended limit information class. Processes exceeding specified limits are killed.

        Use in conjunction with SetInformationJobObject and QueryInformationJobObject API calls. Refer to MSDN
        documentation for usage information.
        """

        _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
                    ('IoInfo', IO_COUNTERS),
                    ('ProcessMemoryLimit', SIZE_T),
                    ('JobMemoryLimit', SIZE_T),
                    ('PeakProcessMemoryUsed', SIZE_T),
                    ('PeakJobMemoryUsed', SIZE_T)]

    class JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION(ctypes.Structure):
        """Basic accounting information and IO counters class."""

        _fields_ = [('BasicInfo', JOBOBJECT_BASIC_ACCOUNTING_INFORMATION),
                    ('IoInfo', IO_COUNTERS)]

    class MEMORYSTATUSEX(ctypes.Structure):
        """The information about memory."""

        _fields_ = [
            ('dwLength', wintypes.ULONG),
            ('dwMemoryLoad', wintypes.ULONG),
            ('ullTotalPhys', wintypes.ULARGE_INTEGER),
            ('ullAvailPhys', wintypes.ULARGE_INTEGER),
            ('ullTotalPageFile', wintypes.ULARGE_INTEGER),
            ('ullAvailPageFile', wintypes.ULARGE_INTEGER),
            ('ullTotalVirtual', wintypes.ULARGE_INTEGER),
            ('ullAvailVirtual', wintypes.ULARGE_INTEGER),
            ('ullAvailExtendedVirtual', wintypes.ULARGE_INTEGER)
        ]

    class JobObjectInfoClass:
        """Job object information class."""

        JobObjectBasicAccountingInformation = 1
        JobObjectBasicAndIoAccountingInformation = 8
        JobObjectBasicLimitInformation = 2
        JobObjectBasicProcessIdList = 3
        JobObjectBasicUIRestrictions = 4
        JobObjectCpuRateControlInformation = 15
        JobObjectEndOfJobTimeInformation = 6
        JobObjectExtendedLimitInformation = 9
        JobObjectGroupInformation = 11
        JobObjectGroupInformationEx = 14
        JobObjectLimitViolationInformation = 13
        JobObjectLimitViolationInformation2 = 35
        JobObjectNetRateControlInformation = 32
        JobObjectNotificationLimitInformation = 12
        JobObjectNotificationLimitInformation2 = 34

    class Win32Exception(ClientException):
        """Exception related to a win32 API call."""

        _error_code = ErrorCodes.OS_ERROR

        def __init__(self, api_name: str, win_error_code: int):
            """
            Construct a new Win32Exception.

            :param api_name: API name
            :param win_error_code: Win32 error code
            """
            self.api_name = api_name
            self.win_error_code = win_error_code
            # For all Win32Exceptions, we only record the API name and the Windows error code, so no PII is recorded
            super().__init__('Win32 {} API call failed: [WinError {}] {}'.format(
                api_name, win_error_code, ctypes.FormatError(win_error_code),
            ), has_pii=False)

    class _Win32Helper:
        """Win32Helper class. Should only be used as a singleton."""

        def __init__(self):
            """Initialize Win32Helper class."""
            # Get a handle to ourselves for future use

            # HANDLE GetCurrentProcess()
            self.current_process = cast(wintypes.HANDLE, windll.kernel32.GetCurrentProcess())

            self.child_handles = {}     # type: Dict[int, wintypes.HANDLE]

            # Create a job with the name automl-{PID} and assign ourselves to it. All child processes will inherit
            # this job object so we can look them up later.

            job_name = 'automl-{}'.format(self.get_process_id())

            # Attempt to open a job object if it already exists
            # Handle OpenJobObjectW(DWORD dwDesiredAccess, BOOL bInheritHandle, LPCWSTR lpName)
            JOB_OBJECT_ALL_ACCESS = 0x1F001F
            self.job_object = cast(wintypes.HANDLE, windll.kernel32.OpenJobObjectW(
                JOB_OBJECT_ALL_ACCESS, None, job_name
            ))

            if self.job_object == 0:
                err = self.get_error('OpenJobObjectW')
                # Win32 error code 2: The path could not be found
                # We will get it if the job doesn't already exist.
                if err.win_error_code != 2:
                    raise err

                # If running on Windows 7 or earlier, job objects cannot be nested. This should be okay since we
                # can pass NULL to get the parent's job.

                if self.is_windows_7_or_earlier():
                    self.job_object = cast(wintypes.HANDLE, None)
                else:
                    # In all other cases, since the job doesn't exist already, create it.
                    self.job_object = self.create_job_object(job_name)

                    # Set flag on the job that causes all processes in the job to be killed when all handles are closed
                    extended_limit_struct = self.query_information_job_object(
                        self.job_object,
                        JobObjectInfoClass.JobObjectExtendedLimitInformation,
                        JOBOBJECT_EXTENDED_LIMIT_INFORMATION())
                    extended_limit_struct.BasicLimitInformation.LimitFlags |= \
                        JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitKillOnJobClose
                    self.set_information_job_object(self.job_object,
                                                    JobObjectInfoClass.JobObjectExtendedLimitInformation,
                                                    extended_limit_struct)

                    # Then add ourselves to the job
                    self.assign_process_to_job_object(self.job_object)

        def __del__(self):
            # Prevent handle leaks
            try:
                self.close_handle(self.job_object)
            except Win32Exception as e:
                if e.win_error_code == 6:
                    # Win32 error code 6: The handle is invalid
                    # Occurs if the handle has already been closed, in which case we don't need to do anything.
                    pass
                raise

        @staticmethod
        def is_windows_7_or_earlier() -> bool:
            winver = sys.getwindowsversion()
            return (winver.major == 6 and winver.minor <= 1) or winver.major < 6

        @classmethod
        def create_job_object(cls, job_name: str) -> wintypes.HANDLE:
            """
            Create a job object using Win32 CreateJobObjectW.

            If the job object already exists with the given name, returns a handle to the existing job object.
            The ERROR_ALREADY_EXISTS error in that case is swallowed.

            HANDLE CreateJobObjectW(
              LPSECURITY_ATTRIBUTES lpJobAttributes,
              LPCWSTR lpName
            );

            :param job_name: the name of the new job object
            :return: a handle to the new job object
            """
            handle = cast(wintypes.HANDLE, windll.kernel32.CreateJobObjectW(None, job_name))
            if handle == 0:
                # Note that we don't have to explicitly handle the "already exists" case, since handle won't be NULL
                # in that case. In all other cases, this code path should get hit.
                raise cls.get_error('CreateJobObjectW')
            return handle

        @classmethod
        def close_handle(cls, handle: wintypes.HANDLE) -> None:
            """
            Close handle wrapper for the Win32 CloseHandle function.

            BOOL WINAPI CloseHandle(
              _In_ HANDLE hObject
            );

            :param handle: A valid handle to an open object.
            """
            success = windll.kernel32.CloseHandle(handle)
            if success == 0:
                raise cls.get_error('CloseHandle')

        def get_process_id(self) -> int:
            """
            Get process Id for Win32 GetProcessId function.

            DWORD GetProcessId(
              HANDLE Process
            );

            :return: the pid of the current process
            """
            return cast(int, windll.kernel32.GetProcessId(self.current_process))

        def open_process(self, pid: Optional[int] = None) -> wintypes.HANDLE:
            """
            Open process wrapper for the Win32 OpenProcess function.

            Note: If a handle was already opened, the previously opened handle is returned instead. This is to prevent
            memory leaks from opening too many handles and then failing to close them. This way, we only need to close
            handles once (when this object is destroyed).
            HANDLE OpenProcess(
              DWORD dwDesiredAccess,
              BOOL  bInheritHandle,
              DWORD dwProcessId
            );

            :param pid: The PID of the process to create a handle for. If None, uses the current process.
            :return: the handle of the process
            """
            if pid is None:
                return self.current_process

            if pid in self.child_handles:
                return self.child_handles[pid]

            PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
            handle = cast(wintypes.HANDLE, windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid))
            if handle == 0:
                raise self.get_error('OpenProcess')
            self.child_handles[pid] = handle
            return handle

        def get_process_memory_info(self, pid: Optional[int] = None) -> PROCESS_MEMORY_COUNTERS_EX:
            """
            Get process memory info wrapper for the Win32 GetProcessMemoryInfo function.

            BOOL GetProcessMemoryInfo(
              HANDLE                   Process,
              PPROCESS_MEMORY_COUNTERS ppsmemCounters,
              DWORD                    cb
            );

            :param pid: ID of the process we want to get memory usage for. If None, gets usage for current process.
            :return: a PROCESS_MEMORY_COUNTERS_EX struct
            """
            handle = self.open_process(pid)
            pmc = PROCESS_MEMORY_COUNTERS_EX()
            success = windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), ctypes.sizeof(pmc))
            if success == 0:
                raise self.get_error('GetProcessMemoryInfo')
            return pmc

        def assign_process_to_job_object(self, job: wintypes.HANDLE, pid: Optional[int] = None) -> None:
            """
            Assign process to job object wrapper for the Win32 AssignProcessToJobObject function.

            BOOL WINAPI AssignProcessToJobObject(
              _In_ HANDLE hJob,
              _In_ HANDLE hProcess
            );
            :param job: Handle to the job object we want to assign to.
            :param pid: ID of the process we want to assign to the job. If None, assigns the current process.
            """
            handle = self.open_process(pid)
            success = windll.kernel32.AssignProcessToJobObject(job, handle)
            if success == 0:
                raise self.get_error('AssignProcessToJobObject')

        def is_process_in_job(self) -> bool:
            """
            Is process in job wrapper for the Win32 IsProcessInJob function.

            BOOL WINAPI IsProcessInJob(
              _In_     HANDLE ProcessHandle,
              _In_opt_ HANDLE JobHandle,
              _Out_    PBOOL  Result
            );

            :return: true if this process is running inside a job, false otherwise
            """
            result = ctypes.c_bool(False)
            success = windll.kernel32.IsProcessInJob(self.current_process, None, ctypes.byref(result))

            if success == 0:
                raise Win32Helper.get_error('IsProcessInJob')

            return result.value

        def query_information_job_object(self,
                                         job: Optional[wintypes.HANDLE],
                                         job_object_info_class: int,
                                         job_info_struct: JobInfoStruct) -> JobInfoStruct:
            """
            Query job object information wrapper for the Win32 QueryInformationJobObject function.

            Queries info for the given job.
            BOOL WINAPI QueryInformationJobObject(
              _In_opt_  HANDLE             hJob,
              _In_      JOBOBJECTINFOCLASS JobObjectInfoClass,
              _Out_     LPVOID             lpJobObjectInfo,
              _In_      DWORD              cbJobObjectInfoLength,
              _Out_opt_ LPDWORD            lpReturnLength
            );

            :param job: the job to query. If None, queries the job for the current process
            :param job_object_info_class: the info class that should be queried
            :param job_info_struct: a struct to pass to the query
            :return: a struct with the job info, type depends on which info class is specified
            """
            out_size = wintypes.DWORD()

            success = windll.kernel32.QueryInformationJobObject(job,
                                                                job_object_info_class,
                                                                ctypes.byref(job_info_struct),
                                                                ctypes.sizeof(job_info_struct),
                                                                ctypes.byref(out_size))
            if success == 0:
                raise self.get_error('QueryInformationJobObject')
            return job_info_struct

        def get_process_times(self, pid: Optional[int] = None) -> Tuple[float, float, float, float]:
            """
            Get process time wrapper for the Win32 GetProcessTimes function.

            Retrieves timing information for the specified process.
            Note: The Win32 API returns times in 100ns increments, but this function converts to seconds.
            BOOL GetProcessTimes(
              HANDLE     hProcess,
              LPFILETIME lpCreationTime,
              LPFILETIME lpExitTime,
              LPFILETIME lpKernelTime,
              LPFILETIME lpUserTime
            );

            :param pid: The PID of the process to get timing information for. If None, gets info for this process.
            :return: a tuple of ints containing (creation time, exit time, kernel time, user time) in seconds
            """
            handle = self.open_process(pid)

            creation_time = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel_time = wintypes.FILETIME()
            user_time = wintypes.FILETIME()

            success = windll.kernel32.GetProcessTimes(handle,
                                                      ctypes.byref(creation_time),
                                                      ctypes.byref(exit_time),
                                                      ctypes.byref(kernel_time),
                                                      ctypes.byref(user_time))
            if success == 0:
                raise self.get_error('GetProcessTimes')

            def ft_to_sec(ft):
                total = ft.dwHighDateTime << 32
                total += ft.dwLowDateTime
                return total / 10000000

            return ft_to_sec(creation_time), ft_to_sec(exit_time), ft_to_sec(kernel_time), ft_to_sec(user_time)

        def get_current_memory_usage(self) -> Tuple[int, int]:
            """
            Get physical and virtual memory usage of this process.

            :return: a tuple containing [physical memory used, virtual memory used] in bytes
            """
            mem_info = self.get_process_memory_info()
            return mem_info.WorkingSetSize, mem_info.PrivateUsage

        def get_children_memory_usage(self) -> Tuple[int, int]:
            """
            Get physical and virtual memory usage of all of this process's children.

            :return: a tuple containing [physical memory used, virtual memory used] in bytes
            """
            pids = self.get_job_process_list()
            mem_info = [self.get_process_memory_info(pid) for pid in pids if pid != self.current_process]
            physical_mem = 0
            virtual_mem = 0
            for info in mem_info:
                physical_mem += info.WorkingSetSize
                virtual_mem += info.PrivateUsage
            return physical_mem, virtual_mem

        def get_job_accounting_info(self) -> JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION:
            """
            Get basic accounting and I/O accounting information for the job this process is in.

            :return: a JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION struct
            """
            struct = JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION()
            return self.query_information_job_object(self.job_object,
                                                     JobObjectInfoClass.JobObjectBasicAndIoAccountingInformation,
                                                     struct)

        def get_job_process_list(self) -> List[int]:
            """
            Get list of pids of all processes associated with the job this process is in.

            :return: a list of all pids
            """
            max_processes = 100
            while True:
                try:
                    # This must be defined dynamically because the struct is variable length
                    class JobObjectBasicProcessIdListStruct(ctypes.Structure):
                        _fields_ = [('NumberOfAssignedProcesses', wintypes.DWORD),
                                    ('NumberOfProcessIdsInList', wintypes.DWORD),
                                    ('ProcessIdList', wintypes.WPARAM * max_processes)]
                    struct = JobObjectBasicProcessIdListStruct()
                    struct.NumberOfAssignedProcesses = max_processes
                    self.query_information_job_object(self.job_object,
                                                      JobObjectInfoClass.JobObjectBasicProcessIdList,
                                                      struct)
                    break
                except Win32Exception as e:
                    # Win32 error code 234: More data is available
                    if e.win_error_code != 234:
                        raise
                    max_processes *= 2
            return list(struct.ProcessIdList[:struct.NumberOfProcessIdsInList])

        def get_child_process_times(self) -> Tuple[float, float, float, float]:
            """
            Get timing information for all currently running processes in this job, except this one.

            :return: a tuple of ints containing (creation time, exit time, kernel time, user time) in seconds
            """
            pids = self.get_job_process_list()
            timing_info = [self.get_process_times(pid) for pid in pids if pid != self.current_process]
            creation_t = 0.0
            exit_t = 0.0
            kernel_t = 0.0
            user_t = 0.0
            for info in timing_info:
                creation_t += info[0]
                exit_t += info[1]
                kernel_t += info[2]
                user_t += info[3]
            return creation_t, exit_t, kernel_t, user_t

        def set_resource_limits(self,
                                limit_num_processes: Optional[int] = None,
                                limit_cpu_time_seconds: Optional[int] = None,
                                limit_memory_mb: Optional[int] = None) -> None:
            """
            Limit resource usage for the current process and all child processes spawned by this process.

            Call with all values set to None to completely disable resource limiting, even if previously set.

            :return:
            """
            extended_limit_struct = self.query_information_job_object(
                self.job_object,
                JobObjectInfoClass.JobObjectExtendedLimitInformation,
                JOBOBJECT_EXTENDED_LIMIT_INFORMATION())

            if limit_num_processes is not None:
                extended_limit_struct.BasicLimitInformation.LimitFlags |= \
                    JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitActiveProcess
                extended_limit_struct.BasicLimitInformation.ActiveProcessLimit = limit_num_processes
            else:
                extended_limit_struct.BasicLimitInformation.LimitFlags &= \
                    ~JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitActiveProcess

            if limit_cpu_time_seconds is not None:
                extended_limit_struct.BasicLimitInformation.LimitFlags |= \
                    JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitJobTime
                # unit is 100 nanosecond ticks
                extended_limit_struct.BasicLimitInformation.PerJobUserTimeLimit = \
                    limit_cpu_time_seconds * 10 * 1000 * 1000
            else:
                extended_limit_struct.BasicLimitInformation.LimitFlags &= \
                    ~JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitJobTime

            if limit_memory_mb is not None:
                extended_limit_struct.BasicLimitInformation.LimitFlags |= \
                    JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitJobMemory
                # Unit is in bytes
                extended_limit_struct.JobMemoryLimit = limit_memory_mb * 1024 * 1024
            else:
                extended_limit_struct.BasicLimitInformation.LimitFlags &= \
                    ~JOBOBJECT_BASIC_LIMIT_INFORMATION.ValidLimitFlags.LimitJobMemory

            self.set_information_job_object(self.job_object,
                                            JobObjectInfoClass.JobObjectExtendedLimitInformation,
                                            extended_limit_struct)

        @classmethod
        def set_information_job_object(cls,
                                       job: Optional[wintypes.HANDLE],
                                       job_object_info_class: int,
                                       job_info_struct: JobInfoStruct) -> None:
            """
            Set limits for a job object.

            BOOL SetInformationJobObject(
              HANDLE hJob,
              JOBOBJECTINFOCLASS JobObjectInformationClass,
              LPVOID lpJobObjectInformation,
              DWORD cbJobObjectInformationLength
            );

            :param job:
            :param job_object_info_class:
            :param job_info_struct:
            :return:
            """
            success = windll.kernel32.SetInformationJobObject(job,
                                                              job_object_info_class,
                                                              ctypes.byref(job_info_struct),
                                                              ctypes.sizeof(job_info_struct))
            if success == 0:
                raise cls.get_error('SetInformationJobObject')

        def get_resource_usage(self) -> Tuple[int, int, float, float, int, int, float, float]:
            """
            Get resource usage for both this process and all child processes in this job.

            :return: a tuple with the following values:
                - parent physical memory usage
                - parent virtual memory usage
                - parent kernel CPU time
                - parent user CPU time
                - child physical memory usage
                - child virtual memory usage
                - child kernel CPU time
                - child user CPU time
            """
            process_creation, process_exit, process_kernel, process_user = self.get_process_times()
            job_info = self.get_job_accounting_info()
            child_kernel = (job_info.BasicInfo.TotalKernelTime / 10000000) - process_kernel
            child_user = (job_info.BasicInfo.TotalUserTime / 10000000) - process_user

            process_phys_mem, process_virt_mem = self.get_current_memory_usage()
            child_phys_mem, child_virt_mem = self.get_children_memory_usage()

            return process_phys_mem, process_virt_mem, process_kernel, process_user, child_phys_mem, child_virt_mem, \
                child_kernel, child_user

        @staticmethod
        def get_all_ram() -> int:
            """
            Retrieve amount of installed RAM in bytes.

            :returns: The amount of memory in bytes.
            """
            kernel32 = ctypes.windll.kernel32
            memoryStatus = MEMORYSTATUSEX()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
            return cast(int, memoryStatus.ullTotalPhys)

        @staticmethod
        def get_available_physical_memory() -> int:
            """
            Retrieve the amount of physical memory available.

            :return: The amount of physical memory in bytes.
            """
            kernel32 = ctypes.windll.kernel32
            memoryStatus = MEMORYSTATUSEX()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
            return cast(int, memoryStatus.ullAvailPhys)

        @staticmethod
        def get_error(api_name: str) -> Win32Exception:
            """
            Retrieve and format the last error generated by a Win32 API call.

            :param api_name: Name of the API call that triggered the error
            :return: RuntimeError with a formatted message describing the error
            """
            return Win32Exception(api_name, ctypes.GetLastError())
else:
    class _Win32Helper:
        """Stub class that does nothing. Only used on non-Windows platforms."""

        def __getattr__(self, key: str) -> Any:
            """Raise an error."""
            raise OSError('Using this class is not supported on non-Windows platforms')

Win32Helper = _Win32Helper()
