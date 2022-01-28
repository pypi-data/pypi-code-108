#
# Copyright 2020 Nebulon, Inc.
# All Rights Reserved.
#
# DISCLAIMER: THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

from time import sleep
from .graphqlclient import GraphQLParam, NebMixin
from datetime import datetime
from .common import NebEnum, PageInput, read_value
from .filters import StringFilter, UuidFilter
from .sorting import SortDirection
from .recipe import RecipeState
from .tokens import TokenResponse
from .issues import Issues
from .updates import UpdateHistory

_TIMEOUT_SECONDS = 60 * 45
"""Timeout to wait for nPod creation to complete"""

__all__ = [
    "BondType",
    "BondTransmitHashPolicy",
    "BondLACPTransmitRate",
    "SetNPodTimeZoneInput",
    "NPodSort",
    "NPodFilter",
    "IPInfoConfigInput",
    "NPodSpuInput",
    "CreateNPodInput",
    "NPod",
    "NPodList",
    "NPodCustomDiagnostic",
    "ExpectedNPodCapacity",
    "NPodsMixin"
]


# TODO: Move these enums to the SPU space
class BondTransmitHashPolicy(NebEnum):
    """Transmit has policy used by link aggregation"""

    TransmitHashPolicyLayer2 = "TransmitHashPolicyLayer2"
    TransmitHashPolicyLayer34 = "TransmitHashPolicyLayer34"
    TransmitHashPolicyLayer23 = "TransmitHashPolicyLayer23"


class BondLACPTransmitRate(NebEnum):
    """Link aggregation transmit rate for LCAP"""

    LACPTransmitRateSlow = "LACPTransmitRateSlow"
    LACPTransmitRateFast = "LACPTransmitRateFast"


class BondType(NebEnum):
    """Link aggregation type for data ports"""

    BondModeNone = "BondModeNone"
    BondMode8023ad = "BondMode8023ad"
    BOND_MODE_BALANCE_ALB = "BondModeBalanceALB"


