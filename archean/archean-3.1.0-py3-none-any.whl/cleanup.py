import re
import datetime

CURRENCY_ABBR = [
    "AFA",  # Afghanistan afghani
    "ALL",  # Albanian lek
    "DZD",  # Algerian dinar
    "AOR",  # Angolan kwanza reajustado
    "ARS",  # Argentine peso
    "AMD",  # Armenian dram
    "AWG",  # Aruban guilder
    "AUD",  # Australian dollar
    "AZN",  # Azerbaijanian new manat
    "BSD",  # Bahamian dollar
    "BHD",  # Bahraini dinar
    "BDT",  # Bangladeshi taka
    "BBD",  # Barbados dollar
    "BYN",  # Belarusian ruble
    "BZD",  # Belize dollar
    "BMD",  # Bermudian dollar
    "BTN",  # Bhutan ngultrum
    "BOB",  # Bolivian boliviano
    "BWP",  # Botswana pula
    "BRL",  # Brazilian real
    "GBP",  # British pound
    "BND",  # Brunei dollar
    "BGN",  # Bulgarian lev
    "BIF",  # Burundi franc
    "KHR",  # Cambodian riel
    "CAD",  # Canadian dollar
    "CVE",  # Cape Verde escudo
    "KYD",  # Cayman Islands dollar
    "XOF",  # CFA franc BCEAO
    "XAF",  # CFA franc BEAC
    "XPF",  # CFP franc
    "CLP",  # Chilean peso
    "CNY",  # Chinese yuan renminbi
    "COP",  # Colombian peso
    "KMF",  # Comoros franc
    "CDF",  # Congolese franc
    "CRC",  # Costa Rican colon
    "HRK",  # Croatian kuna
    "CUP",  # Cuban peso
    "CZK",  # Czech koruna
    "DKK",  # Danish krone
    "DJF",  # Djibouti franc
    "DOP",  # Dominican peso
    "XCD",  # East Caribbean dollar
    "EGP",  # Egyptian pound
    "SVC",  # El Salvador colon
    "ERN",  # Eritrean nakfa
    "EEK",  # Estonian kroon
    "ETB",  # Ethiopian birr
    "EUR",  # EU euro
    "FKP",  # Falkland Islands pound
    "FJD",  # Fiji dollar
    "GMD",  # Gambian dalasi
    "GEL",  # Georgian lari
    "GHS",  # Ghanaian new cedi
    "GIP",  # Gibraltar pound
    "XAU",  # Gold (ounce)
    "XFO",  # Gold franc
    "GTQ",  # Guatemalan quetzal
    "GNF",  # Guinean franc
    "GYD",  # Guyana dollar
    "HTG",  # Haitian gourde
    "HNL",  # Honduran lempira
    "HKD",  # Hong Kong SAR dollar
    "HUF",  # Hungarian forint
    "ISK",  # Icelandic krona
    "XDR",  # IMF special drawing right
    "INR",  # Indian rupee
    "IDR",  # Indonesian rupiah
    "IRR",  # Iranian rial
    "IQD",  # Iraqi dinar
    "ILS",  # Israeli new shekel
    "JMD",  # Jamaican dollar
    "JPY",  # Japanese yen
    "JOD",  # Jordanian dinar
    "KZT",  # Kazakh tenge
    "KES",  # Kenyan shilling
    "KWD",  # Kuwaiti dinar
    "KGS",  # Kyrgyz som
    "LAK",  # Lao kip
    "LVL",  # Latvian lats
    "LBP",  # Lebanese pound
    "LSL",  # Lesotho loti
    "LRD",  # Liberian dollar
    "LYD",  # Libyan dinar
    "LTL",  # Lithuanian litas
    "MOP",  # Macao SAR pataca
    "MKD",  # Macedonian denar
    "MGA",  # Malagasy ariary
    "MWK",  # Malawi kwacha
    "MYR",  # Malaysian ringgit
    "MVR",  # Maldivian rufiyaa
    "MRO",  # Mauritanian ouguiya
    "MUR",  # Mauritius rupee
    "MXN",  # Mexican peso
    "MDL",  # Moldovan leu
    "MNT",  # Mongolian tugrik
    "MAD",  # Moroccan dirham
    "MZN",  # Mozambique new metical
    "MMK",  # Myanmar kyat
    "NAD",  # Namibian dollar
    "NPR",  # Nepalese rupee
    "ANG",  # Netherlands Antillian guilder
    "NZD",  # New Zealand dollar
    "NIO",  # Nicaraguan cordoba oro
    "NGN",  # Nigerian naira
    "KPW",  # North Korean won
    "NOK",  # Norwegian krone
    "OMR",  # Omani rial
    "PKR",  # Pakistani rupee
    "XPD",  # Palladium (ounce)
    "PAB",  # Panamanian balboa
    "PGK",  # Papua New Guinea kina
    "PYG",  # Paraguayan guarani
    "PEN",  # Peruvian nuevo sol
    "PHP",  # Philippine peso
    "XPT",  # Platinum (ounce)
    "PLN",  # Polish zloty
    "QAR",  # Qatari rial
    "RON",  # Romanian new leu
    "RUB",  # Russian ruble
    "RWF",  # Rwandan franc
    "SHP",  # Saint Helena pound
    "WST",  # Samoan tala
    "STD",  # Sao Tome and Principe dobra
    "SAR",  # Saudi riyal
    "RSD",  # Serbian dinar
    "SCR",  # Seychelles rupee
    "SLL",  # Sierra Leone leone
    "XAG",  # Silver (ounce)
    "SGD",  # Singapore dollar
    "SBD",  # Solomon Islands dollar
    "SOS",  # Somali shilling
    "ZAR",  # South African rand
    "KRW",  # South Korean won
    "LKR",  # Sri Lanka rupee
    "SDG",  # Sudanese pound
    "SRD",  # Suriname dollar
    "SZL",  # Swaziland lilangeni
    "SEK",  # Swedish krona
    "CHF",  # Swiss franc
    "SYP",  # Syrian pound
    "TWD",  # Taiwan New dollar
    "TJS",  # Tajik somoni
    "TZS",  # Tanzanian shilling
    "THB",  # Thai baht
    "TOP",  # Tongan pa'anga
    "TTD",  # Trinidad and Tobago dollar
    "TND",  # Tunisian dinar
    "TRY",  # Turkish lira
    "TMT",  # Turkmen new manat
    "AED",  # UAE dirham
    "UGX",  # Uganda new shilling
    "XFU",  # UIC franc
    "UAH",  # Ukrainian hryvnia
    "UYU",  # Uruguayan peso uruguayo
    "USD",  # US dollar
    "UZS",  # Uzbekistani sum
    "VUV",  # Vanuatu vatu
    "VEF",  # Venezuelan bolivar fuerte
    "VND",  # Vietnamese dong
    "YER",  # Yemeni rial
    "ZMK",  # Zambian kwacha
    "ZWL",  # Zimbabwe dollar
]

