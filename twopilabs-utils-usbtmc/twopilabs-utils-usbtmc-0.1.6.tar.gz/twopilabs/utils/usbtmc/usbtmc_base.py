# Large portions taken from https://github.com/python-ivi/python-usbtmc/blob/master/usbtmc/usbtmc.py

from typing import *
from enum import Enum, Flag
import struct
import io

class UsbTmcBase(io.RawIOBase):
    USBTMC_INTERFACE_CLASS                      = 0xFE
    USBTMC_INTERFACE_SUBCLASS                   = 3
    USBTMC_INTERFACE_PROTOCOL                   = 0
    USB488_INTERFACE_PROTOCOL                   = 1

    DEFAULT_TIMEOUT_MS                          = 5000
    DEFAULT_BTAG                                = 1
    DEFAULT_TRANSFER_SIZE_MAX                   = 1024 * 1024
    DEFAULT_TERM_CHAR                           = '\n'.encode('ascii')

    class RequestStatus(Enum):
        USBTMC_STATUS_SUCCESS                   = 0x01
        USBTMC_STATUS_PENDING                   = 0x02
        USBTMC_STATUS_FAILED                    = 0x80
        USBTMC_STATUS_TRANSFER_NOT_IN_PROGRESS  = 0x81
        USBTMC_STATUS_SPLIT_NOT_IN_PROGRESS     = 0x82
        USBTMC_STATUS_SPLIT_IN_PROGRESS         = 0x83
        USB488_STATUS_INTERRUPT_IN_BUSY         = 0x20

    class RequestValue(Enum):
        USBTMC_REQUEST_INITIATE_ABORT_BULK_OUT     = 1
        USBTMC_REQUEST_CHECK_ABORT_BULK_OUT_STATUS = 2
        USBTMC_REQUEST_INITIATE_ABORT_BULK_IN      = 3
        USBTMC_REQUEST_CHECK_ABORT_BULK_IN_STATUS  = 4
        USBTMC_REQUEST_INITIATE_CLEAR           = 5
        USBTMC_REQUEST_CHECK_CLEAR_STATUS       = 6
        USBTMC_REQUEST_GET_CAPABILITIES         = 7
        USBTMC_REQUEST_INDICATOR_PULSE          = 64
        USB488_READ_STATUS_BYTE                 = 128
        USB488_REN_CONTROL                      = 160
        USB488_GOTO_LOCAL                       = 161
        USB488_LOCAL_LOCKOUT                    = 162

    class TransferMsgId(Enum):
        USBTMC_MSGID_DEV_DEP_MSG_OUT            = 1
        USBTMC_MSGID_REQUEST_DEV_DEP_MSG_IN     = 2
        USBTMC_MSGID_DEV_DEP_MSG_IN             = 2
        USBTMC_MSGID_VENDOR_SPECIFIC_OUT        = 126
        USBTMC_MSGID_REQUEST_VENDOR_SPECIFIC_IN = 127
        USBTMC_MSGID_VENDOR_SPECIFIC_IN         = 127
        USB488_MSGID_TRIGGER                    = 128
    
    class TransferAttrs(Flag):
        USBTMC_TRANSFERATTR_NONE                = 0x00
        USBTMC_TRANSFERATTR_EOM                 = 0x01
        USBTMC_TRANSFERATTR_TERM_CHAR           = 0x02
        
    class TransferHeader(NamedTuple):
        message_id: 'UsbTmcBase.TransferMsgId'
        btag: int
        transfer_size: Optional[int] = 0
        transfer_attrs: Optional['UsbTmcBase.TransferAttrs'] = None
        term_char: Optional[bytes] = None
        
        @classmethod
        def struct(cls) -> struct.Struct:
            # Return a Python struct object for parsing the binary header into the named tuple
            return struct.Struct('<BBBxLBBxx')

        @classmethod
        def size(cls) -> int:
            return cls.struct().size

        @classmethod
        def unpack(cls, buffer: bytes) -> 'UsbTmcBase.TransferHeader':
            fields = cls.struct().unpack(buffer[0:cls.struct().size])
            return cls(
                message_id      = fields[0],
                btag            = fields[1],
                transfer_size   = fields[3],
                transfer_attrs  = UsbTmcBase.TransferAttrs(fields[4]),
                term_char       = fields[5]
            )
            
        def pack(self) -> bytes:
            return self.struct().pack(
                self.message_id, 
                self.btag, 
                ~self.btag & 0xFF,
                self.transfer_size,
                self.transfer_attrs.value if self.transfer_attrs is not None else 0,
                self.term_char[0] if self.term_char is not None else 0
            )
        
        @property
        def btag_next(self) -> int:
            return (self.btag % 255) + 1
            
    class Capabilities(NamedTuple):
        bcdUSBTMC: int
        support_pulse: bool
        support_talk_only: bool
        support_listen_only: bool
        support_term_char: bool

        bcdUSB488: int
        support_USB488dot2: bool
        support_remote_local: bool
        support_trigger: bool
        support_scpi: bool
        support_SR: bool
        support_RL: bool
        support_DT: bool
        
        @classmethod
        def struct(cls) -> struct.Struct:
            # Return a Python struct object for parsing the binary header into the named tuple
            return struct.Struct('<BxHBBxxxxxxHBBxxxxxxxx')

        @classmethod
        def size(cls) -> int:
            return cls.struct().size
            
        @classmethod
        def unpack(cls, buffer: bytes) -> 'UsbTmcBase.Capabilities':
            fields = cls.struct().unpack(buffer[0:cls.struct().size])
            return cls(
                # USBTMC interface capabilities
                bcdUSBTMC           = fields[1],
                support_pulse       = fields[2] & (1<<2) != 0,
                support_talk_only   = fields[2] & (1<<1) != 0,
                support_listen_only = fields[2] & (1<<0) != 0,
                
                # USBTMC device capabilities
                support_term_char   = fields[3] & (1<<0) != 0,

                # USB488 interface capabilities
                bcdUSB488           = fields[4],
                support_USB488dot2  = fields[5] & (1<<2) != 0,
                support_remote_local= fields[5] & (1<<1) != 0,
                support_trigger     = fields[5] & (1<<0) != 0,
                
                # USB488 device capabilities
                support_scpi        = fields[6] & (1<<3) != 0,
                support_SR          = fields[6] & (1<<2) != 0,
                support_RL          = fields[6] & (1<<1) != 0,
                support_DT          = fields[6] & (1<<0) != 0
            )
      
    def aligned_length(length: int) -> int:
        # round towards next multiple of 4 bytes
        return (length + 3) & 0xFFFFFFFC
            
    def __init__(self, *args, **kwargs):
        pass
        
    def readlines(self, hint: int = ...) -> List[AnyStr]:
        # Don't support reading until EOF
        raise io.UnsupportedOperation
        
    def isatty(self) -> bool:
        # Report as interactive
        return True
    
    def fileno(self) -> int:
        # Dont support a file object from OS
        raise OSError()

    def flush(self) -> None:
        # Flush is a NOP
        pass

    def readable(self) -> bool:
        # Stream is readable
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        # No seeking supported
        raise io.UnsupportedOperation

    def seekable(self) -> bool:
        # No seeking supported
        return False

    def tell(self) -> int:
        # No seeking supported
        raise OSError()

    def truncate(self, size: Optional[int] = ...) -> int:
        # No seeking supported
        raise OSError()

    def writable(self) -> bool:
        # Stream is writeable
        return True

    def __next__(self) -> AnyStr:
        # Don't support iterating over lines
        raise io.UnsupportedOperation

    def __iter__(self) -> Iterator[AnyStr]:
        # Don't support iterating over lines
        raise io.UnsupportedOperation

    def readall(self) -> bytes:
        # Don't support reading until EOF    
        raise io.UnsupportedOperation
