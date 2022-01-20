class ILError(Exception):
    """IngeniaLink generic error."""
    pass


class ILConfigurationError(ILError):
    """IngeniaLink IPB protocol configuration error."""
    pass


class ILUDPException(Exception):
    """Ingenialink exception on UDP action."""
    pass


class ILFirmwareLoadError(ILError):
    """IngeniaLink error while loading a firmware."""
    pass


class ILCreationError(ILError):
    """IngeniaLink creation error."""
    pass


class ILValueError(ILError):
    """IngeniaLink value error."""
    pass


class ILTimeoutError(ILError):
    """IngeniaLink timeout error."""
    pass


class ILAlreadyInitializedError(ILError):
    """IngeniaLink already initialized error."""
    pass


class ILMemoryError(ILError):
    """IngeniaLink memory error."""
    pass


class ILDisconnectionError(ILError):
    """IngeniaLink disconnection error."""
    pass


class ILAccessError(ILError):
    """IngeniaLink access error."""
    pass


class ILStateError(ILError):
    """IngeniaLink state error."""
    pass


class ILIOError(ILError):
    """IngeniaLink I/O error."""
    pass


class ILNotSupportedError(ILError):
    """IngeniaLink Not supported error."""
    pass


class ILWrongRegisterError(ILError):
    """IngeniaLink Wrong register error."""
    pass


class ILRegisterNotFoundError(ILError):
    """IngeniaLink register not found in dictionary."""
    pass


class ILWrongCRCError(ILError):
    """IngeniaLink Wrong CRC error."""
    pass


class ILNACKError(ILError):
    """IngeniaLink NACK error."""


# Configuration error
class ILIncorrectAccessType(ILConfigurationError):
    """Incorrect access type configuration error."""
    pass


class ILObjectNotExist(ILConfigurationError):
    """Object doesn't exist configuration error."""
    pass


class ILObjectNotCyclicMappable(ILConfigurationError):
    """Object isn't cyclic mappable as requested configuration error."""
    pass


class ILCyclicMappingTooLarge(ILConfigurationError):
    """Cyclic mapping is too large configuration error."""
    pass


class ILWrongCyclicKey(ILConfigurationError):
    """Cyclic mapping key is wrong configuration error."""
    pass


class ILWrongCyclicRegisterSize(ILConfigurationError):
    """Mapped cyclic register size is wrong configuration error."""
    pass


class ILCommunicationStateUnreachable(ILConfigurationError):
    """Communication state is unreachable configuration error."""
    pass


class ILCommunicationNotModifiable(ILConfigurationError):
    """Communication setting is not modifiable in the
    current state configuration"""
    pass


class ILUnsupportedRegisterValue(ILConfigurationError):
    """Unsupported value introduced in register configuration error."""
    pass


class ILInvalidCommand(ILConfigurationError):
    """Invalid command configuration error."""
    pass


class ILCRCError(ILConfigurationError):
    """CRC error configuration error."""
    pass


class ILUnsupportedSynchronization(ILConfigurationError):
    """Unsupported synchronization method configuration error."""
    pass


class ILActiveFeedbacksHigherThanAllowed(ILConfigurationError):
    """Number of active feedbacks is higher than allowed configuration error."""
    pass


class ILCOMKITTimeout(ILConfigurationError):
    """COMKIT Timeout. CORE device is not properly connected configuration error."""
    pass
