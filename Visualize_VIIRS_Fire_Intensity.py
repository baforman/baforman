#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Script used to visualize processed VIIRS-detected burn areas.
#
# Author:   Bart Forman
# Created:  11 Sep 2021

# %% Clear command window and import libraries
#region
import os
os.system('clear') # clear command window
print() # add extra space
import sys
import time
tic = time.perf_counter() # start timer
import matplotlib.pyplot as plt
from matplotlib import cm
#from mpl_toolkits.basemap import Basemap # does *not* work in Jupyter
import numpy as np
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import pandas as pd
import geopandas as gpd
import math
import pickle
import xarray as xr
import glob
import datetime
#endregion

# %% User-defined input variable(s)
#start_date = datetime.date(2021,7,1)
# finish_date = start_date + datetime.timedelta(days=1) # TESTING
start_date = datetime.date(2021,10,3) # RECENT
#finish_date = datetime.date(2021,9,21) # TESTING
finish_date = datetime.date.today() # stops *before* this date
domain = 'Klamath'
#domain = 'Western_CONUS'
#domain = 'CONUS'

print()
print("Start date set to "+start_date.strftime('%Y%m%d'))
print("Finish date set to "+finish_date.strftime('%Y%m%d'))
print("Domain set to "+domain)
print()

# %% Load user-defined function(s) <-- OLD VERSION
#sys.path.append(r'/Users/bartforman/Documents/PYTHON') # <-- Q: no longer needed?
from fct_MAPS import fct_map_global
from fct_collect_spatial_domain_coordinates import fct_collect_spatial_domain_coordinates
from fct_load_GLAD_forest_cover import fct_load_GLAD_forest_cover

# %% Load user-defined function(s) <-- does *not* work
# import mypythonlib
# from mypythonlib import myfunctions

# # Save module requirements for later use
# pip freeze > requirements.txt

# %% Determine lat/lon limits based on domain specification
latlim, lonlim = fct_collect_spatial_domain_coordinates(domain)

# Load GLAD forest cover product
GLAD_array = fct_load_GLAD_forest_cover(domain)
#GLAD_array = fct_load_GLAD_forest_cover() # <-- WORK ON THIS

# Search for preprocessed (via Matlab) VIIRS NetCDF files
if domain == 'Klamath':
    dir_storage = 'Processed_Data/NetCDF_Output/Klamath/' # 500-meter
else:
    dir_storage = 'Processed_Data/NetCDF_Output/Global/' # 0.04-degree

# %% Loop through available NetCDF files (DISABLED -- OLD HEADER) #####
# file_search = 'Fire_Intensity_*'
# files = glob.glob(dir_storage+file_search)
# #os.system('ls '+dir_storage+file_search) # debugging
# for f in sorted(files):

# %% Start temporal loop
current_date = start_date # initialize
while current_date < finish_date:

    # %% Load preprocessed VIIRS file
    #region
    f = dir_storage+'Fire_Intensity_'+current_date.strftime('%Y')+current_date.strftime('%m')+current_date.strftime('%d')+".nc"
    print("Loading file:",f)
    print(os.getcwd())
    DS = xr.open_dataset(f)
    #print(DS.var) # echo general information
    #print()

    # Prepare geolocation arrays (only need to do once)
    if current_date == start_date:
        print("Collecting VIIRS geolocation arrays ... please be patient.")
        lat2D_VIIRS = DS.lat # 2D
        lon2D_VIIRS = DS.lon # 2D
        lat_VIIRS = DS.lat.isel( north_south=[0] ) # contains singular dimension
        lat_VIIRS = np.squeeze(lat_VIIRS) # remove singular dimension
        lon_VIIRS = DS.lon.isel( east_west=[0] ) # contains singular dimension
        lon_VIIRS = np.squeeze(lon_VIIRS) # remove singular dimension
        print("Determining indices within lat/lon limits ...")
        boolean_array_VIIRS = np.logical_and(lat_VIIRS >= latlim[0], lat_VIIRS <= latlim[1] )
        ind_lat_VIIRS = np.where(boolean_array_VIIRS)[0]
        boolean_array_VIIRS = np.logical_and(lon_VIIRS >= lonlim[0], lon_VIIRS <= lonlim[1] )
        ind_lon_VIIRS = np.where(boolean_array_VIIRS)[0]
        print("Saving 'clipped' geolocation arrays for later use ...")
        lat_VIIRS_clipped = lat_VIIRS[ind_lat_VIIRS] # 1D
        lon_VIIRS_clipped = lon_VIIRS[ind_lon_VIIRS] # 1D
        #lon2D_VIIRS_clipped, lat2D_VIIRS_clipped = np.meshgrid(lon_VIIRS_clipped,lat_VIIRS_clipped)
        lat2D_VIIRS_clipped, lon2D_VIIRS_clipped = np.meshgrid(lat_VIIRS_clipped,lon_VIIRS_clipped) # reversed

    # Load state variable(s) of interest
    print("Importing variables ... please be patient.")
    fire_intensity = DS.Fire_Intensity
    #print("Min. Value =",np.nanmin(fire_intensity)) # echo min. value
    #print("Max. Value =",np.nanmax(fire_intensity)) # echo max. value
    #print("Replacing 0's with NaN values ... ")
    fire_intensity = xr.where( fire_intensity==0, np.NaN, fire_intensity)

    # Save "clipped" domain for later use
    #print("Processing 'clipped' domain for basin of interest ... ")
    fire_intensity_clipped = fire_intensity[ind_lon_VIIRS,ind_lat_VIIRS]
    DS.close() # close file

    # Determine number of active pixels (fires)
    nfires = np.count_nonzero(~np.isnan(fire_intensity_clipped))
    
    #endregion

    # ----- Graphical Output -----
    print("Starting graphical output ... ")

    # %% VIIRS fire intensity ---

    # %%
    #region
    plt.close('all') # close existing figure window(s)
    print("   Generating map of VIIRS burn area(s) ... ")

    fig = plt.figure(figsize=(4,4), dpi=300) # [W H] --> Good Size
    ax = fig.add_subplot(1,1,1)

    # Add VIIRS fire intensity
    plot_type = 'contourf' # interpolation issues on 2021-07-19
    #plot_type = 'pcolormesh'
    clims = [0, 3] # colorbar limits
    #custom_levels = range(0,3+1,1) # integer
    custom_levels = np.arange(0.0,3.0+1,1.0) # floating point
    custom_colors = cm.Reds
    colorbar_string = 'Fire Intensity [1=Low; 2=Nominal; 3=High]'
    title_string = str(current_date)+" (# of events="+str(nfires)+")"
