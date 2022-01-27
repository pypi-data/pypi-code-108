# coding: utf-8

# -----------------------------------------------------------------------------
# Уровень точности адреса: населенный пункт.
UI_LEVEL_PLACE = 1

# Уровень точности адреса: улица.
UI_LEVEL_STREET = 2

# Уровень точности адреса: дом.
UI_LEVEL_HOUSE = 3

# Уровень точности адреса: квартира.
UI_LEVEL_FLAT = 4

# Уровни точности адреса
UI_LEVELS = (
    UI_LEVEL_PLACE,
    UI_LEVEL_STREET,
    UI_LEVEL_HOUSE,
    UI_LEVEL_FLAT,
)

# -----------------------------------------------------------------------------
# Уровни адресных объектов ГАР.

# Субъект РФ
GAR_LEVEL_RF_REGION = 1

# Административный район
GAR_LEVEL_ADM_DISTRICT = 2

# Муниципальный район
GAR_LEVEL_MUN_DISTRICT = 3

# Сельское/городское поселение
GAR_LEVEL_SETTLEMENT = 4

# Город
GAR_LEVEL_CITY = 5

# Населенный пункт
GAR_LEVEL_LOCALITY = 6

# Элемент планировочной структуры
GAR_LEVEL_PLANNING_STRUCTURE = 7

# Элемент улично-дорожной сети
GAR_LEVEL_STREET = 8

# Земельный участок
GAR_LEVEL_STEAD = 9

# Здание (сооружение)
GAR_LEVEL_BUILDING = 10

# Помещение
GAR_LEVEL_ROOM = 11

# Помещения в пределах помещения
GAR_LEVEL_ROOM_IN_ROOM = 12

# Автономный округ (устаревшее)
GAR_LEVEL_AUTONOMOUS_DISTRICT = 13

# Внутригородская территория (устаревшее)
GAR_LEVEL_INTRACITY_TERRITORY = 14

# Дополнительные территории (устаревшее)
GAR_LEVEL_ADDITIONAL_TERRITORY = 15

# Объекты на дополнительных территориях (устаревшее)
GAR_LEVEL_ADDITIONAL_TERRITORY_OBJECT = 16

# Машино-место (устаревшее)
GAR_LEVEL_PARKING_PLACE = 17


# Уровни адресных объектов
GAR_LEVELS = (
    GAR_LEVEL_RF_REGION,
    GAR_LEVEL_ADM_DISTRICT,
    GAR_LEVEL_MUN_DISTRICT,
    GAR_LEVEL_SETTLEMENT,
    GAR_LEVEL_CITY,
    GAR_LEVEL_LOCALITY,
    GAR_LEVEL_PLANNING_STRUCTURE,
    GAR_LEVEL_STREET,
    GAR_LEVEL_STEAD,
    GAR_LEVEL_BUILDING,
    GAR_LEVEL_ROOM,
    GAR_LEVEL_ROOM_IN_ROOM,
    GAR_LEVEL_AUTONOMOUS_DISTRICT,
    GAR_LEVEL_INTRACITY_TERRITORY,
    GAR_LEVEL_ADDITIONAL_TERRITORY,
    GAR_LEVEL_ADDITIONAL_TERRITORY_OBJECT,
    GAR_LEVEL_PARKING_PLACE,
)

# Уровни адресных объектов, относящихся к населенным пунктам.
GAR_LEVELS_PLACE = (
    GAR_LEVEL_RF_REGION,
    GAR_LEVEL_MUN_DISTRICT,
    GAR_LEVEL_SETTLEMENT,
    GAR_LEVEL_CITY,
    GAR_LEVEL_LOCALITY,
    GAR_LEVEL_PLANNING_STRUCTURE,
)

# Уровни адресных объектов, относящимся к улицам.
GAR_LEVELS_STREET = (
    GAR_LEVEL_STREET,
)


# -----------------------------------------------------------------------------
# Виды иерархического деления ГАР.

# Иерархия в муниципальном делении
GAR_HIERARCHY_MUN = 'mun'

# Иерархия в административном делении
GAR_HIERARCHY_ADM = 'adm'


# Виды иерархического деления
GAR_HIERARCHIES = (
    GAR_HIERARCHY_MUN,
    GAR_HIERARCHY_ADM,
)

DEFAULT_PAGE_LIMIT = 20
