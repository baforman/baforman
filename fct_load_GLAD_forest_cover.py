# Function used to import forest cover percent estimates from
# the Global Land Analysis Dataset (GLAD) product.
#
# Author:   Bart Forman
# Created:  12 Sep 2021
# Modified: 13 Sep 2021 -- introduced use of global variable(s)

def fct_load_GLAD_forest_cover(domain):
#def fct_load_GLAD_forest_cover(): # <-- WORK ON THIS

    # Define global variable(s) <-- WORK ON THIS
    #global domain, latlim, lonlim

    ## Import libraries
    import os
    import sys
    import numpy as np
    import xarray as xr

    # Load user-defined function(s) <-- OLD VERSION
    #sys.path.append(r'/Users/bartforman/Documents/PYTHON') <-- Q: Is this needed?
    from fct_collect_spatial_domain_coordinates import fct_collect_spatial_domain_coordinates

    # Determine lat/lon limits based on domain specification
    latlim, lonlim = fct_collect_spatial_domain_coordinates(domain)

    # Load GLAD forest cover
    filename_GLAD = '/Volumes/Data_Repository/GLAD_Forest_Cover/Processed_Data/Merged_Files/GLAD_2010_0p01deg.nc'
    print("Loading file:",filename_GLAD)
    DS = xr.open_dataset(filename_GLAD)
    #print(DS.var) # echo general information
    # Prepare geolocation arrays
    print("Collecting GLAD geolocation arrays ... please be patient.")
    lat2D_GLAD = DS.lat # 2D
    lon2D_GLAD = DS.lon # 2D
    lat_GLAD = DS.lat.isel( north_south=[0] ) # contains singular dimension
    lat_GLAD = np.squeeze(lat_GLAD) # remove singular dimension
    lon_GLAD = DS.lon.isel( east_west=[0] ) # contains singular dimension
    lon_GLAD = np.squeeze(lon_GLAD) # remove singular dimension
    # Find indices within specified lat/lon limits
    boolean_array_GLAD = np.logical_and(lat_GLAD >= latlim[0], lat_GLAD <= latlim[1] )
    ind_lat_GLAD = np.where(boolean_array_GLAD)[0]
    boolean_array_GLAD = np.logical_and(lon_GLAD >= lonlim[0], lon_GLAD <= lonlim[1] )
    ind_lon_GLAD = np.where(boolean_array_GLAD)[0]
    # Load state variable(s) of interest
    print("Importing variables ... please be patient.")
    forest_cover = DS.Forest_Cover_Percent
    #print("Min. Value =",np.nanmin(forest_cover)) # echo min. value
    #print("Max. Value =",np.nanmax(forest_cover)) # echo max. value
    print("Replacing 0's with NaN values ... ")
    forest_cover = xr.where( forest_cover==0, np.NaN, forest_cover)
    #print() # add extra space
    # Save "clipped" domain for later use
    print("Processing 'clipped' domain for basin of interest ... ")
    lat_GLAD_clipped = lat_GLAD[ind_lat_GLAD] # 1D
    lon_GLAD_clipped = lon_GLAD[ind_lon_GLAD] # 1D
    #lon2D_GLAD_clipped, lat2D_GLAD_clipped = np.meshgrid(lon_GLAD_clipped,lat_GLAD_clipped)
    lat2D_GLAD_clipped, lon2D_GLAD_clipped = np.meshgrid(lat_GLAD_clipped,lon_GLAD_clipped) # reversed
    forest_cover_clipped = forest_cover[ind_lon_GLAD,ind_lat_GLAD]
    DS.close() # close file
    print() # add extra space
    #endregion

    # Save clipped array(s) to structured array format
    result = xr.DataArray(
        data=forest_cover_clipped, # original
        dims=["x","y"],
        coords=dict(lon=(["x", "y"],lon2D_GLAD_clipped),lat=(["x", "y"],lat2D_GLAD_clipped)),
        attrs=dict(
            long_name="forest_cover_percent",
            description="Percent Forest Cover",
            units="%",
            ),
        )
    #print(result.var)

    return result
