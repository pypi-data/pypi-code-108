# Power Drive System
# Controlword common bits.
IL_MC_CW_SO = (1 << 0)
IL_MC_CW_EV = (1 << 1)
IL_MC_CW_QS = (1 << 2)
IL_MC_CW_EO = (1 << 3)
IL_MC_CW_FR = (1 << 7)
IL_MC_CW_H = (1 << 8)
# Statusword common bits.
IL_MC_SW_RTSO = (1 << 0)
IL_MC_SW_SO = (1 << 1)
IL_MC_SW_OE = (1 << 2)
IL_MC_SW_F = (1 << 3)
IL_MC_SW_VE = (1 << 4)
IL_MC_SW_QS = (1 << 5)
IL_MC_SW_SOD = (1 << 6)
IL_MC_SW_W = (1 << 7)
IL_MC_SW_RM = (1 << 9)
IL_MC_SW_TR = (1 << 10)
IL_MC_SW_ILA = (1 << 11)
IL_MC_SW_IANGLE = (1 << 14)

# PDS FSA states
# Masks for PDS FSA states
IL_MC_PDS_STA_NRTSO_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_SOD)
IL_MC_PDS_STA_SOD_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_SOD)
IL_MC_PDS_STA_RTSO_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_QS
     | IL_MC_SW_SOD)
IL_MC_PDS_STA_SO_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_QS
     | IL_MC_SW_SOD)
IL_MC_PDS_STA_OE_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_QS
     | IL_MC_SW_SOD)
IL_MC_PDS_STA_QSA_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_QS
     | IL_MC_SW_SOD)
IL_MC_PDS_STA_FRA_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_SOD)
IL_MC_PDS_STA_F_MSK = \
    (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F | IL_MC_SW_SOD)
# Not ready to switch on.
IL_MC_PDS_STA_NRTSO = 0x0000
# Switch on disabled.
IL_MC_PDS_STA_SOD = IL_MC_SW_SOD
# Ready to switch on.
IL_MC_PDS_STA_RTSO = (IL_MC_SW_RTSO | IL_MC_SW_QS)
# Switched on.
IL_MC_PDS_STA_SO = (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_QS)
# Operation enabled.
IL_MC_PDS_STA_OE = (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_QS)
# Quick stop active.
IL_MC_PDS_STA_QSA = (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE)
# Fault reaction active.
IL_MC_PDS_STA_FRA = (IL_MC_SW_RTSO | IL_MC_SW_SO | IL_MC_SW_OE | IL_MC_SW_F)
# Fault.
IL_MC_PDS_STA_F = IL_MC_SW_F
# Unknown.
IL_MC_PDS_STA_UNKNOWN = 0xFFFF

# PDS FSA commands
# Shutdown.
IL_MC_PDS_CMD_SD = (IL_MC_CW_EV | IL_MC_CW_QS)
# Switch on.
IL_MC_PDS_CMD_SO = (IL_MC_CW_SO | IL_MC_CW_EV | IL_MC_CW_QS)
# Switch on + enable operation.
IL_MC_PDS_CMD_SOEO = (IL_MC_CW_SO | IL_MC_CW_EV | IL_MC_CW_QS | IL_MC_CW_EO)
# Disable voltage.
IL_MC_PDS_CMD_DV = 0x0000
# Quick stop.
IL_MC_PDS_CMD_QS = IL_MC_CW_EV
# Disable operation.
IL_MC_PDS_CMD_DO = (IL_MC_CW_SO | IL_MC_CW_EV | IL_MC_CW_QS)
# Enable operation.
IL_MC_PDS_CMD_EO = (IL_MC_CW_SO | IL_MC_CW_EV | IL_MC_CW_QS | IL_MC_CW_EO)
# Fault reset.
IL_MC_PDS_CMD_FR = IL_MC_CW_FR
# Unknown command.
IL_MC_PDS_CMD_UNKNOWN = 0xFFFF

# Homing controlword bits
# Homing operation start
IL_MC_HOMING_CW_START = (1 << 4)
# Halt
IL_MC_HOMING_CW_HALT = (1 << 8)
# Homing statusword bits
# Homing attained.
IL_MC_HOMING_SW_ATT = (1 << 12)
# Homing error.
IL_MC_HOMING_SW_ERR = (1 << 13)
# Homing states
# Homing state mask.
IL_MC_HOMING_STA_MSK = (IL_MC_SW_TR | IL_MC_HOMING_SW_ATT |
                        IL_MC_HOMING_SW_ERR)
# Homing procedure is in progress.
IL_MC_HOMING_STA_INPROG = 0x0000
# Homing procedure is interrupted or not started.
IL_MC_HOMING_STA_INT = (IL_MC_SW_TR)
# Homing is attained, but target is not reached.
IL_MC_HOMING_STA_ATT = (IL_MC_HOMING_SW_ATT)
# Homing procedure is completed successfully.
IL_MC_HOMING_STA_SUCCESS = (IL_MC_SW_TR | IL_MC_HOMING_SW_ATT)
# Homing error occurred, velocity not zero.
IL_MC_HOMING_STA_ERR_VNZ = (IL_MC_HOMING_SW_ERR)
# Homing error ocurred, velocity is zero.
IL_MC_HOMING_STA_ERR_VZ = (IL_MC_SW_TR | IL_MC_HOMING_SW_ERR)

# Profile Position
# Profile position controlword bits
# New set-point.
IL_MC_PP_CW_NEWSP = (1 << 4)
# Change set immediately
IL_MC_PP_CW_IMMEDIATE = (1 << 5)
# Target position is relative.
IL_MC_PP_CW_REL = (1 << 6)
# Profile position specific statusword bits
# Set-point acknowledge.
IL_MC_PP_SW_SPACK = (1 << 12)
# Following error.
IL_MC_PP_SW_FOLLOWERR = (1 << 13)

# PDS
# Flags position offset in statusword.
FLAGS_SW_POS = 10
# Number of retries to reset fault state
FAULT_RESET_RETRIES = 20

# General failure. */
IL_EFAIL = -1
# Invalid values. */
IL_EINVAL = -2
# Operation timed out. */
IL_ETIMEDOUT = -3
# Not enough memory. */
IL_ENOMEM = -4
# Already initialized. */
IL_EALREADY = -5
# Device disconnected. */
IL_EDISCONN = -6
# Access error. */
IL_EACCESS = -7
# State error. */
IL_ESTATE = -8
# I/O error. */
IL_EIO = -9
# Not supported. */
IL_ENOTSUP = -10
