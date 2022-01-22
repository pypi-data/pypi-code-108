from enum import Enum


class CWE(Enum):
    """Common Weakness Enumeration."""

    def __init__(self, code: int, summary: str) -> None:
        self.code = code
        self.summary = summary

    ID_15 = 15, "External Control of System or Configuration Setting"
    ID_23 = 23, "Relative Path Traversal"
    ID_36 = 36, "Absolute Path Traversal"
    ID_41 = 41, "Improper Resolution of Path Equivalence"
    ID_59 = 59, "Improper Link Resolution Before File Access ('Link Following')"
    ID_66 = 66, "Improper Handling of File Names that Identify Virtual Resources"
    ID_73 = 73, "External Control of File Name or Path"
    ID_76 = 76, "Improper Neutralization of Equivalent Special Elements"
    ID_78 = (
        78,
        "Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
    )
    ID_79 = (
        79,
        "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
    )
    ID_88 = (
        88,
        "Improper Neutralization of Argument Delimiters in a Command ('Argument Injection')",
    )
    ID_89 = (
        89,
        "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
    )
    ID_90 = (
        90,
        "Improper Neutralization of Special Elements used in an LDAP Query ('LDAP Injection')",
    )
    ID_91 = 91, "XML Injection (aka Blind XPath Injection)"
    ID_93 = 93, "Improper Neutralization of CRLF Sequences ('CRLF Injection')"
    ID_94 = 94, "Improper Control of Generation of Code ('Code Injection')"
    ID_96 = (
        96,
        "Improper Neutralization of Directives in Statically Saved Code ('Static Code Injection')",
    )
    ID_112 = 112, "Missing XML Validation"
    ID_115 = 115, "Misinterpretation of Input"
    ID_117 = 117, "Improper Output Neutralization for Logs"
    ID_120 = (
        120,
        "Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')",
    )
    ID_123 = 123, "Write-what-where Condition"
    ID_124 = 124, "Buffer Underwrite ('Buffer Underflow')"
    ID_125 = 125, "Out-of-bounds Read"
    ID_128 = 128, "Wrap-around Error"
    ID_129 = 129, "Improper Validation of Array Index"
    ID_130 = 130, "Improper Handling of Length Parameter Inconsistency"
    ID_131 = 131, "Incorrect Calculation of Buffer Size"
    ID_134 = 134, "Use of Externally-Controlled Format String"
    ID_135 = 135, "Incorrect Calculation of Multi-Byte String Length"
    ID_140 = 140, "Improper Neutralization of Delimiters"
    ID_166 = 166, "Improper Handling of Missing Special Element"
    ID_167 = 167, "Improper Handling of Additional Special Element"
    ID_168 = 168, "Improper Handling of Inconsistent Special Elements"
    ID_170 = 170, "Improper Null Termination"
    ID_178 = 178, "Improper Handling of Case Sensitivity"
    ID_179 = 179, "Incorrect Behavior Order: Early Validation"
    ID_182 = 182, "Collapse of Data into Unsafe Value"
    ID_183 = 183, "Permissive List of Allowed Inputs"
    ID_184 = 184, "Incomplete List of Disallowed Inputs"
    ID_186 = 186, "Overly Restrictive Regular Expression"
    ID_188 = 188, "Reliance on Data/Memory Layout"
    ID_190 = 190, "Integer Overflow or Wraparound"
    ID_191 = 191, "Integer Underflow (Wrap or Wraparound)"
    ID_192 = 192, "Integer Coercion Error"
    ID_193 = 193, "Off-by-one Error"
    ID_197 = 197, "Numeric Truncation Error"
    ID_198 = 198, "Use of Incorrect Byte Ordering"
    ID_201 = 201, "Insertion of Sensitive Information Into Sent Data"
    ID_204 = 204, "Observable Response Discrepancy"
    ID_205 = 205, "Observable Behavioral Discrepancy"
    ID_208 = 208, "Observable Timing Discrepancy"
    ID_209 = 209, "Generation of Error Message Containing Sensitive Information"
    ID_212 = 212, "Improper Removal of Sensitive Information Before Storage or Transfer"
    ID_213 = 213, "Exposure of Sensitive Information Due to Incompatible Policies"
    ID_214 = 214, "Invocation of Process Using Visible Sensitive Information"
    ID_215 = 215, "Insertion of Sensitive Information Into Debugging Code"
    ID_222 = 222, "Truncation of Security-relevant Information"
    ID_223 = 223, "Omission of Security-relevant Information"
    ID_224 = 224, "Obscured Security-relevant Information by Alternate Name"
    ID_226 = 226, "Sensitive Information in Resource Not Removed Before Reuse"
    ID_229 = 229, "Improper Handling of Values"
    ID_233 = 233, "Improper Handling of Parameters"
    ID_237 = 237, "Improper Handling of Structural Elements"
    ID_241 = 241, "Improper Handling of Unexpected Data Type"
    ID_242 = 242, "Use of Inherently Dangerous Function"
    ID_243 = 243, "Creation of chroot Jail Without Changing Working Directory"
    ID_248 = 248, "Uncaught Exception"
    ID_250 = 250, "Execution with Unnecessary Privileges"
    ID_252 = 252, "Unchecked Return Value"
    ID_253 = 253, "Incorrect Check of Function Return Value"
    ID_256 = 256, "Plaintext Storage of a Password"
    ID_257 = 257, "Storing Passwords in a Recoverable Format"
    ID_260 = 260, "Password in Configuration File"
    ID_261 = 261, "Weak Encoding for Password"
    ID_262 = 262, "Not Using Password Aging"
    ID_263 = 263, "Password Aging with Long Expiration"
    ID_266 = 266, "Incorrect Privilege Assignment"
    ID_267 = 267, "Privilege Defined With Unsafe Actions"
    ID_268 = 268, "Privilege Chaining"
    ID_270 = 270, "Privilege Context Switching Error"
    ID_272 = 272, "Least Privilege Violation"
    ID_273 = 273, "Improper Check for Dropped Privileges"
    ID_274 = 274, "Improper Handling of Insufficient Privileges"
    ID_276 = 276, "Incorrect Default Permissions"
    ID_277 = 277, "Insecure Inherited Permissions"
    ID_278 = 278, "Insecure Preserved Inherited Permissions"
    ID_279 = 279, "Incorrect Execution-Assigned Permissions"
    ID_280 = 280, "Improper Handling of Insufficient Permissions or Privileges "
    ID_281 = 281, "Improper Preservation of Permissions"
    ID_283 = 283, "Unverified Ownership"
    ID_288 = 288, "Authentication Bypass Using an Alternate Path or Channel"
    ID_290 = 290, "Authentication Bypass by Spoofing"
    ID_294 = 294, "Authentication Bypass by Capture-replay"
    ID_295 = 295, "Improper Certificate Validation"
    ID_296 = 296, "Improper Following of a Certificate's Chain of Trust"
    ID_299 = 299, "Improper Check for Certificate Revocation"
    ID_303 = 303, "Incorrect Implementation of Authentication Algorithm"
    ID_304 = 304, "Missing Critical Step in Authentication"
    ID_305 = 305, "Authentication Bypass by Primary Weakness"
    ID_306 = 306, "Missing Authentication for Critical Function"
    ID_307 = 307, "Improper Restriction of Excessive Authentication Attempts"
    ID_308 = 308, "Use of Single-factor Authentication"
    ID_309 = 309, "Use of Password System for Primary Authentication"
    ID_312 = 312, "Cleartext Storage of Sensitive Information"
    ID_317 = 317, "Cleartext Storage of Sensitive Information in GUI"
    ID_319 = 319, "Cleartext Transmission of Sensitive Information"
    ID_321 = 321, "Use of Hard-coded Cryptographic Key"
    ID_322 = 322, "Key Exchange without Entity Authentication"
    ID_323 = 323, "Reusing a Nonce, Key Pair in Encryption"
    ID_324 = 324, "Use of a Key Past its Expiration Date"
    ID_325 = 325, "Missing Cryptographic Step"
    ID_328 = 328, "Use of Weak Hash"
    ID_331 = 331, "Insufficient Entropy"
    ID_334 = 334, "Small Space of Random Values"
    ID_335 = 335, "Incorrect Usage of Seeds in Pseudo-Random Number Generator (PRNG)"
    ID_338 = 338, "Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG)"
    ID_341 = 341, "Predictable from Observable State"
    ID_342 = 342, "Predictable Exact Value from Previous Values"
    ID_343 = 343, "Predictable Value Range from Previous Values"
    ID_346 = 346, "Origin Validation Error"
    ID_347 = 347, "Improper Verification of Cryptographic Signature"
    ID_348 = 348, "Use of Less Trusted Source"
    ID_349 = 349, "Acceptance of Extraneous Untrusted Data With Trusted Data"
    ID_351 = 351, "Insufficient Type Distinction"
    ID_353 = 353, "Missing Support for Integrity Check"
    ID_354 = 354, "Improper Validation of Integrity Check Value"
    ID_356 = 356, "Product UI does not Warn User of Unsafe Actions"
    ID_357 = 357, "Insufficient UI Warning of Dangerous Operations"
    ID_359 = 359, "Exposure of Private Personal Information to an Unauthorized Actor"
    ID_363 = 363, "Race Condition Enabling Link Following"
    ID_364 = 364, "Signal Handler Race Condition"
    ID_365 = 365, "Race Condition in Switch"
    ID_366 = 366, "Race Condition within a Thread"
    ID_367 = 367, "Time-of-check Time-of-use (TOCTOU) Race Condition"
    ID_368 = 368, "Context Switching Race Condition"
    ID_369 = 369, "Divide By Zero"
    ID_372 = 372, "Incomplete Internal State Distinction"
    ID_374 = 374, "Passing Mutable Objects to an Untrusted Method"
    ID_375 = 375, "Returning a Mutable Object to an Untrusted Caller"
    ID_378 = 378, "Creation of Temporary File With Insecure Permissions"
    ID_379 = 379, "Creation of Temporary File in Directory with Insecure Permissions"
    ID_385 = 385, "Covert Timing Channel"
    ID_386 = 386, "Symbolic Name not Mapping to Correct Object"
    ID_390 = 390, "Detection of Error Condition Without Action"
    ID_391 = 391, "Unchecked Error Condition"
    ID_392 = 392, "Missing Report of Error Condition"
    ID_393 = 393, "Return of Wrong Status Code"
    ID_394 = 394, "Unexpected Status Code or Return Value"
    ID_395 = 395, "Use of NullPointerException Catch to Detect NULL Pointer Dereference"
    ID_396 = 396, "Declaration of Catch for Generic Exception"
    ID_397 = 397, "Declaration of Throws for Generic Exception"
    ID_403 = (
        403,
        "Exposure of File Descriptor to Unintended Control Sphere ('File Descriptor Leak')",
    )
    ID_408 = 408, "Incorrect Behavior Order: Early Amplification"
    ID_409 = 409, "Improper Handling of Highly Compressed Data (Data Amplification)"
    ID_410 = 410, "Insufficient Resource Pool"
    ID_412 = 412, "Unrestricted Externally Accessible Lock"
    ID_413 = 413, "Improper Resource Locking"
    ID_414 = 414, "Missing Lock Check"
    ID_419 = 419, "Unprotected Primary Channel"
    ID_420 = 420, "Unprotected Alternate Channel"
    ID_421 = 421, "Race Condition During Access to Alternate Channel"
    ID_425 = 425, "Direct Request ('Forced Browsing')"
    ID_426 = 426, "Untrusted Search Path"
    ID_427 = 427, "Uncontrolled Search Path Element"
    ID_428 = 428, "Unquoted Search Path or Element"
    ID_430 = 430, "Deployment of Wrong Handler"
    ID_431 = 431, "Missing Handler"
    ID_432 = 432, "Dangerous Signal Handler not Disabled During Sensitive Operations"
    ID_433 = 433, "Unparsed Raw Web Content Delivery"
    ID_434 = 434, "Unrestricted Upload of File with Dangerous Type"
    ID_437 = 437, "Incomplete Model of Endpoint Features"
    ID_439 = 439, "Behavioral Change in New Version or Environment"
    ID_440 = 440, "Expected Behavior Violation"
    ID_444 = (
        444,
        "Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling')",
    )
    ID_447 = 447, "Unimplemented or Unsupported Feature in UI"
    ID_448 = 448, "Obsolete Feature in UI"
    ID_449 = 449, "The UI Performs the Wrong Action"
    ID_450 = 450, "Multiple Interpretations of UI Input"
    ID_454 = 454, "External Initialization of Trusted Variables or Data Stores"
    ID_455 = 455, "Non-exit on Failed Initialization"
    ID_459 = 459, "Incomplete Cleanup"
    ID_460 = 460, "Improper Cleanup on Thrown Exception"
    ID_462 = 462, "Duplicate Key in Associative List (Alist)"
    ID_463 = 463, "Deletion of Data Structure Sentinel"
    ID_464 = 464, "Addition of Data Structure Sentinel"
    ID_466 = 466, "Return of Pointer Value Outside of Expected Range"
    ID_467 = 467, "Use of sizeof() on a Pointer Type"
    ID_468 = 468, "Incorrect Pointer Scaling"
    ID_469 = 469, "Use of Pointer Subtraction to Determine Size"
    ID_470 = (
        470,
        "Use of Externally-Controlled Input to Select Classes or Code ('Unsafe Reflection')",
    )
    ID_471 = 471, "Modification of Assumed-Immutable Data (MAID)"
    ID_472 = 472, "External Control of Assumed-Immutable Web Parameter"
    ID_474 = 474, "Use of Function with Inconsistent Implementations"
    ID_475 = 475, "Undefined Behavior for Input to API"
    ID_476 = 476, "NULL Pointer Dereference"
    ID_477 = 477, "Use of Obsolete Function"
    ID_478 = 478, "Missing Default Case in Switch Statement"
    ID_479 = 479, "Signal Handler Use of a Non-reentrant Function"
    ID_480 = 480, "Use of Incorrect Operator"
    ID_483 = 483, "Incorrect Block Delimitation"
    ID_484 = 484, "Omitted Break Statement in Switch"
    ID_487 = 487, "Reliance on Package-level Scope"
    ID_488 = 488, "Exposure of Data Element to Wrong Session"
    ID_489 = 489, "Active Debug Code"
    ID_494 = 494, "Download of Code Without Integrity Check"
    ID_497 = (
        497,
        "Exposure of Sensitive System Information to an Unauthorized Control Sphere",
    )
    ID_501 = 501, "Trust Boundary Violation"
    ID_502 = 502, "Deserialization of Untrusted Data"
    ID_515 = 515, "Covert Storage Channel"
    ID_521 = 521, "Weak Password Requirements"
    ID_523 = 523, "Unprotected Transport of Credentials"
    ID_524 = 524, "Use of Cache Containing Sensitive Information"
    ID_532 = 532, "Insertion of Sensitive Information into Log File"
    ID_540 = 540, "Inclusion of Sensitive Information in Source Code"
    ID_544 = 544, "Missing Standardized Error Handling Mechanism"
    ID_546 = 546, "Suspicious Comment"
    ID_547 = 547, "Use of Hard-coded, Security-relevant Constants"
    ID_549 = 549, "Missing Password Field Masking"
    ID_551 = (
        551,
        "Incorrect Behavior Order: Authorization Before Parsing and Canonicalization",
    )
    ID_561 = 561, "Dead Code"
    ID_562 = 562, "Return of Stack Variable Address"
    ID_563 = 563, "Assignment to Variable without Use"
    ID_565 = 565, "Reliance on Cookies without Validation and Integrity Checking"
    ID_567 = 567, "Unsynchronized Access to Shared Data in a Multithreaded Context"
    ID_570 = 570, "Expression is Always False"
    ID_571 = 571, "Expression is Always True"
    ID_580 = 580, "clone() Method Without super.clone()"
    ID_581 = 581, "Object Model Violation: Just One of Equals and Hashcode Defined"
    ID_584 = 584, "Return Inside Finally Block"
    ID_585 = 585, "Empty Synchronized Block"
    ID_586 = 586, "Explicit Call to Finalize()"
    ID_587 = 587, "Assignment of a Fixed Address to a Pointer"
    ID_588 = 588, "Attempt to Access Child of a Non-structure Pointer"
    ID_595 = 595, "Comparison of Object References Instead of Object Contents"
    ID_597 = 597, "Use of Wrong Operator in String Comparison"
    ID_600 = 600, "Uncaught Exception in Servlet "
    ID_601 = 601, "URL Redirection to Untrusted Site ('Open Redirect')"
    ID_603 = 603, "Use of Client-Side Authentication"
    ID_605 = 605, "Multiple Binds to the Same Port"
    ID_606 = 606, "Unchecked Input for Loop Condition"
    ID_609 = 609, "Double-Checked Locking"
    ID_611 = 611, "Improper Restriction of XML External Entity Reference"
    ID_612 = 612, "Improper Authorization of Index Containing Sensitive Information"
    ID_613 = 613, "Insufficient Session Expiration"
    ID_617 = 617, "Reachable Assertion"
    ID_618 = 618, "Exposed Unsafe ActiveX Method"
    ID_619 = 619, "Dangling Database Cursor ('Cursor Injection')"
    ID_620 = 620, "Unverified Password Change"
    ID_621 = 621, "Variable Extraction Error"
    ID_624 = 624, "Executable Regular Expression Error"
    ID_625 = 625, "Permissive Regular Expression"
    ID_627 = 627, "Dynamic Variable Evaluation"
    ID_628 = 628, "Function Call with Incorrectly Specified Arguments"
    ID_639 = 639, "Authorization Bypass Through User-Controlled Key"
    ID_640 = 640, "Weak Password Recovery Mechanism for Forgotten Password"
    ID_641 = 641, "Improper Restriction of Names for Files and Other Resources"
    ID_643 = (
        643,
        "Improper Neutralization of Data within XPath Expressions ('XPath Injection')",
    )
    ID_645 = 645, "Overly Restrictive Account Lockout Mechanism"
    ID_648 = 648, "Incorrect Use of Privileged APIs"
    ID_649 = (
        649,
        "Reliance on Obfuscation or Encryption of Security-Relevant Inputs without Integrity Checking",
    )
    ID_652 = (
        652,
        "Improper Neutralization of Data within XQuery Expressions ('XQuery Injection')",
    )
    ID_663 = 663, "Use of a Non-reentrant Function in a Concurrent Context"
    ID_676 = 676, "Use of Potentially Dangerous Function"
    ID_681 = 681, "Incorrect Conversion between Numeric Types"
    ID_694 = 694, "Use of Multiple Resources with Duplicate Identifier"
    ID_695 = 695, "Use of Low-Level Functionality"
    ID_698 = 698, "Execution After Redirect (EAR)"
    ID_708 = 708, "Incorrect Ownership Assignment"
    ID_733 = (
        733,
        "Compiler Optimization Removal or Modification of Security-critical Code",
    )
    ID_749 = 749, "Exposed Dangerous Method or Function"
    ID_756 = 756, "Missing Custom Error Page"
    ID_763 = 763, "Release of Invalid Pointer or Reference"
    ID_764 = 764, "Multiple Locks of a Critical Resource"
    ID_765 = 765, "Multiple Unlocks of a Critical Resource"
    ID_766 = 766, "Critical Data Element Declared Public"
    ID_767 = 767, "Access to Critical Private Variable via Public Method"
    ID_770 = 770, "Allocation of Resources Without Limits or Throttling"
    ID_771 = 771, "Missing Reference to Active Allocated Resource"
    ID_772 = 772, "Missing Release of Resource after Effective Lifetime"
    ID_776 = (
        776,
        "Improper Restriction of Recursive Entity References in DTDs ('XML Entity Expansion')",
    )
    ID_778 = 778, "Insufficient Logging"
    ID_779 = 779, "Logging of Excessive Data"
    ID_783 = 783, "Operator Precedence Logic Error"
    ID_786 = 786, "Access of Memory Location Before Start of Buffer"
    ID_787 = 787, "Out-of-bounds Write"
    ID_788 = 788, "Access of Memory Location After End of Buffer"
    ID_791 = 791, "Incomplete Filtering of Special Elements"
    ID_795 = 795, "Only Filtering Special Elements at a Specified Location"
    ID_798 = 798, "Use of Hard-coded Credentials"
    ID_804 = 804, "Guessable CAPTCHA"
    ID_805 = 805, "Buffer Access with Incorrect Length Value"
    ID_820 = 820, "Missing Synchronization"
    ID_821 = 821, "Incorrect Synchronization"
    ID_822 = 822, "Untrusted Pointer Dereference"
    ID_823 = 823, "Use of Out-of-range Pointer Offset"
    ID_824 = 824, "Access of Uninitialized Pointer"
    ID_825 = 825, "Expired Pointer Dereference"
    ID_826 = 826, "Premature Release of Resource During Expected Lifetime"
    ID_828 = 828, "Signal Handler with Functionality that is not Asynchronous-Safe"
    ID_829 = 829, "Inclusion of Functionality from Untrusted Control Sphere"
    ID_831 = 831, "Signal Handler Function Associated with Multiple Signals"
    ID_832 = 832, "Unlock of a Resource that is not Locked"
    ID_833 = 833, "Deadlock"
    ID_835 = 835, "Loop with Unreachable Exit Condition ('Infinite Loop')"
    ID_836 = 836, "Use of Password Hash Instead of Password for Authentication"
    ID_837 = 837, "Improper Enforcement of a Single, Unique Action"
    ID_838 = 838, "Inappropriate Encoding for Output Context"
    ID_839 = 839, "Numeric Range Comparison Without Minimum Check"
    ID_841 = 841, "Improper Enforcement of Behavioral Workflow"
    ID_842 = 842, "Placement of User into Incorrect Group"
    ID_843 = 843, "Access of Resource Using Incompatible Type ('Type Confusion')"
    ID_908 = 908, "Use of Uninitialized Resource"
    ID_909 = 909, "Missing Initialization of Resource"
    ID_910 = 910, "Use of Expired File Descriptor"
    ID_911 = 911, "Improper Update of Reference Count"
    ID_914 = 914, "Improper Control of Dynamically-Identified Variables"
    ID_915 = (
        915,
        "Improperly Controlled Modification of Dynamically-Determined Object Attributes",
    )
    ID_916 = 916, "Use of Password Hash With Insufficient Computational Effort"
    ID_917 = (
        917,
        "Improper Neutralization of Special Elements used in an Expression Language Statement ('Expression Language Injection')",
    )
    ID_918 = 918, "Server-Side Request Forgery (SSRF)"
    ID_920 = 920, "Improper Restriction of Power Consumption"
    ID_921 = 921, "Storage of Sensitive Data in a Mechanism without Access Control"
    ID_924 = (
        924,
        "Improper Enforcement of Message Integrity During Transmission in a Communication Channel",
    )
    ID_939 = 939, "Improper Authorization in Handler for Custom URL Scheme"
    ID_940 = 940, "Improper Verification of Source of a Communication Channel"
    ID_941 = 941, "Incorrectly Specified Destination in a Communication Channel"
    ID_1007 = 1007, "Insufficient Visual Distinction of Homoglyphs Presented to User"
    ID_1021 = 1021, "Improper Restriction of Rendered UI Layers or Frames"
    ID_1024 = 1024, "Comparison of Incompatible Types"
    ID_1025 = 1025, "Comparison Using Wrong Factors"
    ID_1037 = (
        1037,
        "Processor Optimization Removal or Modification of Security-critical Code",
    )
    ID_1041 = 1041, "Use of Redundant Code"
    ID_1043 = (
        1043,
        "Data Element Aggregating an Excessively Large Number of Non-Primitive Elements",
    )
    ID_1044 = (
        1044,
        "Architecture with Number of Horizontal Layers Outside of Expected Range",
    )
    ID_1045 = (
        1045,
        "Parent Class with a Virtual Destructor and a Child Class without a Virtual Destructor",
    )
    ID_1046 = 1046, "Creation of Immutable Text Using String Concatenation"
    ID_1047 = 1047, "Modules with Circular Dependencies"
    ID_1048 = 1048, "Invokable Control Element with Large Number of Outward Calls"
    ID_1049 = 1049, "Excessive Data Query Operations in a Large Data Table"
    ID_1050 = 1050, "Excessive Platform Resource Consumption within a Loop"
    ID_1051 = 1051, "Initialization with Hard-Coded Network Resource Configuration Data"
    ID_1052 = 1052, "Excessive Use of Hard-Coded Literals in Initialization"
    ID_1053 = 1053, "Missing Documentation for Design"
    ID_1054 = (
        1054,
        "Invocation of a Control Element at an Unnecessarily Deep Horizontal Layer",
    )
    ID_1055 = 1055, "Multiple Inheritance from Concrete Classes"
    ID_1056 = 1056, "Invokable Control Element with Variadic Parameters"
    ID_1057 = 1057, "Data Access Operations Outside of Expected Data Manager Component"
    ID_1058 = (
        1058,
        "Invokable Control Element in Multi-Thread Context with non-Final Static Storable or Member Element",
    )
    ID_1060 = 1060, "Excessive Number of Inefficient Server-Side Data Accesses"
    ID_1062 = 1062, "Parent Class with References to Child Class"
    ID_1063 = 1063, "Creation of Class Instance within a Static Code Block"
    ID_1064 = (
        1064,
        "Invokable Control Element with Signature Containing an Excessive Number of Parameters",
    )
    ID_1065 = (
        1065,
        "Runtime Resource Management Control Element in a Component Built to Run on Application Servers",
    )
    ID_1066 = 1066, "Missing Serialization Control Element"
    ID_1067 = 1067, "Excessive Execution of Sequential Searches of Data Resource"
    ID_1068 = 1068, "Inconsistency Between Implementation and Documented Design"
    ID_1069 = 1069, "Empty Exception Block"
    ID_1070 = (
        1070,
        "Serializable Data Element Containing non-Serializable Item Elements",
    )
    ID_1071 = 1071, "Empty Code Block"
    ID_1072 = 1072, "Data Resource Access without Use of Connection Pooling"
    ID_1073 = (
        1073,
        "Non-SQL Invokable Control Element with Excessive Number of Data Resource Accesses",
    )
    ID_1074 = 1074, "Class with Excessively Deep Inheritance"
    ID_1075 = 1075, "Unconditional Control Flow Transfer outside of Switch Block"
    ID_1077 = 1077, "Floating Point Comparison with Incorrect Operator"
    ID_1079 = 1079, "Parent Class without Virtual Destructor Method"
    ID_1080 = 1080, "Source Code File with Excessive Number of Lines of Code"
    ID_1082 = 1082, "Class Instance Self Destruction Control Element"
    ID_1083 = 1083, "Data Access from Outside Expected Data Manager Component"
    ID_1084 = (
        1084,
        "Invokable Control Element with Excessive File or Data Access Operations",
    )
    ID_1085 = (
        1085,
        "Invokable Control Element with Excessive Volume of Commented-out Code",
    )
    ID_1086 = 1086, "Class with Excessive Number of Child Classes"
    ID_1087 = 1087, "Class with Virtual Method without a Virtual Destructor"
    ID_1088 = 1088, "Synchronous Access of Remote Resource without Timeout"
    ID_1089 = 1089, "Large Data Table with Excessive Number of Indices"
    ID_1090 = 1090, "Method Containing Access of a Member Element from Another Class"
    ID_1091 = 1091, "Use of Object without Invoking Destructor Method"
    ID_1092 = (
        1092,
        "Use of Same Invokable Control Element in Multiple Architectural Layers",
    )
    ID_1094 = 1094, "Excessive Index Range Scan for a Data Resource"
    ID_1095 = 1095, "Loop Condition Value Update within the Loop"
    ID_1097 = (
        1097,
        "Persistent Storable Data Element without Associated Comparison Control Element",
    )
    ID_1098 = (
        1098,
        "Data Element containing Pointer Item without Proper Copy Control Element",
    )
    ID_1099 = 1099, "Inconsistent Naming Conventions for Identifiers"
    ID_1100 = 1100, "Insufficient Isolation of System-Dependent Functions"
    ID_1101 = 1101, "Reliance on Runtime Component in Generated Code"
    ID_1102 = 1102, "Reliance on Machine-Dependent Data Representation"
    ID_1103 = 1103, "Use of Platform-Dependent Third Party Components"
    ID_1104 = 1104, "Use of Unmaintained Third Party Components"
    ID_1105 = 1105, "Insufficient Encapsulation of Machine-Dependent Functionality"
    ID_1106 = 1106, "Insufficient Use of Symbolic Constants"
    ID_1107 = 1107, "Insufficient Isolation of Symbolic Constant Definitions"
    ID_1108 = 1108, "Excessive Reliance on Global Variables"
    ID_1109 = 1109, "Use of Same Variable for Multiple Purposes"
    ID_1110 = 1110, "Incomplete Design Documentation"
    ID_1111 = 1111, "Incomplete I/O Documentation"
    ID_1112 = 1112, "Incomplete Documentation of Program Execution"
    ID_1113 = 1113, "Inappropriate Comment Style"
    ID_1114 = 1114, "Inappropriate Whitespace Style"
    ID_1115 = 1115, "Source Code Element without Standard Prologue"
    ID_1116 = 1116, "Inaccurate Comments"
    ID_1117 = 1117, "Callable with Insufficient Behavioral Summary"
    ID_1118 = 1118, "Insufficient Documentation of Error Handling Techniques"
    ID_1119 = 1119, "Excessive Use of Unconditional Branching"
    ID_1121 = 1121, "Excessive McCabe Cyclomatic Complexity"
    ID_1122 = 1122, "Excessive Halstead Complexity"
    ID_1123 = 1123, "Excessive Use of Self-Modifying Code"
    ID_1124 = 1124, "Excessively Deep Nesting"
    ID_1125 = 1125, "Excessive Attack Surface"
    ID_1126 = 1126, "Declaration of Variable with Unnecessarily Wide Scope"
    ID_1127 = 1127, "Compilation with Insufficient Warnings or Errors"
    ID_1173 = 1173, "Improper Use of Validation Framework"
    ID_1188 = 1188, "Insecure Default Initialization of Resource"
    ID_1220 = 1220, "Insufficient Granularity of Access Control"
    ID_1230 = 1230, "Exposure of Sensitive Information Through Metadata"
    ID_1235 = (
        1235,
        "Incorrect Use of Autoboxing and Unboxing for Performance Critical Operations",
    )
    ID_1236 = 1236, "Improper Neutralization of Formula Elements in a CSV File"
    ID_1240 = 1240, "Use of a Cryptographic Primitive with a Risky Implementation"
    ID_1241 = 1241, "Use of Predictable Algorithm in Random Number Generator"
    ID_1265 = (
        1265,
        "Unintended Reentrant Invocation of Non-reentrant Code Via Nested Calls",
    )
    ID_1339 = 1339, "Insufficient Precision or Accuracy of a Real Number"

    def __str__(self) -> str:
        return str(f"{self.code} - {self.summary}")
