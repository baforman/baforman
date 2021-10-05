# Function used to define the spatial coordinates (i.e., domain extent) based
# on an input string abbreviation.
#
# Author:   Bart Forman

# Collect geolocation limits based on the "domain"
def fct_collect_spatial_domain_coordinates(domain):

    ## Import libraries
    #print('Loading local libraries ...')
    import os
    import sys
    import numpy as np

    ## Determine lat/lon limits
    if domain == 'Global' or domain == 'global':
        latlim = np.array([-90, 90]) # [deg] -- clipped
        #latlim = np.array([-60, 80]) # [deg]
        lonlim = np.array([-180, 180]) # [deg]
    elif domain == 'NH': # northern hemisphere
        latlim = np.array([25, 90]) # [deg] -- clipped
        #latlim = np.array([0, 90]) # [deg]
        lonlim = np.array([-180, 180]) # [deg]
    elif domain == 'NA': # North America
        latlim = np.array([20, 72]) # [deg]
        #latlim = np.array([32, 72]) # [deg] -- clipped for snow
        lonlim = np.array([-175, -50]) # [deg]
    elif domain == 'CONUS':
        latlim = np.array([24, 51]) # [deg]
        lonlim = np.array([-130, -65]) # [deg]
    elif domain == 'Western_CONUS':
        latlim = np.array([27, 50]) # [deg]
        lonlim = np.array([-130, -100]) # [deg]
    elif domain == 'Kashmir_Valley':
        latlim = np.array([32, 36]) # [deg]
        lonlim = np.array([72, 76]) # [deg]
    elif domain == 'Indus':
        #latlim = np.array([21, 40]) # [deg] -- relaxed
        #lonlim = np.array([65, 86]) # [deg] -- relaxed
        latlim = np.array([22.0250, 38.9750]) # [deg]
        lonlim = np.array([66.0250, 84.9750]) # [deg]
    elif domain == 'HMA':
        #latlim = np.array([5, 45]) # [deg] -- India centric
        #lonlim = np.array([60, 100]) # [deg] -- India centric
        #latlim = np.array([25, 45]) # [deg] -- Snow centric
        #lonlim = np.array([60, 100]) # [deg] -- Snow centric
        #latlim = np.array([20.8750, 40.8750]) # [deg] -- tight
        #lonlim = np.array([65.8750, 100.8750]) # [deg] -- tight
        latlim = np.array([27, 45]) # [deg] -- UCLA SWE
        lonlim = np.array([60, 105]) # [deg] -- UCLA SWE
    elif domain == 'India':
        latlim = np.array([6, 41]) # [deg]
        lonlim = np.array([60, 100]) # [deg]
    elif domain == 'Krishna_Basin':
        latlim = np.array([13, 20]) # [deg]
        lonlim = np.array([73, 82]) # [deg]
    elif domain == 'Tuolumne':
        latlim = np.array([37.6299, 38.2815]) # [deg]
        lonlim = np.array([-120.6264,-119.1520]) # [deg]
    elif domain == 'Upper_Tuolumne':
        latlim = np.array([37.7167, 38.2046]) # [deg]
        lonlim = np.array([-119.8200, -119.1592]) # [deg]
    elif domain == 'Congo':
        latlim = np.array([-14, 10]) # [deg]
        lonlim = np.array([11, 35]) # [deg]
    elif domain == 'Klamath':
        latlim = np.array([40, 44]) # [deg]
        lonlim = np.array([-125, -120]) # [deg]
    else:
        sys.exit("Unknown domain "+domain+" specified ... please double-check.")

    ## Debugging
    #print(latlim)
    #print(lonlim)

    # Return output argument(s)
    return latlim, lonlim