CURRENCY_SYMBOL = [
    r"A\$",  # A$
    r"AU\$",  # AU$
    r"C\$",  # C$
    "\u00A5",  # Yen(JPY)
    r"NZ\$",  # NZ$
    "\u20AC",  # Euro(EUR)
    "\u00A3",  # Pound(GBP)
    "kr",
    r"S\$",
    "K\u010D",  # Czech koruna
    r"HK\$",
    r"HK \$",
    r"CAD\$",
    r"Mex\$",
    "\u20A6",  # Naria sign
    "\u20B9",  # Rupee sign(INR),
    r"US\$",
    r"\$",  # $(USD)
]


class TimeCleanup:
    def to_numeric(self, time: str, granularity="min") -> int:
        """
        Convert runtime like 2h 35 min 35seconds
        """
        regex = r"((\d+)\s*(hours|hrs?|h)\s*)?(((\d+)\s*(minutes?|mins?|m)\s*)?((\d+)\s*(seconds?|secs?|s))?)?"

        total_runtime = 0
        total_seconds = 0

        matches = re.finditer(regex, time, re.IGNORECASE)
        if matches is None:
            return time

        for match in matches:
            hr, min, sec = match.group(2), match.group(6), match.group(9)

            if hr:
                total_runtime += int(hr) * 60
            if min:
                total_runtime += int(min)
            if sec:
                total_seconds += int(sec)

        if granularity == "sec":
            total_runtime = total_runtime * 60
            if total_seconds:
                total_runtime += total_seconds

        return total_runtime


