# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

from enum import IntEnum


class ErrCode(IntEnum):
    """
    Error codes for the fura module
    """
    NoError         = 0
    UnexpectedError = 2

    UserNotFound     = 100
    UserDisabled     = 101
    UserDeleted      = 102
    UserSuspended    = 103
    UserExpired      = 104
    UserHasNoRole    = 105
    USER_MAX_ERROR   = 199

    SiteNotFound     = 200
    SiteDisabled     = 201
    SITE_MAX_ERROR   = 299

    RoleNotFound     = 300
    RoleDisabled     = 301
    ROLE_MAX_ERROR   = 399

    FuncNotfound     = 400
    FUNC_MAX_ERROR   = 499

    AccessDenied     = 500
    AccReqEaTok      = 501
    AccessExpired    = 502
    ACCESS_MAX_ERROR = 599

    EaTokNotFound    = 600
    EaTokExpired     = 601
    EaTokMaxUses     = 602
    EaTokWrongFunc   = 603
    EaTokWrongUser   = 604
    EAKTOK_MAX_ERROR = 699

    AuthInvalid      = 700
    AuthEmpty        = 701
    AuthNotFound     = 702
    AuthWrongType    = 703
    AuthMaxFailures  = 704
    AuthNotLoggedIn  = 705
    AuthOTPNotFound  = 720
    AuthOTPUsed      = 721
    AuthOTPExpired   = 722
    AuthOTPInvlalid  = 723
    AuthOTPTarget    = 724
    AuthOTPTMaxFails = 725
    AuthOTPTMethod   = 726
    AUTH_MAX_ERROR   = 799

    TokenInvalid     = 800
    TokenTooMany     = 801
    TokenExpired     = 802
    TOKEN_MAX_ERROR  = 899
