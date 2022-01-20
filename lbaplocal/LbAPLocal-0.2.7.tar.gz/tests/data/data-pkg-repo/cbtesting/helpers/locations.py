
from Configurables import (
    DaVinci
)
import os


"""
get_line is a function to take as input
- Data or MC (is_mc)
- The dilepton mode (mode)
- Name of sample, formatted as {year}_{polarity}_MC_{decay}  ; needed for exceptions in stripping line names
and return the stripping line name
"""
import tags

def get_line(is_mc,lepton_mode,name=None):

    dem_in_eeline = False
    noPID_in_line = True
    if is_mc:
        line = tags.tags[name]['StrippingLine']
        if 'dem' in line: dem_in_eeline = True # ONLY REQUIREMENT FROM TAGS 
        line = line.split('_')[0]+'_'+lepton_mode+'Line'     

    elif not is_mc:     
        line = 'Bu2LLK_'+lepton_mode+'Line'

    if 'ee' in line: #  # EXCEPTIONS: EE LINE WHICH IS eeLine2 or eeLine_dem depending on sample
        if dem_in_eeline: line += '_dem'
        else:             line += '2'

    return line

"""
locations is a function to take as input
- Stripping stream
- Lepton mode (ee,mm,em)
- Sample_name (used to obtain info from tags)
- Is sample data/MC?
- Is sample MDST/DST?
- Does sample include upstream_electrons?
and return the location(s) to take candidates from + set DaVinci RootInTES for MDST
"""

def get_locations(stream, lepton_mode, sample_name, is_mc, is_mdst,upstream_electrons=False):

    # SET STREAM AND RootInTES IF NEEDED
    tes_root = '/Event/' + stream 
    if is_mdst:
        DaVinci().RootInTES = tes_root

    # Get stripping line
    stripping_line = get_line(is_mc,lepton_mode,sample_name)
    
    location = 'Phys/{}/Particles'.format(stripping_line)  
    if 'Radiative' in stream or not is_mdst:
        location = tes_root + '/' + location
    print("TEST", location)
    
    if upstream_electrons:
        location_upstream = 'Phys/Bu2LLK_eeLine4/Particles'
        if not is_mdst:
            location_upstream = tes_root + '/' + location_upstream
        return [location,location_upstream]
    else:
        return [location]