#f"{i:0>2}
#print(f'{number:05d}')
    fct_map_global(
        ax,domain,plot_type,
        lon2D_VIIRS_clipped,lat2D_VIIRS_clipped,fire_intensity_clipped,
        clims,custom_colors,custom_levels,
        colorbar_string,title_string)

    ## Save figure to output file
    #print("      Saving figure to output file ... please be patient.")
    ax.set_aspect('equal')
    plt.tight_layout()
    output_filename = "Images/Daily_Fire_Intensity/Python_Version/Map_of_Fire_Intensity_"+domain+"_"+str(current_date)+".jpg"
    fig.savefig(output_filename, dpi = 300) # save figure
    plt.close('all') # close existing figure window(s)
    #print() # add extra space
    #endregion

    # %% GLAD w/ daily VIIRS overlay
    #region
    plt.close('all') # close existing figure window(s)
    print("   Generating map of GLAD w/ daily VIIRS overlay ... ")

    fig = plt.figure(figsize=(4,4), dpi=300) # [W H] --> Good Size
    ax = fig.add_subplot(1,1,1)

    # Add GLAD forest cover
    plot_type = 'pcolormesh'
    clims = [0, 100] # colorbar limits
    #custom_levels = range(0,3+1,1) # integer
    #custom_levels = np.arange(0.0,3.0+1,1.0) # floating point
    custom_colors = cm.Greens
    colorbar_string = 'Forest Cover [%]'
    title_string = str(current_date)
    fct_map_global(
        ax,domain,plot_type,
        GLAD_array['lon'],GLAD_array['lat'],GLAD_array,
        clims,custom_colors,custom_levels,
        colorbar_string,title_string)

    ## Overlay VIIRS fire occurrence
    #print("Adding VIIRS overlay ... please be patient.")
    p = ax.contourf(
        lon2D_VIIRS_clipped,
        lat2D_VIIRS_clipped,
        fire_intensity_clipped,
        cmap = 'Reds',
        #cmap = 'red', # single color <-- does not work
        #hatches=['xxxxxxxx'],
        levels=[0,3],
        #levels=[0,1],
        #alpha=0.3 # 0=transparent; 1=opaque;
        alpha=1.0 # 0=transparent; 1=opaque;
        )
    #plt.rcParams['hatch.linewidth'] = 0.5
    #proxy = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0], hatch=pc.get_hatch()) for pc in p.collections] # face color + hatching
    proxy = [plt.Rectangle((0,0),1,1,fc = pc.get_facecolor()[0]) for pc in p.collections] # face color *only*
    plt.legend(proxy,["active fire"],loc='upper right',frameon=True)

    ## Save figure to output file
    #print("      Saving figure to output file ... please be patient.")
    ax.set_aspect('equal')
    plt.tight_layout()
    output_filename = "Images/Forest_Cover_with_Fire_Demarcators/Python_Version/GLAD_with_VIIRS_overlay_"+domain+"_"+str(current_date)+".jpg"
    fig.savefig(output_filename, dpi = 300) # save figure
    plt.close('all') # close existing figure window(s)
    print() # add extra space
    #endregion

    # Increment current_date to the next day
    current_date += datetime.timedelta(days=1)

# %% GLAD w/ time-integrated VIIRS overlay
#region

