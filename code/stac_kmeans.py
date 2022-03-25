# %%
import folium
from streamlit_folium import folium_static
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy
import pandas
import pystac_client
import rasterio
from rasterio import warp
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

# %%
# Get the less cloudy image, the clipping window around a given a point, and its transform object
def get_less_cloudy_image(coords, start_date, end_date, max_cloud_cover=10, npixels=100, plotimage=False):
    """
    Read the Sentinel-2 STAC catalogue and return the best image (i.e. less cloud coverage), at the
    specified location and using the given start and end dates.

    INPUT   -   coords:             List with [Lon, Lat] coordinates
            -   start_date:         Start date as a string with format "YYYY-MM-DD" 
            -   end_date:           End date as a string with format "YYYY-MM-DD" 
            -   max_cloud_cover:    Integer between 0-100
            -   npixels:            Number of pixels that defines the size of the image
            -   plotimage:          Plot the less cloudy image (True/False)
    OUTPUT  -   best_image:         Less cloudy image
            -   window:             Object for extracting the image subset
            -   transform:          Object for georeferencing the image subset
            -   bounds:             Lon/Lat bounds coordinates
    """
    # API
    catalog_url = "https://earth-search.aws.element84.com/v0"
    catalog = pystac_client.Client.open(catalog_url)

    # Image retrieval parameters
    intersects_dict = dict(type="Point", coordinates=coords)
    dates = start_date + "/" + end_date
    filters = {"eo:cloud_cover":dict(lt=max_cloud_cover),
               "sentinel:valid_cloud_cover": {"eq": True}}

    # Search the Sentinel-2 COGs catalog
    search = catalog.search(
        collections=["sentinel-s2-l2a-cogs"],
        intersects=intersects_dict,
        datetime=dates,
        query=filters)
    
    # Sort items by cloud cover and return the less cloudy image
    if search.matched() > 0:
        best_image = sorted(search.get_all_items(), key=lambda item: item.properties["eo:cloud_cover"])[0]

        # Read band 8 and calculate the clipping window
        with rasterio.open(best_image.assets["B08"].href) as img:

            # Extract raster parameters
            ncols, nrows = img.width, img.height
            sref = img.crs

            # Transform Lon/Lat to the image CRS
            sref_wgs84 = rasterio.crs.CRS.from_epsg(4326)
            x, y = warp.transform(sref_wgs84, sref, [coords[0]], [coords[1]])
            row, col = rasterio.transform.rowcol(img.transform, x[0], y[0])

            # Enforce npixels is less than the image size
            if (npixels*2 > ncols) or (npixels*2 > nrows):
                npixels = min(nrows/4, ncols/4)

            # Define rasterio window
            row_start = row - npixels
            row_stop = row + npixels
            col_start = col - npixels
            col_stop = col + npixels
            window = rasterio.windows.Window.from_slices((row_start, row_stop), (col_start, col_stop))
            
            # Create the transform object for the subset area
            transform = img.window_transform(window)

            # Plot the image band
            if plotimage:
                plt.imshow(img.read(1), cmap='Greys_r')
                plt.scatter([col],[row], s=200, c='yellow', marker='+')
                plt.axis('off')

        # Return image, the clipping window, and its transform object
        return best_image, window, transform
    else:
        print("No images found. Change search parameters")
        return None, None, None


# %%
# Read a subset of the image bands and create an array
def read_sentinel2(best_image, window, transform, plotimage=False):
    """
    Read a subset of the best satellite image and return a numpy array
    for the clustering process.

    INPUT   -   best_image:     COG image selected using the API (pystac item)
            -   window:         Rasterio's Window object that defines the clipping boundary
            -   plotimage:      Plot the clipped satellite image (True/False)

    OUTPUT  -   image_array:    3D numpy array with the clipped image
    """
    # Sentinel-2 10-m bands
    bands = [2, 3, 4, 8]

    # Create an empty array to store each band as a column
    arr = numpy.empty((0))

    # Loop through the bands
    for b in bands:

        # Create band name string
        band_name = 'B'+ str(b).zfill(2)

        # Get the url to the COG
        asset_url = best_image.assets[band_name].href

        # Open the COG image
        with rasterio.open(asset_url) as img:

            # Read only the pixels inside the window
            img_arr = img.read(1, window=window)

            # Extract windowed image bounds
            sref = img.crs
            sref_wgs84 = rasterio.crs.CRS.from_epsg(4326)
            bounds_utm = rasterio.transform.array_bounds(img_arr.shape[0], img_arr.shape[1], transform)
            image_bounds = warp.transform(sref, sref_wgs84, [bounds_utm[0], bounds_utm[2]], [bounds_utm[1], bounds_utm[3]])

            # Reshape and append each band
            arr = numpy.append(arr, img_arr.flatten())

    
    # Reshape array
    image_array = arr.reshape(len(bands), img_arr.shape[0], img_arr.shape[1])

    if plotimage:
        plt.imshow(img_arr, cmap='Greys_r')
        plt.axis('off')
    
    return image_array, image_bounds, sref