class SetNPodTimeZoneInput:
    """Allows setting the timezone of an nPod or SPU

    Possible timezones include:
    * Africa/Abidjan
    * Africa/Accra
    * Africa/Addis_Ababa
    * Africa/Algiers
    * Africa/Asmara
    * Africa/Asmera
    * Africa/Bamako
    * Africa/Bangui
    * Africa/Banjul
    * Africa/Bissau
    * Africa/Blantyre
    * Africa/Brazzaville
    * Africa/Bujumbura
    * Africa/Cairo
    * Africa/Casablanca
    * Africa/Ceuta
    * Africa/Conakry
    * Africa/Dakar
    * Africa/Dar_es_Salaam
    * Africa/Djibouti
    * Africa/Douala
    * Africa/El_Aaiun
    * Africa/Freetown
    * Africa/Gaborone
    * Africa/Harare
    * Africa/Johannesburg
    * Africa/Juba
    * Africa/Kampala
    * Africa/Khartoum
    * Africa/Kigali
    * Africa/Kinshasa
    * Africa/Lagos
    * Africa/Libreville
    * Africa/Lome
    * Africa/Luanda
    * Africa/Lubumbashi
    * Africa/Lusaka
    * Africa/Malabo
    * Africa/Maputo
    * Africa/Maseru
    * Africa/Mbabane
    * Africa/Mogadishu
    * Africa/Monrovia
    * Africa/Nairobi
    * Africa/Ndjamena
    * Africa/Niamey
    * Africa/Nouakchott
    * Africa/Ouagadougou
    * Africa/Porto-Novo
    * Africa/Sao_Tome
    * Africa/Timbuktu
    * Africa/Tripoli
    * Africa/Tunis
    * Africa/Windhoek
    * America/Adak
    * America/Anchorage
    * America/Anguilla
    * America/Antigua
    * America/Araguaina
    * America/Argentina/Buenos_Aires
    * America/Argentina/Catamarca
    * America/Argentina/ComodRivadavia
    * America/Argentina/Cordoba
    * America/Argentina/Jujuy
    * America/Argentina/La_Rioja
    * America/Argentina/Mendoza
    * America/Argentina/Rio_Gallegos
    * America/Argentina/Salta
    * America/Argentina/San_Juan
    * America/Argentina/San_Luis
    * America/Argentina/Tucuman
    * America/Argentina/Ushuaia
    * America/Aruba
    * America/Asuncion
    * America/Atikokan
    * America/Atka
    * America/Bahia
    * America/Bahia_Banderas
    * America/Barbados
    * America/Belem
    * America/Belize
    * America/Blanc-Sablon
    * America/Boa_Vista
    * America/Bogota
    * America/Boise
    * America/Buenos_Aires
    * America/Cambridge_Bay
    * America/Campo_Grande
    * America/Cancun
    * America/Caracas
    * America/Catamarca
    * America/Cayenne
    * America/Cayman
    * America/Chicago
    * America/Chihuahua
    * America/Coral_Harbour
    * America/Cordoba
    * America/Costa_Rica
    * America/Creston
    * America/Cuiaba
    * America/Curacao
    * America/Danmarkshavn
    * America/Dawson
    * America/Dawson_Creek
    * America/Denver
    * America/Detroit
    * America/Dominica
    * America/Edmonton
    * America/Eirunepe
    * America/El_Salvador
    * America/Ensenada
    * America/Fort_Nelson
    * America/Fort_Wayne
    * America/Fortaleza
    * America/Glace_Bay
    * America/Godthab
    * America/Goose_Bay
    * America/Grand_Turk
    * America/Grenada
    * America/Guadeloupe
    * America/Guatemala
    * America/Guayaquil
    * America/Guyana
    * America/Halifax
    * America/Havana
    * America/Hermosillo
    * America/Indiana/Indianapolis
    * America/Indiana/Knox
    * America/Indiana/Marengo
    * America/Indiana/Petersburg
    * America/Indiana/Tell_City
    * America/Indiana/Vevay
    * America/Indiana/Vincennes
    * America/Indiana/Winamac
    * America/Indianapolis
    * America/Inuvik
    * America/Iqaluit
    * America/Jamaica
    * America/Jujuy
    * America/Juneau
    * America/Kentucky/Louisville
    * America/Kentucky/Monticello
    * America/Knox_IN
    * America/Kralendijk
    * America/La_Paz
    * America/Lima
    * America/Los_Angeles
    * America/Louisville
    * America/Lower_Princes
    * America/Maceio
    * America/Managua
    * America/Manaus
    * America/Marigot
    * America/Martinique
    * America/Matamoros
    * America/Mazatlan
    * America/Mendoza
    * America/Menominee
    * America/Merida
    * America/Metlakatla
    * America/Mexico_City
    * America/Miquelon
    * America/Moncton
    * America/Monterrey
    * America/Montevideo
    * America/Montreal
    * America/Montserrat
    * America/Nassau
    * America/New_York
    * America/Nipigon
    * America/Nome
    * America/Noronha
    * America/North_Dakota/Beulah
    * America/North_Dakota/Center
    * America/North_Dakota/New_Salem
    * America/Nuuk
    * America/Ojinaga
    * America/Panama
    * America/Pangnirtung
    * America/Paramaribo
    * America/Phoenix
    * America/Port-au-Prince
    * America/Port_of_Spain
    * America/Porto_Acre
    * America/Porto_Velho
    * America/Puerto_Rico
    * America/Punta_Arenas
    * America/Rainy_River
    * America/Rankin_Inlet
    * America/Recife
    * America/Regina
    * America/Resolute
    * America/Rio_Branco
    * America/Rosario
    * America/Santa_Isabel
    * America/Santarem
    * America/Santiago
    * America/Santo_Domingo
    * America/Sao_Paulo
    * America/Scoresbysund
    * America/Shiprock
    * America/Sitka
    * America/St_Barthelemy
    * America/St_Johns
    * America/St_Kitts
    * America/St_Lucia
    * America/St_Thomas
    * America/St_Vincent
    * America/Swift_Current
    * America/Tegucigalpa
    * America/Thule
    * America/Thunder_Bay
    * America/Tijuana
    * America/Toronto
    * America/Tortola
    * America/Vancouver
    * America/Virgin
    * America/Whitehorse
    * America/Winnipeg
    * America/Yakutat
    * America/Yellowknife
    * Antarctica/Casey
    * Antarctica/Davis
    * Antarctica/DumontDUrville
    * Antarctica/Macquarie
    * Antarctica/Mawson
    * Antarctica/McMurdo
    * Antarctica/Palmer
    * Antarctica/Rothera
    * Antarctica/South_Pole
    * Antarctica/Syowa
    * Antarctica/Troll
    * Antarctica/Vostok
    * Arctic/Longyearbyen
    * Asia/Aden
    * Asia/Almaty
    * Asia/Amman
    * Asia/Anadyr
    * Asia/Aqtau
    * Asia/Aqtobe
    * Asia/Ashgabat
    * Asia/Ashkhabad
    * Asia/Atyrau
    * Asia/Baghdad
    * Asia/Bahrain
    * Asia/Baku
    * Asia/Bangkok
    * Asia/Barnaul
    * Asia/Beirut
    * Asia/Bishkek
    * Asia/Brunei
    * Asia/Calcutta
    * Asia/Chita
    * Asia/Choibalsan
    * Asia/Chongqing
    * Asia/Chungking
    * Asia/Colombo
    * Asia/Dacca
    * Asia/Damascus
    * Asia/Dhaka
    * Asia/Dili
    * Asia/Dubai
    * Asia/Dushanbe
    * Asia/Famagusta
    * Asia/Gaza
    * Asia/Harbin
    * Asia/Hebron
    * Asia/Ho_Chi_Minh
    * Asia/Hong_Kong
    * Asia/Hovd
    * Asia/Irkutsk
    * Asia/Istanbul
    * Asia/Jakarta
    * Asia/Jayapura
    * Asia/Jerusalem
    * Asia/Kabul
    * Asia/Kamchatka
    * Asia/Karachi
    * Asia/Kashgar
    * Asia/Kathmandu
    * Asia/Katmandu
    * Asia/Khandyga
    * Asia/Kolkata
    * Asia/Krasnoyarsk
    * Asia/Kuala_Lumpur
    * Asia/Kuching
    * Asia/Kuwait
    * Asia/Macao
    * Asia/Macau
    * Asia/Magadan
    * Asia/Makassar
    * Asia/Manila
    * Asia/Muscat
    * Asia/Nicosia
    * Asia/Novokuznetsk
    * Asia/Novosibirsk
    * Asia/Omsk
    * Asia/Oral
    * Asia/Phnom_Penh
    * Asia/Pontianak
    * Asia/Pyongyang
    * Asia/Qatar
    * Asia/Qostanay
    * Asia/Qyzylorda
    * Asia/Rangoon
    * Asia/Riyadh
    * Asia/Saigon
    * Asia/Sakhalin
    * Asia/Samarkand
    * Asia/Seoul
    * Asia/Shanghai
    * Asia/Singapore
    * Asia/Srednekolymsk
    * Asia/Taipei
    * Asia/Tashkent
    * Asia/Tbilisi
    * Asia/Tehran
    * Asia/Tel_Aviv
    * Asia/Thimbu
    * Asia/Thimphu
    * Asia/Tokyo
    * Asia/Tomsk
    * Asia/Ujung_Pandang
    * Asia/Ulaanbaatar
    * Asia/Ulan_Bator
    * Asia/Urumqi
    * Asia/Ust-Nera
    * Asia/Vientiane
    * Asia/Vladivostok
    * Asia/Yakutsk
    * Asia/Yangon
    * Asia/Yekaterinburg
    * Asia/Yerevan
    * Atlantic/Azores
    * Atlantic/Bermuda
    * Atlantic/Canary
    * Atlantic/Cape_Verde
    * Atlantic/Faeroe
    * Atlantic/Faroe
    * Atlantic/Jan_Mayen
    * Atlantic/Madeira
    * Atlantic/Reykjavik
    * Atlantic/South_Georgia
    * Atlantic/St_Helena
    * Atlantic/Stanley
    * Australia/ACT
    * Australia/Adelaide
    * Australia/Brisbane
    * Australia/Broken_Hill
    * Australia/Canberra
    * Australia/Currie
    * Australia/Darwin
    * Australia/Eucla
    * Australia/Hobart
    * Australia/LHI
    * Australia/Lindeman
    * Australia/Lord_Howe
    * Australia/Melbourne
    * Australia/NSW
    * Australia/North
    * Australia/Perth
    * Australia/Queensland
    * Australia/South
    * Australia/Sydney
    * Australia/Tasmania
    * Australia/Victoria
    * Australia/West
    * Australia/Yancowinna
    * Brazil/Acre
    * Brazil/DeNoronha
    * Brazil/East
    * Brazil/West
    * CET
    * CST6CDT
    * Canada/Atlantic
    * Canada/Central
    * Canada/Eastern
    * Canada/Mountain
    * Canada/Newfoundland
    * Canada/Pacific
    * Canada/Saskatchewan
    * Canada/Yukon
    * Chile/Continental
    * Chile/EasterIsland
    * Cuba
    * EET
    * EST
    * EST5EDT
    * Egypt
    * Eire
    * Etc/GMT
    * Etc/GMT+0
    * Etc/GMT+1
    * Etc/GMT+10
    * Etc/GMT+11
    * Etc/GMT+12
    * Etc/GMT+2
    * Etc/GMT+3
    * Etc/GMT+4
    * Etc/GMT+5
    * Etc/GMT+6
    * Etc/GMT+7
    * Etc/GMT+8
    * Etc/GMT+9
    * Etc/GMT-0
    * Etc/GMT-1
    * Etc/GMT-10
    * Etc/GMT-11
    * Etc/GMT-12
    * Etc/GMT-13
    * Etc/GMT-14
    * Etc/GMT-2
    * Etc/GMT-3
    * Etc/GMT-4
    * Etc/GMT-5
    * Etc/GMT-6
    * Etc/GMT-7
    * Etc/GMT-8
    * Etc/GMT-9
    * Etc/GMT0
    * Etc/Greenwich
    * Etc/UCT
    * Etc/UTC
    * Etc/Universal
    * Etc/Zulu
    * Europe/Amsterdam
    * Europe/Andorra
    * Europe/Astrakhan
    * Europe/Athens
    * Europe/Belfast
    * Europe/Belgrade
    * Europe/Berlin
    * Europe/Bratislava
    * Europe/Brussels
    * Europe/Bucharest
    * Europe/Budapest
    * Europe/Busingen
    * Europe/Chisinau
    * Europe/Copenhagen
    * Europe/Dublin
    * Europe/Gibraltar
    * Europe/Guernsey
    * Europe/Helsinki
    * Europe/Isle_of_Man
    * Europe/Istanbul
    * Europe/Jersey
    * Europe/Kaliningrad
    * Europe/Kiev
    * Europe/Kirov
    * Europe/Lisbon
    * Europe/Ljubljana
    * Europe/London
    * Europe/Luxembourg
    * Europe/Madrid
    * Europe/Malta
    * Europe/Mariehamn
    * Europe/Minsk
    * Europe/Monaco
    * Europe/Moscow
    * Europe/Nicosia
    * Europe/Oslo
    * Europe/Paris
    * Europe/Podgorica
    * Europe/Prague
    * Europe/Riga
    * Europe/Rome
    * Europe/Samara
    * Europe/San_Marino
    * Europe/Sarajevo
    * Europe/Saratov
    * Europe/Simferopol
    * Europe/Skopje
    * Europe/Sofia
    * Europe/Stockholm
    * Europe/Tallinn
    * Europe/Tirane
    * Europe/Tiraspol
    * Europe/Ulyanovsk
    * Europe/Uzhgorod
    * Europe/Vaduz
    * Europe/Vatican
    * Europe/Vienna
    * Europe/Vilnius
    * Europe/Volgograd
    * Europe/Warsaw
    * Europe/Zagreb
    * Europe/Zaporozhye
    * Europe/Zurich
    * Factory
    * GB
    * GB-Eire
    * GMT
    * GMT+0
    * GMT-0
    * GMT0
    * Greenwich
    * HST
    * Hongkong
    * Iceland
    * Indian/Antananarivo
    * Indian/Chagos
    * Indian/Christmas
    * Indian/Cocos
    * Indian/Comoro
    * Indian/Kerguelen
    * Indian/Mahe
    * Indian/Maldives
    * Indian/Mauritius
    * Indian/Mayotte
    * Indian/Reunion
    * Iran
    * Israel
    * Jamaica
    * Japan
    * Kwajalein
    * Libya
    * MET
    * MST
    * MST7MDT
    * Mexico/BajaNorte
    * Mexico/BajaSur
    * Mexico/General
    * NZ
    * NZ-CHAT
    * Navajo
    * PRC
    * PST8PDT
    * Pacific/Apia
    * Pacific/Auckland
    * Pacific/Bougainville
    * Pacific/Chatham
    * Pacific/Chuuk
    * Pacific/Easter
    * Pacific/Efate
    * Pacific/Enderbury
    * Pacific/Fakaofo
    * Pacific/Fiji
    * Pacific/Funafuti
    * Pacific/Galapagos
    * Pacific/Gambier
    * Pacific/Guadalcanal
    * Pacific/Guam
    * Pacific/Honolulu
    * Pacific/Johnston
    * Pacific/Kiritimati
    * Pacific/Kosrae
    * Pacific/Kwajalein
    * Pacific/Majuro
    * Pacific/Marquesas
    * Pacific/Midway
    * Pacific/Nauru
    * Pacific/Niue
    * Pacific/Norfolk
    * Pacific/Noumea
    * Pacific/Pago_Pago
    * Pacific/Palau
    * Pacific/Pitcairn
    * Pacific/Pohnpei
    * Pacific/Ponape
    * Pacific/Port_Moresby
    * Pacific/Rarotonga
    * Pacific/Saipan
    * Pacific/Samoa
    * Pacific/Tahiti
    * Pacific/Tarawa
    * Pacific/Tongatapu
    * Pacific/Truk
    * Pacific/Wake
    * Pacific/Wallis
    * Pacific/Yap
    * Poland
    * Portugal
    * ROC
    * ROK
    * Singapore
    * Turkey
    * UCT
    * US/Alaska
    * US/Aleutian
    * US/Arizona
    * US/Central
    * US/East-Indiana
    * US/Eastern
    * US/Hawaii
    * US/Indiana-Starke
    * US/Michigan
    * US/Mountain
    * US/Pacific
    * US/Samoa
    * UTC
    * Universal
    * W-SU
    * WET
    * Zulu
    """

    def __init__(
            self,
            time_zone: str
    ):
        """Constructs a new input object to set timezone

        :param time_zone: The time zone to set
        :type time_zone: str
        """

        self.__time_zone = time_zone

    @property
    def time_zone(self) -> str:
        """The time zone to set"""
        return self.__time_zone

    @property
    def as_dict(self):
        result = dict()
        result["timeZone"] = self.time_zone
        return result


