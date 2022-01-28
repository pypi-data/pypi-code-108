from datetime import datetime

# Default Start and End Dates for GO Data
start_date = "2017-05-31"
end_date = datetime.now().strftime("%Y-%m-%d")

mosquito_protocol = "mosquito_habitat_mapper"
landcover_protocol = "land_covers"

region_dict = {
    "Africa": [
        "Benin",
        "Botswana",
        "Burkina Faso",
        "Cameroon",
        "Cape Verde",
        "Chad",
        "Congo DRC",
        "Ethiopia",
        "Gabon",
        "Gambia",
        "Ghana",
        "Guinea",
        "Kenya",
        "Liberia",
        "Madagascar",
        "Mali",
        "Mauritius",
        "Namibia",
        "Niger",
        "Nigeria",
        "Rwada",
        "Senegal",
        "Seychelles",
        "South Africa",
        "Tanzania",
        "Togo",
        "Uganda",
    ],
    "Asia and the Pacific": [
        "Australia",
        "Bangladesh",
        "Fiji",
        "India",
        "Japan",
        "Maldives",
        "Marshall Islands",
        "Micronesia",
        "Mongolia",
        "Nepal",
        "New Zealand",
        "Palau",
        "Philippines",
        "Republic of Korea",
        "Sri Lanka",
        "Taiwan Partnership",
        "Thailand",
        "Vietnam",
    ],
    "Latin America and Caribbean": [
        "Argentina",
        "Bahamas",
        "Burmuda",
        "Bolivia",
        "Brazil",
        "Chile",
        "Colombia",
        "Costa Rica",
        "Dominican Republic",
        "Ecuador",
        "El Salvador",
        "Guatemala",
        "Honduras",
        "Mexico",
        "Panama",
        "Paraguay",
        "Peru",
        "Suriname",
        "Trinidad and Tobago",
        "Uruguay",
    ],
    "Europe and Eurasia": [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Cyprus",
        "Czech Republic",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Georgia",
        "Germany",
        "Greece",
        "Hungary",
        "Iceland",
        "Ireland",
        "Israel",
        "Italy",
        "Kazakhstan",
        "Kyrgyz Republic",
        "Latvia",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Moldovia",
        "Montenegro",
        "Netherlands",
        "North Macedonia",
        "Norway",
        "Poland",
        "Portugal",
        "Romania",
        "Russia",
        "Serbia",
        "Slovak Republic",
        "Spain",
        "Sweden",
        "Switzerland",
        "Turkey",
        "Ukraine",
        "United Kingdom",
    ],
    "Near East and North Africa": [
        "Bahrain",
        "Egypt",
        "Jordan",
        "Kuwait",
        "Lebanon",
        "Mauritania",
        "Morocco",
        "Oman",
        "Pakistan",
        "Qatar",
        "Saudi Arabia",
        "Tunisia",
        "United Arab Emirates",
    ],
    "North America": ["Canada", "United States"],
}

abbreviation_dict = {
    mosquito_protocol: "mhm",
    landcover_protocol: "lc",
}

__doc__ = """
Useful stored values for GLOBE Observer scripts

Stored Values
-------------
- mosquito_protocol: the string used in the GLOBE API for the Mosquito Habitat Mapper protocol
- landcover_protocol: the string used in the GLOBE API for the Land Cover Protocol.
- start_date: the default starting date of GLOBE Obsever data requests in YYYY-MM-DD Form.
- end_date: the current date in YYYY-MM-DD Form.
- regions_dict: contains all the different GLOBE regions and the countries associated with each region
"""