# Load time-integrated VIIRS file
VIIRS_date_string_integrated = '2021152_to_2021279'
f = dir_storage+'Time_Integrated_Fire_Intensity_'+VIIRS_date_string_integrated+".nc"
print("Loading file:",f)
DS = xr.open_dataset(f)
#print(DS.var) # echo general information
#print()

# # Prepare geolocation arrays (only need to do once)
# if current_date == start_date:
#     print("Collecting VIIRS geolocation arrays ... please be patient.")
#     lat2D_VIIRS = DS.lat # 2D
#     lon2D_VIIRS = DS.lon # 2D
#     lat_VIIRS = DS.lat.isel( north_south=[0] ) # contains singular dimension
#     lat_VIIRS = np.squeeze(lat_VIIRS) # remove singular dimension
#     lon_VIIRS = DS.lon.isel( east_west=[0] ) # contains singular dimension
#     lon_VIIRS = np.squeeze(lon_VIIRS) # remove singular dimension
#     print("Determining indices within lat/lon limits ...")
#     boolean_array_VIIRS = np.logical_and(lat_VIIRS >= latlim[0], lat_VIIRS <= latlim[1] )
#     ind_lat_VIIRS = np.where(boolean_array_VIIRS)[0]
#     boolean_array_VIIRS = np.logical_and(lon_VIIRS >= lonlim[0], lon_VIIRS <= lonlim[1] )
#     ind_lon_VIIRS = np.where(boolean_array_VIIRS)[0]
#     print("Saving 'clipped' geolocation arrays for later use ...")
#     lat_VIIRS_clipped = lat_VIIRS[ind_lat_VIIRS] # 1D
#     lon_VIIRS_clipped = lon_VIIRS[ind_lon_VIIRS] # 1D
#     #lon2D_VIIRS_clipped, lat2D_VIIRS_clipped = np.meshgrid(lon_VIIRS_clipped,lat_VIIRS_clipped)
#     lat2D_VIIRS_clipped, lon2D_VIIRS_clipped = np.meshgrid(lat_VIIRS_clipped,lon_VIIRS_clipped) # reversed

# Load state variable(s) of interest
print("Importing variables ... please be patient.")
fire_intensity = DS.Fire_Intensity
#print("Min. Value =",np.nanmin(fire_intensity)) # echo min. value
#print("Max. Value =",np.nanmax(fire_intensity)) # echo max. value
#print("Replacing 0's with NaN values ... ")
fire_intensity = xr.where( fire_intensity==0, np.NaN, fire_intensity)

# Save "clipped" domain for later use
#print("Processing 'clipped' domain for basin of interest ... ")
fire_intensity_clipped = fire_intensity[ind_lon_VIIRS,ind_lat_VIIRS]
DS.close() # close file

plt.close('all') # close existing figure window(s)
print("   Generating map of GLAD w/ time-integrated VIIRS overlay ... ")

fig = plt.figure(figsize=(4,4), dpi=300) # [W H] --> Good Size
ax = fig.add_subplot(1,1,1)

# Add GLAD forest cover
plot_type = 'pcolormesh'
clims = [0, 100] # colorbar limits
#custom_levels = range(0,3+1,1) # integer
#custom_levels = np.arange(0.0,3.0+1,1.0) # floating point
custom_colors = cm.Greens
colorbar_string = 'Forest Cover [%]'
title_string = '' # leave empty
fct_map_global(
    ax,domain,plot_type,
    GLAD_array['lon'],GLAD_array['lat'],GLAD_array,
    clims,custom_colors,custom_levels,
    colorbar_string,title_string)

## Overlay VIIRS fire occurrence
#print("Adding VIIRS overlay ... please be patient.")
p = ax.contourf(
    lon2D_VIIRS_clipped,
    lat2D_VIIRS_clipped,
    fire_intensity_clipped,
    cmap = 'Reds',
    hatches=['xxxxxxxx'],
    levels=[0,3],
    #levels=[0,1],
    alpha=0.2 # 0=transparent; 1=opaque;
    #alpha=1.0 # 0=transparent; 1=opaque;
    )
plt.rcParams['hatch.linewidth'] = 0.5
proxy = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0], hatch=pc.get_hatch()) for pc in p.collections] # face color + hatching
#proxy = [plt.Rectangle((0,0),1,1,fc = pc.get_facecolor()[0]) for pc in p.collections] # face color *only*
plt.legend(proxy,["burned areas"],loc='upper right',frameon=True)

## Save figure to output file
#print("      Saving figure to output file ... please be patient.")
ax.set_aspect('equal')
plt.tight_layout()
output_filename = "Images/Forest_Cover_with_Fire_Demarcators/Python_Version/GLAD_with_VIIRS_overlay_"+domain+"_"+VIIRS_date_string_integrated+".jpg"
fig.savefig(output_filename, dpi = 300) # save figure
plt.close('all') # close existing figure window(s)
print() # add extra space
#endregion

# %% Echo computational run-time
toc = time.perf_counter()
print() # add extra space
print(f"Computational run-time was {(toc - tic)/60:4.2f} minutes")
print() # add extra space 