class NPodSort:
    """A sort object for nPods

    Allows sorting nPods on common properties. The sort object allows
    only one property to be specified.
    """

    def __init__(
            self,
            name: SortDirection = None
    ):
        """Constructs a new sort object for nPods

        :param name: Sort direction for the ``name`` property
        :type name: SortDirection, optional
        """

        self.__name = name

    @property
    def name(self) -> SortDirection:
        """Sort direction for the ``name`` property"""
        return self.__name

    @property
    def as_dict(self):
        result = dict()
        result["name"] = self.name
        return result


class NPodFilter:
    """A filter object to filter nPods.

    Allows filtering for specific nPods in nebulon ON. The
    filter allows only one property to be specified. If filtering on multiple
    properties is needed, use the ``and_filter`` and ``or_filter`` options to
    concatenate multiple filters.
    """

    def __init__(
            self,
            uuid: UuidFilter = None,
            name: StringFilter = None,
            and_filter=None,
            or_filter=None
    ):
        """Constructs a new filter object

        :param uuid: Filter based on nPod unique identifiers
        :type uuid: UuidFilter, optional
        :param name: Filter based on nPod name
        :type name: StringFilter, optional
        :param and_filter: Concatenate another filter with a logical AND
        :type and_filter: DataCenterFilter, optional
        :param or_filter: Concatenate another filter with a logical OR
        :type or_filter: DataCenterFilter, optional
        """

        self.__uuid = uuid
        self.__name = name
        self.__and = and_filter
        self.__or = or_filter

    @property
    def uuid(self) -> UuidFilter:
        """Filter based on nPod unique identifiers"""
        return self.__uuid

    @property
    def name(self) -> StringFilter:
        """Filter based on nPod name"""
        return self.__name

    @property
    def and_filter(self):
        """Allows concatenation of multiple filters via logical AND"""
        return self.__and

    @property
    def or_filter(self):
        """Allows concatenation of multiple filters via logical OR"""
        return self.__or

    @property
    def as_dict(self):
        result = dict()
        result["uuid"] = self.uuid
        result["name"] = self.name
        result["and"] = self.and_filter
        result["or"] = self.or_filter
        return result