# %%
# Perform a K-Means clustering
def get_clusters(image_array, nclusters=5, plotimage=False):
    """
    Using the satellite image subset array, calculate the specified
    number of clusters and return a numpy array.

    INPUT   -   image_array:        Satellite image stored as a 3D array
            -   nclusters:          Number of clusters
            -   plotimage:          Plot the clustered image (True/False)
    OUTPUT  -   clusters_array:     Clusters stored as a 2D array
    """
    # Reshape the array
    arr_kmeans = image_array.reshape([image_array.shape[0], -1]).T

    # Normalize the data
    scaled = MinMaxScaler().fit_transform(arr_kmeans)

    # Calculate clusters
    clusters = KMeans(n_clusters=nclusters).fit(scaled)

    # Convert the clusters to a raster image
    rowcol = int(clusters.labels_.shape[0]**.5)
    clusters_array = clusters.labels_.reshape(rowcol, rowcol)

    if plotimage:
        # Plot the clusters
        plt.imshow(clusters_array, cmap="tab20")
        plt.axis('off')

    return clusters_array

# %%
# Create dataframe to visualize area by clusters
def get_areas(clusters_array):
    """
    Calculate the area (in hectares) covered by each cluster, and
    return a pandas dataframe.

    INPUT   -   clusters_array:     Clusters stored as a 2D array
    OUTPUT  -   df_areas:           Dataframe with the areas in hectares
    """
    # Get summary table
    clusters, counts = numpy.unique(clusters_array, return_counts=True)
    # Transform area from m2 to hectares. Pixel size: 10x10m
    counts = [npixels*100/10000.0 for npixels in counts]
    # Create dataframe
    df_areas = pandas.DataFrame(list(zip(clusters, counts)), columns=['Clusters', 'Area (ha)'])

    return df_areas

# %%
# folium map
def show_folium_map(clusters_array, lon, lat, image_bounds):
    """
    Create a folium map using as background Esri's satellite
    tiles, and on top showing the clusters.

    INPUT   -   clusters_array:     Clusters stored as a 2D array
            -   lon:                Longitude (user's input)
            -   lat:                Latitude (user's input)
            -   bounds:             List of the clusters bounds
    OUTPUT  -   folium_map:         folium object
    """
    # Create folium map
    map_bounds = [[image_bounds[1][0], image_bounds[0][0]],
                  [image_bounds[1][1], image_bounds[0][1]]]

    m = folium.Map(location=[lat, lon], tiles=None)

    # Create FeatureGroup
    fg = folium.FeatureGroup(name='Image Clusters').add_to(m)

    # Add LayerControl
    folium.LayerControl(collapsed=False).add_to(m)

    # Add tile layer to map
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    attribution = 'Tiles &copy; Esri Imagery'
    folium.TileLayer(tiles=tiles, attr=attribution, name='Esri Imagery', control=False).add_to(m)

    # Create the folium raster overlay with the same colour palette
    # used in the Altair chart
    folium.raster_layers.ImageOverlay(
            image=clusters_array,
            colormap=cm.tab10,
            bounds=map_bounds,
            opacity=0.7).add_to(fg)

    # Add full screen button
    folium.plugins.Fullscreen().add_to(m)

    # Add feature group to map
    m.add_child(fg).fit_bounds(map_bounds)

    # Render Folium map
    folium_map = folium_static(m, width=1000)

    return folium_map

# %%
# Export clusters to GeoTIFF
def export_clusters(clusters_array, sref, transform):
    """
    Export the clusters array to GeoTIFF.

    INPUT   -   clusters_array:     Numpy array with the clusters
            -   sref:               Spatial reference of the original image
    OUTPUT  -   GeoTIFF:            File named 'clusters.tif'
    """

    # Export clusters
    profile = {
        'driver':   'GTiff',
        'height':   clusters_array.shape[0],
        'width':    clusters_array.shape[1],
        'count':    1,
        'dtype':    rasterio.uint8,
        'crs':      sref,
        'transform':transform
    }
    with rasterio.open('clusters.tif', 'w', **profile) as dst:
        dst.write(clusters_array, 1)

    return 'clusters.tif'