class MonetaryCleanup:
    def large_num_names(self, value: str) -> str:
        """
        Replace large number names such as millions billions crores with
        their correct numeric representation

            Parameters:
                value: str      Convert large number names to numeric value

            Returns:
                String with numeric representation of the given number

            Examples:
                large_num_names('$1.25 million') -> '$1250000'
                large_num_names('Rs 15 crore (India)') 'Rs 150000000'
        """

        if type(value) != str:
            return

        regex = r"(\d+(\.\d+)?)\s*(-|\u2013)?(\s*\d+(\.\d+)?)?\s*(crores?|millions?|billions?|lakhs?)"
        group_count = 6
        match = re.search(regex, value, re.IGNORECASE)

        if value and match:

            if len(match.groups()) != group_count:
                return
            (low, x, _, high, y, factor) = match.groups()
            if factor.lower() == "lakh" or factor.lower() == "lakhs":
                mfactor = 100000
            if factor.lower() == "million" or factor.lower() == "millions":
                mfactor = 1000000
            if factor.lower() == "crore" or factor.lower() == "crores":
                mfactor = 10000000
            if factor.lower() == "billion" or factor.lower() == "billions":
                mfactor = 1000000000
            if low and high:
                # range of gross income
                value = re.sub(
                    regex,
                    f"{float(low)*mfactor}-{float(high)*mfactor}",
                    value,
                    flags=re.IGNORECASE,
                )
            if low and not high:
                # single value
                value = re.sub(
                    regex, str(float(low) * mfactor), value, flags=re.IGNORECASE
                )
            return value

        return value

    def extract_estimated_amount(self, value: str) -> str:
        """
        Extract the numeric/monetary part from a string

            Parameters:
                value: str      String to extract estimated amount from

            Returns:
                String of monetary value along with the currency abbr/symbol

            Examples:
                extract_estimated_amount('est. 927498732') -> '927498732'
                extract_estimated_amount('est. INR29727.97') -> 'INR29727.97'

            Note:
                This function does not accept monetary values in words like millions, billions.
                Hence for extract_estimated_amount("~$23989 million") -> "$23989"
                So large number names should be treated before using this function.
        """
        if type(value) != str:
            return

        currencies = "|".join([*CURRENCY_ABBR, *CURRENCY_SYMBOL])
        regex = r"(estimated\.?|est\.?|~)\s*({0})?\s*(\d+(\.\d+)?)".format(currencies)

        match = re.search(regex, value, re.IGNORECASE)

        if match is None:
            return value

        currency = match.group(2)
        amt = match.group(3)

        value = str(currency) + str(amt) if currency else str(amt)

        return value

    def remove_equivalent_amt(self, value: str) -> str:
        """
        Remove the amount equivalence statements from a string

            Parameters:
                value: str      String to remove equivalence statements from

            Returns:
                String with equivalent amount removed

            Examples:
                remove_equivalent_amt('1 crore (119 crore as of 2011)') -> '1 crore'
                remove_equivalent_amt('INR3274 (equivalent to  in 2016)') -> 'INR3274'
                remove_equivalent_amt('98779 (equivalent to  or  in 2019)') -> '98779'
                remove_equivalent_amt('₹89.2 crore (equivalent to ₹326 crore (US$46 million) in 2016)') -> '₹89.2 crore'
        """
        if type(value) != str:
            return

        regex = r"\(equivalent to.*?in (\d{4})?.*\)"

        if re.search(regex, value):
            modified_val = re.sub(regex, "", value, flags=re.IGNORECASE)
            return modified_val.strip()

        regex = r"\(equivalent to.*euros\)"
        if re.search(regex, value):
            modified_val = re.sub(regex, "", value, flags=re.IGNORECASE)
            return modified_val.strip()

        regex = r"\(\s?\d+\s?(crores?|millions?|billions?|euros?) as of \d{4}\s?\)"
        if re.search(regex, value, re.IGNORECASE):
            modified_val = re.sub(regex, "", value, flags=re.IGNORECASE)
            return modified_val.strip()

        return value

    def extract_series_collection(self, value: str) -> str:
        """
        Extract the amount given a string quoting amount of more than
        one entity

            Parameters:
                value: str      String to extract monetary value from

            Returns:
                String containing monetary value

            Examples:
                extract_series_collection('$106759044(Total of 2 films)') -> '$106759044'
                extract_series_collection('$2937437 (Total of 2 theatrical films)') -> '$2937437'
                extract_series_collection('$634450 (USA Gross Total)') -> '$634450'
                extract_series_collection('Total (2 films)$686.6 million') -> '$686.6 million'
                extract_series_collection('Total (1 film):$856.08 million') -> '$856.08 million'
                extract_series_collection('£160000 (Australia)£250000 (total)') -> '£160000'
                extract_series_collection('$218626 (USA) (sub-total)£2475758 (UK)') -> '$218626'
        """

        if type(value) != str:
            return

        currencies = "|".join([*CURRENCY_ABBR, *CURRENCY_SYMBOL])
        regex = rf"({currencies})\s*(\d+(\.\d+)?)"

        if (
            "total" in value.lower()
            or "cumulative" in value.lower()
            or "overall" in value.lower()
        ):
            match = re.search(regex, value, flags=re.IGNORECASE)

            if match:
                currency = match.group(1)
                amt = match.group(2)

                value = str(currency) + str(amt) if currency else str(amt)
                return value

        return value

    def money(self, value: str) -> str:
        """
        Extract monetary values from a string

            Parameters:
                value: str      String to extract monetary values from

            Returns:
                String of FIRST monetary value

            Examples:

                money('$389106 (non-USA)  €411480 (Spain) (20 December 2002)') -> '$389106'
                money('$689000000.0-791000000.0') -> '$689000000.0-791000000.0'
                money('$36122 (1995 US re-release only)') -> '$36122'
                money('$8234000  Industry  ByronStuart. Film Comment; New York Vol. 14Iss. 2(...') -> '$8234000'
        """
        currencies = r"|".join([*CURRENCY_ABBR, *CURRENCY_SYMBOL])
        single_regex = rf"({currencies})\s*(\d+(\.\d+)?)"
        range_regex = rf"({currencies})\s*(\d+(\.\d+)?)\s*-\s*(\1)?(\d+(\.\d+)?)"

        if type(value) != str:
            return

        # order and ELSE IF of match is important as singular will always
        # match in case of range of values as well
        range_match = re.search(range_regex, value, re.IGNORECASE)
        match = re.search(single_regex, value, re.IGNORECASE)

        if range_match:
            return range_match.group(0)
            # self.__collection__.update_one({'_id': item['_id']}, {'$set':{key: match.group(0)}})

        elif match:
            return match.group(0)
            # self.__collection__.update_one({'_id': item['_id']}, {'$set':{key: match.group(0)}})

        return value