class IPInfoConfigInput:
    """An input object to configure SPU networking

     SPU network configuration is determined at nPod creation. Customers have
     the option to use static IP addresses for the control network or DHCP.
     When using DHCP, it is recommended to use static IP reservations for the
     data networks.

     Customers can choose between using two separate networks for the data
     network or a link aggregation (LACP). When using link aggregation, two
     interface names are expected, one if not.

     When specifying an IP address, it can be either IPv4 or IPv6 and supports
     the CIDR address format.
     """

    def __init__(
            self,
            dhcp: bool,
            bond_mode: BondType,
            interfaces: [str],
            address: str = "",
            netmask_bits: int = 0,
            gateway: str = "",
            half_duplex: bool = False,
            speed_mb: int = 0,
            locked_speed: bool = False,
            mtu: int = 1500,
            bond_transmit_hash_policy: BondTransmitHashPolicy = None,
            bond_mii_monitor_ms: int = None,
            bond_lacp_transmit_rate: BondLACPTransmitRate = None
    ):
        """Constructs a new input object for configuring SPU network config

        :param dhcp: Specifies if DHCP should be used for the data network. If
            set to ``True``, fields ``address``, ``netmask_bits``, ``gateway`` are
            optional. If set to ``False``, these values become mandatory.
        :type dhcp: bool
        :param bond_mode: Specifies the link aggregation mode for the data
            network ports. If not set to ``None``, the ``interfaces`` parameter must
            be an array that lists the names of both interfaces:
            `['enP8p1s0f0np0', 'enP8p1s0f1np1']`, if set to ``None`` the specific
            interface must be identified by its name.
        :type bond_mode: BondType
        :param interfaces: List of interfaces that shall be configured with
            this object. If ``bond_mode`` is set to ``None`` a single interface
            shall be specified. If set to a link aggregation mode both data
            interface names shall be specified. Options are `enP8p1s0f0np0` and
            `enP8p1s0f1np1`.
        :type interfaces: [str]
        :param address: The IPv4 or IPv6 address for the data network interface.
            If CIDR format is used, the ``netmask_bits`` value is ignored. If
            ``DHCP`` is set to ``True``, this field must not be specified.
        :type address: str, optional
        :param netmask_bits: The network mask in bits. If ``address`` is specified
            in CIDR format, this value will be ignored, otherwise this is a
            mandatory field.
        :type netmask_bits: int, optional
        :param gateway: The network gateway address for the network interface.
            If ``dhcp`` is set to ``True`` this field is optional and ignored. If
            static IP address is used, this field is mandatory.
        :type gateway: str, optional
        :param half_duplex: Specifies if the network interface shall use
            half duplex. By default, this field should be set to ``False``.
        :type half_duplex: bool, optional
        :param speed_mb: Allows setting the interface speed to a specific
            value. This field is ignored when ``locked_speed`` is set to ``False``
            (default).
        :type speed_mb: int, optional
        :param locked_speed: Allows setting the interface speed and the
            duplex mode to specific values. If set to ``True`` the values of
            ``speed_mb`` and ``half_duplex`` are enforced.
        :type locked_speed: bool, optional
        :param mtu: Allows setting the maximum transfer unit (MTU) for the
            interface. By default an MTU of `1500` is used.
        :type mtu: int, optional
        :param bond_transmit_hash_policy: Allows specifying the transmit hashing
            policy mode when using link aggregation. This field is ignored when
            ``bond_mode`` is set to ``None``.
        :type bond_transmit_hash_policy: BondTransmitHashPolicy, optional
        :param bond_mii_monitor_ms: Allows alerting the default media
            independent interface monitoring interval. This field is ignored
            when ``bond_mode`` is set to ``None``.
        :type bond_mii_monitor_ms: int, optional
        :param bond_lacp_transmit_rate: Allows altering the default LACP
            transmit rate. This field is ignored if ``bond_mode`` is not set to
            `BondMode8023ad`.
        :type bond_lacp_transmit_rate: BondLACPTransmitRate, optional
        """

        self.__dhcp = dhcp
        self.__address = address
        self.__netmask_bits = netmask_bits
        self.__gateway = gateway
        self.__bond_mode = bond_mode
        self.__bond_transmit_hash_policy = bond_transmit_hash_policy
        self.__bond_mii_monitor_ms = bond_mii_monitor_ms
        self.__bond_lacp_transmit_rate = bond_lacp_transmit_rate
        self.__interfaces = interfaces
        self.__half_duplex = half_duplex
        self.__speed_mb = speed_mb
        self.__locked_speed = locked_speed
        self.__mtu = mtu

    @property
    def dhcp(self) -> bool:
        """Specifies if DHCP should be used for the data network."""
        return self.__dhcp

    @property
    def address(self) -> str:
        """IPv4 or IPv6 address if static IP address is used"""
        return self.__address

    @property
    def netmask_bits(self) -> int:
        """Netmask in bits if static IP address is used"""
        return self.__netmask_bits

    @property
    def gateway(self) -> str:
        """Gateway IP address if static IP address is used"""
        return self.__gateway

    @property
    def bond_mode(self) -> BondType:
        """Link aggregation mode for the data interfaces"""
        return self.__bond_mode

    @property
    def bond_transmit_hash_policy(self) -> BondTransmitHashPolicy:
        """Allows specifying the transmit hashing policy"""
        return self.__bond_transmit_hash_policy

    @property
    def bond_mii_monitor_ms(self) -> int:
        """Allows specifying the MII monitor interval"""
        return self.__bond_mii_monitor_ms

    @property
    def bond_lacp_transmit_rate(self) -> BondLACPTransmitRate:
        """Allows specifying the LACP transmit rate"""
        return self.__bond_lacp_transmit_rate

    @property
    def interfaces(self) -> list:
        """List of interfaces to include in the configuration"""
        return self.__interfaces

    @property
    def half_duplex(self) -> bool:
        """Allows overwriting duplex for the interface"""
        return self.__half_duplex

    @property
    def speed_mb(self) -> int:
        """Allows overwriting interface speed"""
        return self.__speed_mb

    @property
    def locked_speed(self) -> bool:
        """Allows locking interface speed"""
        return self.__locked_speed

    @property
    def mtu(self) -> int:
        """Allows specifying MTU"""
        return self.__mtu

    @property
    def as_dict(self):
        result = dict()
        result["dhcp"] = self.dhcp
        result["addr"] = self.address
        result["netmaskBits"] = self.netmask_bits
        result["gateway"] = self.gateway
        result["bondModeV2"] = self.bond_mode
        result["bondTransmitHashPolicy"] = self.bond_transmit_hash_policy
        result["bondMIIMonitorMilliSeconds"] = self.bond_mii_monitor_ms
        result["bondLACPTransmitRate"] = self.bond_lacp_transmit_rate
        result["interfaces"] = self.interfaces
        result["halfDuplex"] = self.half_duplex
        result["speedMB"] = self.speed_mb
        result["lockedSpeed"] = self.locked_speed
        result["mtu"] = self.mtu
        return result


