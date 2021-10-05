"""
Function used to plot georeferenced array using matplotlib.pyplot and geopandas.

Author:   Bart Forman
Created:  27 Aug 2021
Modified:  6 Sep 2021 -- incorporated new "world map" database via shapefile import
"""

## Create domain-specific map
#def fct_map_global(ax,domain,lon2D,lat2D,Z_2D,clims,custom_colors,colorbar_string,title_string): # OLD VERSION
def fct_map_global(ax,domain,plot_type,lon2D,lat2D,Z_2D,clims,custom_colors,custom_levels,colorbar_string,title_string):

    ## Import libraries
    #print('Loading local libraries ...')
    import os
    import matplotlib.pyplot as plt
    from matplotlib import cm
    import numpy as np
    import geopandas as gpd
    from matplotlib import colors

    # Load user-defined function(s)
    from fct_collect_spatial_domain_coordinates import fct_collect_spatial_domain_coordinates

    # Determine lat/lon limits
    latlim, lonlim = fct_collect_spatial_domain_coordinates(domain)

    # Load shapefile of U.S. state outlines
    state_outlines = gpd.read_file("/Users/bartforman/Documents/MATLAB/Utilities/state_outlines.shp")
    #type(state_outlines)
    #state_outlines.head()
    #state_outlines.crs

    # Load shapefile of international outlines
    intl_outlines = gpd.read_file("/Volumes/Data_Repository/ArcGIS_Files/IPUMSI_world_release2020/world_countries_2020.shp")
    #type(intl_outlines)
    #intl_outlines.head()
    #intl_outlines.crs

    # Load GRDC basin outlines
    GRDC_405_basins_from_mouth = gpd.read_file("/Volumes/Data_Repository/ArcGIS_Files/GRDC_Shapefiles/GRDC_405_basins_from_mouth.shp")
    GRDC_687_rivers = gpd.read_file("/Volumes/Data_Repository/ArcGIS_Files/GRDC_Shapefiles/GRDC_687_rivers.shp")

    # Set aspect of the axes
    ax.set_aspect('equal')

    # Add international and U.S. state outlines
    intl_outlines.boundary.plot(ax=ax, color='k', linewidth=0.70, alpha=0.3)
    state_outlines.boundary.plot(ax=ax, color='k', linewidth=0.40, alpha=0.2)

    # Add GRDC basin outlines
    GRDC_405_basins_from_mouth.boundary.plot(ax=ax, color='b', linewidth=0.2, alpha=0.8)

    # Add GRDC rivers
##### need to clean up *.shp file #####
#    GRDC_687_rivers.boundary.plot(ax=ax, color='c', linewidth=0.3, alpha=0.8) # works!

    # Choose plot type
    if plot_type == 'contourf':
        # Generate "contourf" plot
        p = plt.contourf(
            lon2D,
            lat2D,
            Z_2D,
            #vmin = -6, # does *not* work
            #vmax = 6, # does *not* work
            levels = custom_levels,
            cmap = custom_colors,
            )
        # Add colorbar
        cb = plt.colorbar(p, 
            ax=ax,
            orientation = 'horizontal',
            pad = 0.10, # nudge upward (default=0.15 for horizontal)
            label=colorbar_string)

    elif plot_type == 'pcolormesh':
        # Generate "pcolormesh" plot
        if clims[0] == 0:
            #extension_string = 'max'
            extension_string = 'neither'
        else:
            extension_string = 'both'
        divnorm = colors.TwoSlopeNorm(
            vmin = clims[0],
            #vcenter = 0.,
            vcenter = (clims[1]-clims[0])/2 + clims[0],
            vmax = clims[1])
        p = plt.pcolormesh(
            lon2D,
            lat2D,
            Z_2D,
            shading = 'nearest',
            cmap = custom_colors,
            norm = divnorm # enable continuous colorbar
            )
        # Add colorbar
        cb = plt.colorbar(p,
            ax = ax,
            orientation = 'horizontal',
            pad = 0.10, # nudge upward (default=0.15 for horizontal)
            label = colorbar_string,
            extend = extension_string
            )

###### work on "low resolution" equivalent #####
    #elif plot_type == 'imagesh':

    # Set axis limits
    ax.set_xlim(lonlim) #ax.set_xlim([lonlim[0],lonlim[1]]) # works!
    ax.set_ylim(latlim) #ax.set_ylim([latlim[0],latlim[1]]) # works!
    # #ax.set_xticklabels([]) # remove axis labels
    # #ax.set_yticklabels([]) # remove axis labels

    # Add grid lines
    plt.grid(color='gray', linestyle='--', linewidth=0.25, alpha=0.90) # turn on grid lines

    # Modify axis spacing (as desired)
    if domain == 'Klamath':
        delta_lat_lon = 1.0
        plt.xticks(np.arange(lonlim[0],lonlim[1]+delta_lat_lon,delta_lat_lon))
        plt.yticks(np.arange(latlim[0],latlim[1]+delta_lat_lon,delta_lat_lon))
    # else:
    #     # do nothing
    #     junk = 2

    # Add figure title
    #plt.title(title_string)
    plt.title(title_string,loc='left')
    