def humanize_date(match):
    formatted = datetime.strptime(match, "%Y/%m/%d")
    return formatted.strftime("%d %B, %Y")


def normalize_date(date: list | tuple) -> str:
    """
    Given a date, return a formatted version of the
    date in yyyy/mm/dd format
        Parameters:
            date : str - Date in (yyyy,mm,dd) format or (yyyy,m,d) format

        Returns:
            str - date in yyyy/mm/dd  format
    """
    y, m, d = date
    if len(m) == 1:
        m = "0" + m
    if len(d) == 1:
        d = "0" + d
    date = f"{y}/{m}/{d}"
    return date


def str_to_list(string: str) -> list:
    """
    Convert a comma-separated string to an array of strings
    """
    if type(string) is not str:
        return string
    return [strng.strip() for strng in string.split(",")]


def normalize_str(value: str) -> str:
    """
    Apply different kinds of normalization and cleanup strategies on a string
        Parameters:
            value: str      String to apply normalization/cleaning on

        Returns:
            str             Normalized string
    """
    if type(value) is not str:
        return value

    value = value.strip()
    # remove links marked with [[ and ]] (Media Wiki template)
    if value.startswith("[[") or value.endswith("]]"):
        value = value.strip("[[").strip("]]")

    # remove any space at string start or end
    value = value.strip()
    # remove any , at string start or end
    if value.startswith(",") or value.endswith(","):
        value = value.strip(",")

    # remove line break tags
    value = re.sub(r"<\s?br(\s?\/)?\s?>", ", ", value, flags=re.I)
    # remove references marked with < ref > abcdefgh < /ref >
    value = re.sub(
        r"<\s*ref\s*([a-zA-Z0-9\s]+=\s?\\?\"?.*?\\?\"?\s?)?\/?\s?>(.*<\s*\/ref\s*>)?",
        "",
        value,
    )
    # remove comments
    value = re.sub(r"<\s?!--.*?--\s?>", "", value)
    # remove extra whitespace and remove new line feed
    value = value.replace(" , ", ", ").replace("\n", "")
    # remove incomplete comment tags at start or end
    value = value.strip("< !--").strip("-- >")
    # remove small tags as their content can be directly interpreted
    value = re.sub(r"<\s?small\s?>", "", value)
    value = re.sub(r"<\s?/\s?small", "", value)
    # remove & nbsp; from  value
    value = value.replace("& nbsp;", "")
    # remove extra spaces
    value = (
        value.replace(" , ", ", ")
        .replace(" ( ", " (")
        .replace(" ) ", ")")
        .replace(" ),", "), ")
    )
    value = re.sub(r"\s+", " ", value)
    return value


def extract_template_money(value: str):
    """
    In few instances, the MediaWiki code has template literals around actual values.
    For example, {{INR|90902090}} is the value of budget.
    In such cases, strip_code() removes the content completely and hence information is lost.

    This function extracts information between the template literals.
        Parameters:
            value: str      String to check for available template literals

        Returns:
            str             Extracted value
    """
    currencies = "|".join([*CURRENCY_ABBR, *CURRENCY_SYMBOL])
    regex = r"\{\{(" + rf"{currencies}" + r")\|[0-9,]+\}\}"
    match = re.search(regex, str(value))
    if match is None:
        value: str = value.strip_code().strip()
    else:
        value: str = match.group(0).strip().lstrip("{").rstrip("}")
        value = value.replace("|", " ")
    return value