class NPodSpuInput:
    """An input object to configure SPUs for nPod creation

    Allows specifying SPU configuration options when creating a new nPod.
    Configuration is mostly for network configuration.
    """

    def __init__(
            self,
            spu_serial: str,
            spu_data_ips: [IPInfoConfigInput] = None
    ):
        """Constructs a new NPodSpuInput object

        Allows specifying SPU configuration options when creating a new nPod.
        Configuration is mostly for network configuration.

        :param spu_serial: Specifies the SPU serial number
        :type spu_serial: str
        :param spu_data_ips: Allows configuring the SPUs network interfaces
        :type spu_data_ips: [IPInfoConfigInput], optional
        """

        self.__spu_name = ""
        self.__spu_serial = spu_serial
        self.__spu_data_ips = spu_data_ips

    @property
    def spu_name(self) -> str:
        """Human readable name for a SPU"""
        return self.__spu_name

    @property
    def spu_serial(self) -> str:
        """Serial number for the SPU"""
        return self.__spu_serial

    @property
    def spu_data_ips(self) -> [IPInfoConfigInput]:
        """Allows configuring the SPUs network interfaces"""
        return self.__spu_data_ips

    @property
    def as_dict(self):
        result = dict()
        result["SPUName"] = self.spu_name
        result["SPUSerial"] = self.spu_serial
        result["SPUDataIPs"] = self.spu_data_ips
        return result


class CreateNPodInput:
    """An input object to create a new nPod

    A nPod is a collection of network-connected application servers with SPUs
    installed that form an application cluster. Together, the SPUs in a nPod
    serve shared or local storage to the servers in the application cluster,
    e.g. a hypervisor cluster, container platform, or clustered bare metal
    application.
    """

    def __init__(
            self,
            name: str,
            npod_group_uuid: str,
            spus: [NPodSpuInput],
            npod_template_uuid: str,
            note: str = None,
            timezone: str = None
    ):
        """Constructs a new input object to create a new nPod

        :param name: Name of the new nPod
        :type name: str
        :param npod_group_uuid: The unique identifier of the nPod group this
            nPod will be added to
        :type npod_group_uuid: str
        :param spus: List of SPU configuration information that will be used
            in the new nPod. At least 3 SPU configuration information objects
            must be specified
        :type spus: [NPodSpuInput]
        :param npod_template_uuid: The unique identifier of the nPod template
            to use for the new nPod
        :type npod_template_uuid: str
        :param note: An optional note for the new nPod
        :type note: str, optional
        :param timezone: The timezone to be configured for all SPUs in the nPod
        :type timezone: str, optional
        """

        self.__name = name
        self.__npod_group_uuid = npod_group_uuid
        self.__spus = spus
        self.__npod_template_uuid = npod_template_uuid
        self.__note = note
        self.__timezone = timezone

    @property
    def name(self) -> str:
        """Name of the new nPod"""
        return self.__name

    @property
    def npod_group_uuid(self) -> str:
        """The unique identifier of the nPod group this nPod will be added to"""
        return self.__npod_group_uuid

    @property
    def spus(self) -> [NPodSpuInput]:
        """List of SPU configuration information for SPUs to use"""
        return self.__spus

    @property
    def npod_template_uuid(self) -> str:
        """The unique identifier of the nPod template to use"""
        return self.__npod_template_uuid

    @property
    def note(self) -> str:
        """An optional note for the new nPod"""
        return self.__note

    @property
    def timezone(self) -> str:
        """The timezone to be configured for all SPUs in the nPod"""
        return self.__timezone

    @property
    def as_dict(self):
        result = dict()
        result["nPodName"] = self.name
        result["nPodGroupUUID"] = self.npod_group_uuid
        result["spus"] = self.spus
        result["nPodTemplateUUID"] = self.npod_template_uuid
        result["note"] = self.note
        result["timeZone"] = self.timezone
        return result


