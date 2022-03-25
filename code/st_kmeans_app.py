from altair import Chart, Color, Scale
from datetime import date, timedelta
import streamlit as st
import stac_kmeans as sk

st.set_page_config(
     page_title="Sentinel-2 10-m bands clustering",
     page_icon=":satellite:",
     layout="wide"
 )

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Main title
st.title("Cloud-optimized GeoTIFF clustering on Sentinel-2 images")

# Streamlit parameters
st.sidebar.title("Define the location, satellite image parameters, and the number of clusters")
with st.sidebar.form(key='params_form'):
    lon = st.number_input(
        label='Longitud',
        format='%.6f',
        step=0.000001,
        min_value=-180.0,
        max_value=180.0,
        value=-123.37294
    )
    lat = st.number_input(
        label='Latitude',
        format='%.6f',
        step=0.000001,
        min_value=-90.0,
        max_value=90.0,
        value=48.46334
    )
    start_date = st.date_input(
        label='Start date',
        value=date(2021, 7, 15)
    )
    min_value = start_date + timedelta(days=1)
    end_date = st.date_input(
        label='End date',
        value=date(2021, 8, 15),
        min_value=min_value
    )
    max_cloud_cover = st.slider(
        label="Maximum cloud cover % (0-50)",
        value=10,
        step=5,
        min_value=0,
        max_value=50
    )
    npixels = st.slider(
        label="Image width/height in kilometers (1-10)",
        value=1,
        step=1,
        min_value=1,
        max_value=10)*100/2
    nclusters = st.slider(
        label="Number of clusters (2-10)",
        value=5,
        step=1,
        min_value=2,
        max_value=10
    )
    sub1 = st.form_submit_button(label='Calculate clusters')

# Read the STAC catalog and retrieve the best satellite image
best_image, window, transform = sk.get_less_cloudy_image(
    coords=[lon, lat],
    start_date=str(start_date),
    end_date=str(end_date),
    max_cloud_cover=max_cloud_cover,
    npixels=npixels
)
if best_image:

    # Read image subset
    image_array, image_bounds, sref = sk.read_sentinel2(
        best_image=best_image,
        window=window,
        transform=transform
    )

    # K-means clustering
    with st.spinner('Image clustering in progress...'):
        # K-means clustering
        clusters_array = sk.get_clusters(
            image_array=image_array,
            nclusters=nclusters
        )
    
        # Create clusters GeoTIFF
        output_file = sk.export_clusters(clusters_array, sref, transform)
        # Download clusters GeoTIFF
        with open(output_file, 'rb') as img:
            st.sidebar.download_button('Download clusters', img, file_name='clusters.tif')

        # Calculate clusters areas in hectares
        df_areas = sk.get_areas(clusters_array)

    # Create bar chart
    st.header('Area(ha) covered by each cluster')
    
    # Define custom Altair parameters
    # The colour palette is the same one used for the map clusters
    c = Chart(df_areas, width=1000).mark_bar().encode(
        x='Clusters:N',
        y='Area (ha):Q',
        color=Color('Clusters:N', scale=Scale(scheme='category10')),
        tooltip='Area (ha)'
    ).interactive()

    # Show the chart
    st.altair_chart(c)

    # Show the map
    st.header('Satellite image clusters')
    sk.show_folium_map(clusters_array, lon, lat, image_bounds)


else:
    st.write('No satellite images were found. Please change some parameters')

st.sidebar.info('Code available at [Github](https://www.github.com/julionovoa/st-kmeans)')
