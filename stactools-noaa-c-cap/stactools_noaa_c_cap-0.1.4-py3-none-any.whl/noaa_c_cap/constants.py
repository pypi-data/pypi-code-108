from pystac.extensions.file import MappingObject
from pystac.provider import Provider, ProviderRole

COLLECTION_ID = 'noaa-c-cap'
COLLECTION_TITLE = 'C-CAP Regional Land Cover and Change'
COLLECTION_KEYWORDS = ['landcover', 'coastal', 'change']
COLLECTION_PROVIDERS = [
    Provider(name=('National Oceanic and Atmospheric Administration, '
                   'Office for Coastal Management'),
             roles=[
                 ProviderRole.LICENSOR, ProviderRole.PRODUCER,
                 ProviderRole.PROCESSOR, ProviderRole.HOST
             ],
             url='https://coast.noaa.gov/digitalcoast/data/ccapregional.html')
]
COLLECTION_DESCRIPTION = """Nationally standardized, raster-based inventories of
land cover for the coastal areas of the U.S.  Data are derived, through the
Coastal Change Analysis Program, from the analysis of multiple dates of remotely
sensed imagery.  Two file types are available: individual dates that supply a
wall-to-wall map, and change files that compare one date to another.

The use of standardized data and procedures assures consistency through time and
across geographies.  C-CAP data forms the coastal expression of the National
Land Cover Database (NLCD) and the A-16 land cover theme of the National Spatial
Data Infrastructure.  The data are updated every 5 years."""
LABEL_CLASSES = [
    "Background", "Unclassified (Cloud, Shadow, etc)",
    "High Intensity Developed", "Medium Intensity Developed",
    "Low Intensity Developed", "Developed Open Space", "Cultivated Land",
    "Pasture/Hay", "Grassland", "Deciduous Forest", "Evergreen Forest",
    "Mixed Forest", "Scrub/Shrub", "Palustrine Forested Wetland",
    "Palustrine Scrub/Shrub Wetland", "Palustrine Emergent Wetland",
    "Estuarine Forested Wetland", "Estuarine Scrub/Shrub Wetland",
    "Estuarine Emergent Wetland", "Unconsolidated Shore", "Bare Land",
    "Open Water", "Palustrine Aquatic Bed", "Estuarine Aquatic Bed", "Tundra",
    "Snow/Ice"
]
FILE_VALUES = list(
    MappingObject.create([i], name) for i, name in enumerate(LABEL_CLASSES))
COLLECTION_CITATION = (
    "National Oceanic and Atmospheric Administration, "
    "Office for Coastal Management. "
    "Name of Data Set: Coastal Change Analysis Program (C-CAP) Regional Land Cover. "
    "Charleston, SC: NOAA Office for Coastal Management. "
    "Accessed Month Year at www.coast.noaa.gov/htdata/raster1/landcover/bulkdownload/30m_lc/."
)