class NPod:
    """Defines a nebulon Pod (nPod)

    A nPod is a collection of network-connected application servers with SPUs
    installed that form an application cluster. Together, the SPUs in a nPod
    serve shared or local storage to the servers in the application cluster,
    e.g. a hypervisor cluster, container platform, or clustered bare metal
    application.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__uuid = read_value(
            "uuid", response, str, True)
        self.__name = read_value(
            "name", response, str, True)
        self.__note = read_value(
            "note", response, str, True)
        self.__npod_group_uuid = read_value(
            "nPodGroup.uuid", response, str, False)
        self.__volume_uuids = read_value(
            "volumes.uuid", response, str, False)
        self.__volume_count = read_value(
            "volumeCount", response, int, True)
        self.__host_uuids = read_value(
            "hosts.uuid", response, str, False)
        self.__host_count = read_value(
            "hostCount", response, int, True)
        self.__spu_serials = read_value(
            "spus.serial", response, str, False)
        self.__spu_count = read_value(
            "spuCount", response, int, True)
        self.__snapshot_uuids = read_value(
            "snapshots.uuid", response, str, False)
        self.__update_history = read_value(
            "updateHistory", response, UpdateHistory, False)
        self.__npod_template_uuid = read_value(
            "nPodTemplate.uid", response, str, False)

    @property
    def uuid(self) -> str:
        """The unique identifier of the nPod"""
        return self.__uuid

    @property
    def name(self) -> str:
        """The name of the nPod"""
        return self.__name

    @property
    def note(self) -> str:
        """An optional note for the nPod"""
        return self.__note

    @property
    def npod_group_uuid(self) -> str:
        """The unique identifier of the nPod group this nPod belongs to"""
        return self.__npod_group_uuid

    @property
    def volume_uuids(self) -> [str]:
        """List of volume identifiers defined in this nPod"""
        return self.__volume_uuids

    @property
    def volume_count(self) -> int:
        """Number of volumes defined in this nPod"""
        return self.__volume_count

    @property
    def host_uuids(self) -> list:
        """List of host identifiers part of this nPod"""
        return self.__host_uuids

    @property
    def host_count(self) -> int:
        """Number of hosts part of this nPod"""
        return self.__host_count

    @property
    def spu_serials(self) -> list:
        """List of serial numbers part of this nPod"""
        return self.__spu_serials

    @property
    def spu_count(self) -> int:
        """Number of spus part of this nPod"""
        return self.__spu_count

    @property
    def snapshot_uuids(self) -> list:
        """List of snapshot identifiers defined in this nPod"""
        return self.__snapshot_uuids

    @property
    def update_history(self) -> [UpdateHistory]:
        """List of updates performed on this nPod"""
        return self.__update_history

    @property
    def npod_template_uuid(self) -> str:
        """Unique identifier for the nPod template used during nPod creation"""
        return self.__npod_template_uuid

    @staticmethod
    def fields():
        return [
            "uuid",
            "name",
            "note",
            "nPodGroup{uuid}",
            "volumes{uuid}",
            "volumeCount",
            "hosts{uuid}",
            "hostCount",
            "spus{serial}",
            "spuCount",
            "snapshots{uuid}",
            "updateHistory{%s}" % ",".join(UpdateHistory.fields()),
            "nPodTemplate{uid}"
        ]


class NPodList:
    """Paginated nPod list object

    Contains a list of nPod objects and information for
    pagination. By default a single page includes a maximum of `100` items
    unless specified otherwise in the paginated query.

    Consumers should always check for the property ``more`` as per default
    the server does not return the full list of alerts but only one page.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new nPod list object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__items = read_value(
            "items", response, NPod, True)
        self.__more = read_value(
            "more", response, bool, True)
        self.__total_count = read_value(
            "totalCount", response, int, True)
        self.__filtered_count = read_value(
            "filteredCount", response, int, True)

    @property
    def items(self) -> list:
        """List of nPods in the pagination list"""
        return self.__items

    @property
    def more(self) -> bool:
        """Indicates if there are more items on the server"""
        return self.__more

    @property
    def total_count(self) -> int:
        """The total number of items on the server"""
        return self.__total_count

    @property
    def filtered_count(self) -> int:
        """The number of items on the server matching the provided filter"""
        return self.__filtered_count

    @staticmethod
    def fields():
        return [
            "items{%s}" % ",".join(NPod.fields()),
            "more",
            "totalCount",
            "filteredCount",
        ]


class NPodCustomDiagnostic:
    """Defines a custom diagnostics script

    Custom diagnostics scripts are used by nebulon customer satisfaction when
    custom commands and diagnostics scripts need to be executed on SPUs in
    customers datacenters to resolve issues.

    Commands cannot be executed without customer approval as they need to be
    approved and authenticated through the security triangle. Custom diagnostics
    scripts are the vehicle to facilitate the security triangle.
    """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new NPodCustomDiagnostic object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__request_uuid = read_value(
            "requestUID", response, str, False)
        self.__diagnostic_name = read_value(
            "diagnosticName", response, str, False)
        self.__npod_uuid = read_value(
            "podUID", response, str, False)
        self.__once_only = read_value(
            "onceOnly", response, bool, False)
        self.__note = read_value(
            "note", response, str, False)

    @property
    def request_uuid(self) -> str:
        """Unique identifier for the diagnostic script"""
        return self.__request_uuid

    @property
    def diagnostic_name(self) -> str:
        """Human readable name for the diagnostic script"""
        return self.__diagnostic_name

    @property
    def npod_uuid(self) -> str:
        """Unique identifier of the nPod on which the script should run"""
        return self.__npod_uuid

    @property
    def once_only(self) -> bool:
        """Indicates that the script will only be executed once"""
        return self.__once_only

    @property
    def note(self) -> str:
        """An optional note for the diagnostics script"""
        return self.__note

    @staticmethod
    def fields():
        return [
            "requestUID",
            "diagnosticName",
            "podUID",
            "onceOnly",
            "note",
        ]


class ExpectedNPodCapacity:
    """Describes information for nPods that are about to be created

     Allows predicting of the storage configuration of an nPod before its
     creation.
     """

    def __init__(
            self,
            response: dict
    ):
        """Constructs a new ExpectedNPodCapacity object

        This constructor expects a dict() object from the nebulon ON API. It
        will check the returned data against the currently implemented schema
        of the SDK.

        :param response: The JSON response from the server
        :type response: dict

        :raises ValueError: An error if illegal data is returned from the server
        """
        self.__total_pd_capacity_blk = read_value(
            "totalPDCapacityBlk", response, int, False)
        self.__total_raw_capacity_blk = read_value(
            "totalRawCapacityBlk", response, int, False)
        self.__total_user_data_capacity_blk = read_value(
            "totalUserDataCapacityBlk", response, int, False)
        self.__template_saving_factor = read_value(
            "templateSavingFactor", response, float, False)
        self.__total_presented_capacity = read_value(
            "totalPresentedCapacity", response, int, False)
        self.__total_vv_count = read_value(
            "totalVVCount", response, int, False)

    @property
    def total_pd_capacity_blk(self) -> int:
        """Total physical drive capacity in blocks (512 bytes)"""
        return self.__total_pd_capacity_blk

    @property
    def total_raw_capacity_blk(self) -> int:
        """Total raw capacity in blocks (512 bytes)"""
        return self.__total_raw_capacity_blk

    @property
    def total_user_data_capacity_blk(self) -> int:
        """Total usable capacity in blocks (512 bytes)"""
        return self.__total_user_data_capacity_blk

    @property
    def template_saving_factor(self) -> float:
        """Savings factor used for the calculation, provided by the template"""
        return self.__template_saving_factor

    @property
    def total_presented_capacity(self) -> int:
        """Total capacity presented to hosts"""
        return self.__total_presented_capacity

    @property
    def total_vv_count(self) -> int:
        """Total number of volumes that will be created"""
        return self.__total_vv_count

    @staticmethod
    def fields():
        return [
            "totalPDCapacityBlk",
            "totalRawCapacityBlk",
            "totalUserDataCapacityBlk",
            "templateSavingFactor",
            "totalPresentedCapacity",
            "totalVVCount",
        ]


class NPodsMixin(NebMixin):
    """Mixin to add nPod related methods to the GraphQL client"""

    def get_npods(
            self,
            page: PageInput = None,
            npod_filter: NPodFilter = None,
            sort: NPodSort = None
    ) -> NPodList:
        """Retrieve a list of provisioned nPods

        :param page: The requested page from the server. This is an optional
            argument and if omitted the server will default to returning the
            first page with a maximum of `100` items.
        :type page: PageInput, optional
        :param npod_filter: A filter object to filter the nPods on the
            server. If omitted, the server will return all objects as a
            paginated response.
        :type npod_filter: NPodFilter, optional
        :param sort: A sort definition object to sort the nPod objects
            on supported properties. If omitted objects are returned in the
            order as they were created in.
        :type sort: NPodSort, optional

        :returns NPodList: A paginated list of nPods.

        :raises GraphQLError: An error with the GraphQL endpoint.
        """

        # setup query parameters
        parameters = dict()
        parameters["page"] = GraphQLParam(
            page, "PageInput", False)
        parameters["filter"] = GraphQLParam(
            npod_filter, "NPodFilter", False)
        parameters["sort"] = GraphQLParam(
            sort, "NPodSort", False)

        # make the request
        response = self._query(
            name="getNPods",
            params=parameters,
            fields=NPodList.fields()
        )

        # convert to object
        return NPodList(response)

    def __get_new_pod_issues(
            self,
            spus: [NPodSpuInput]
    ) -> Issues:
        """Internal method that checks for issues during nPod creation"""

        # current API expects a list of spu serial numbers
        spu_serials = [i.spu_serial for i in spus]

        # setup query parameters
        parameters = dict()
        parameters["spuSerials"] = GraphQLParam(
            spu_serials,
            "[String!]",
            True
        )

        # make the request
        response = self._query(
            name="newPodIssues",
            params=parameters,
            fields=Issues.fields()
        )

        # convert to object
        return Issues(response)

    def create_npod(
            self,
            name: str,
            npod_group_uuid: str,
            spus: [NPodSpuInput],
            npod_template_uuid: str,
            note: str = None,
            timezone: str = None,
            ignore_warnings: bool = False
    ) -> NPod:
        """Allows creation of a new nPod

        A nPod is a collection of network-connected application servers with
        SPUs installed that form an application cluster. Together, the SPUs in
        a nPod serve shared or local storage to the servers in the application
        cluster, e.g. a hypervisor cluster, container platform, or clustered
        bare metal application.

        :param name: Name of the new nPod
        :type name: str
        :param npod_group_uuid: The unique identifier of the nPod group this
            nPod will be added to
        :type npod_group_uuid: str
        :param spus: List of SPU configuration information that will be used
            in the new nPod. At least 3 SPU configuration information objects
            must be specified
        :type spus: [NPodSpuInput]
        :param npod_template_uuid: The unique identifier of the nPod template
            to use for the new nPod
        :type npod_template_uuid: str
        :param note: An optional note for the new nPod
        :type note: str, optional
        :param timezone: The timezone to be configured for all SPUs in the nPod
        :type timezone: str, optional
        :param ignore_warnings: If specified and set to ``True`` the nPod creation
            will proceed even if nebulon ON reports warnings. It is advised to
            not ignore warnings. Consequently, the default behavior is that
            the nPod creation will fail when nebulon ON reports validation
            errors.
        :type ignore_warnings: bool, optional

        :returns NPod: The new nPod

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: When illegal parameters are supplied.
        :raises Exception: When nebulon ON reports validation errors or warnings
            and the ``ignore_warnings`` parameter is not set to ``True`` or if the
            nPod creation times out.
        """

        # check the basics
        if name is None or len(name) == 0:
            raise ValueError("name must be a non-zero length utf-8 string")

        if npod_group_uuid is None or len(npod_group_uuid) == 0:
            raise ValueError("npod_group_uuid must be a valid UUID string")

        if npod_template_uuid is None or len(npod_template_uuid) == 0:
            raise ValueError("npod_template_uuid must be a valid UUID string")

        if len(spus) == 2:
            raise ValueError("spus must be a list of exactly 1, 3 or more")

        # check for potential issues that nebulon ON predicts
        issues = self.__get_new_pod_issues(spus=spus)
        issues.assert_no_issues(ignore_warnings=ignore_warnings)

        # setup query parameters for npod creation
        parameters = dict()
        parameters["input"] = GraphQLParam(
            CreateNPodInput(
                name=name,
                npod_group_uuid=npod_group_uuid,
                spus=spus,
                npod_template_uuid=npod_template_uuid,
                note=note,
                timezone=timezone
            ),
            "CreateNPodInput",
            True
        )

        # make the request
        response = self._mutation(
            name="createNPod",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        delivery_response = token_response.deliver_token()

        # wait for recipe completion
        # TODO: Nebulon ON now returns a different response
        recipe_uuid = delivery_response["recipe_uuid_to_wait_on"]
        npod_uuid = delivery_response["npod_uuid_to_wait_on"]

        # set a custom timeout for the nPod creation process
        start = datetime.now()

        while True:
            sleep(5)

            recipes = self.get_npod_recipes(
                npod_uuid=npod_uuid,
                recipe_uuid=recipe_uuid
            )

            # if there is no record in the cloud wait a few more seconds
            # this case should not exist. TODO: Remove in next version.
            if len(recipes.items) == 0:
                continue

            # based on the query there should be exactly one
            recipe = recipes.items[0]

            if recipe.state == RecipeState.Failed:
                raise Exception(f"nPod creation failed: {recipe.status}")

            if recipe.state == RecipeState.Completed:
                npod_list = self.get_npods(
                    npod_filter=NPodFilter(
                        uuid=UuidFilter(
                            equals=npod_uuid
                        )
                    )
                )
                return npod_list.items[0]

            # Wait time remaining until timeout
            total_duration = (datetime.now() - start).seconds
            time_remaining = _TIMEOUT_SECONDS - total_duration

            if time_remaining <= 0:
                raise Exception("nPod creation timed out")

    def delete_npod(
            self,
            uuid: str,
            secure_erase: bool = False
    ):
        """Delete an existing nPod

        Deletes an nPod and erases all stored data. During nPod deletion the
        configuration of SPUs in an nPod is wiped and data encryption keys are
        erased. This renders all data in the nPod unrecoverable. This operation
        is irreversible.

        :param uuid: The unique identifier of the nPod to delete.
        :type uuid: str
        :param secure_erase: Forces a secure wipe of the nPod. While this is not
            required in most cases as nPod deletion will destroy the encryption
            keys and render data unreadable, it allows to explicitly overwrite
            data on server SSDs. Only use this flag when decommissioning
            storage as the secure_wipe procedure will take some time.
        :type secure_erase: bool, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: When illegal parameters are supplied.
        :raises Exception: When there were issues delivering the security token
            to affected SPUs.

        .. warnings also::
            This operation will permanently erase data and the data cannot be
            recovered.
        """

        # check the basics
        if uuid is None or len(uuid) == 0:
            raise ValueError("uuid must be a valid UUID string")

        # setup query parameters
        parameters = dict()
        parameters["uid"] = GraphQLParam(
            uuid,
            "String",
            True
        )
        parameters["secureErase"] = GraphQLParam(
            secure_erase,
            "Boolean",
            False
        )

        # make the request
        response = self._mutation(
            name="delPod",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        # TODO: Implement waiting for all contained SPUs to become available
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def set_npod_timezone(
            self,
            uuid: str,
            timezone: str = "UTC"
    ):
        """Allows setting the timezone for all SPUs in an nPod

        :param uuid: The unique identifier of the nPod that is being modified.
        :type uuid: str
        :param timezone: The target timezone for the nPod. Refer to the
            ``Timezone`` enumeration for available options. By default ``UTC`` is
            used for the timezone.
        :type timezone: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: When illegal parameters are supplied.
        :raises Exception: When there were issues delivering the security token
            to affected SPUs.
        """

        # check the basics
        if uuid is None or len(uuid) == 0:
            raise ValueError("uuid must be a valid UUID string")

        # setup query parameters
        parameters = dict()
        parameters["uuid"] = GraphQLParam(
            uuid, "UUID", True)
        parameters["input"] = GraphQLParam(
            SetNPodTimeZoneInput(
                time_zone=timezone
            ),
            "SetNPodTimeZoneInput",
            True
        )

        # make the request
        response = self._mutation(
            name="setNPodTimeZone",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object and deliver token
        token_response = TokenResponse(response)
        token_response.deliver_token()

    def send_npod_debug_info(
            self,
            uuid: str,
            note: str = None
    ):
        """Allows sending verbose diagnostic information to nebulon ON

        In cases where more in-depth diagnostic information is required to
        resolve customer issues, this method allows capturing and uploading
        verbose diagnostic information from SPUs in the specified nPod through
        a secure channel to nebulon ON.

        :param uuid: The unique identifier of the affected nPod.
        :type uuid: str
        :param note: Allows specifying additional textual information that is
            added to the diagnostic bundle. This allows a user to provide
            accompanying information, e.g. to describe an observed issue.
        :type note: str, optional

        :raises GraphQLError: An error with the GraphQL endpoint.
        :raises ValueError: When illegal parameters are supplied.
        :raises Exception: When there were issues delivering the security token
            to affected SPUs.
        """

        # check the basics
        if uuid is None or len(uuid) == 0:
            raise ValueError("uuid must be a valid UUID string")

        # setup query parameters
        parameters = dict()
        parameters["podUID"] = GraphQLParam(
            uuid, "String", False)
        parameters["note"] = GraphQLParam(
            note, "String", False)

        # make the request
        response = self._mutation(
            name="sendDebugInfo",
            params=parameters,
            fields=TokenResponse.fields()
        )

        # convert to object
        token_response = TokenResponse(response)
        token_response.deliver_token()
