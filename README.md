# Sentinel-2 cloud-optimized GeoTIFF clustering
## Contents
1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Usage](#3-usage)
4. [Conclusions](#4-conclusions)

### 1. Introduction
Until recently, satellite image processing required to locally store these datasets for performing any pre-processing or analyses. Nowadays, recent advances in streaming protocols for geospatial information, in particular cloud-optimized GeoTIFFs ([COG](https://www.cogeo.org/)), and specifications for indexing and discovering geospatial datasets such as the SpatioTemporal Asset Catalog ([STAC](https://stacspec.org/)) specification, have created a new paradigm in remote sensing for data retrieval, processing, and analysis, where one can process satellite imagery on-premises or in the cloud, without downloading these massive datasets.

This repository contains an example of how to perform a cluster analysis (i.e. unsupervised classification) on a Sentinel-2 satellite image, using its four 10-m spatial resolution bands, and how to create a Streamlit app to allow user's interaction and results visualization. The algorithm used was [k-means](https://en.wikipedia.org/wiki/K-means_clustering) and the clusters can be generated anywhere in the world where there is availability of Sentinel-2 imagery. The satellite imagery is searched and retrieved from a public AWS catalog, the clusters are calculated and a bar chart and a map are shown on the app.

### 2. Installation
You must have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and [Git](https://git-scm.com/) installed. Open the Miniconda terminal and clone this repository using `git clone https://github.com/julionovoa/st-kmeans.git`, go to the cloned repository's directory, and create a new `conda` environment using  `conda env create -f environment.yml`. Activate the new conda environment using `activate st-kmeans`.
These are the main Python libraries installed :
- streamlit
- streamlit_folium
- folium
- pystac_client
- rasterio
- numpy
- pandas
- matplotlib
- altair
- scikit-learn

### 3. Usage
Once the conda environment was created and activated, use the terminal to execute the command `streamlit run code/st_kmeans_app.py`.

The Streamlit app contains two main elements, the sidebar on the left and the results area on the right. On the sidebar the user must specify the following parameters:
- Longitude:            central longitude of the area of interest, expressed in decimal degrees
- Latitude:             central latitude of the area of interest, expressed in decimal degrees
- Start date:           satellite image start acquisition date   
- End date:             satellite image end acquisition date
- Maximum cloud cover:  maximum cloud cover, expressed as percentage
- Image width/height:   size of the area of interest, expressed in kilometers
- Number of clusters:   desired number of clusters

Once all the parameters have been specified, clicking on the `Calculate clusters` button will generate on the results area, a bar chart showing the area (in hectares) covered by each cluster, and a map where the user can turn on and off the clusters to compare them with the underlying satellite imagery.

Finally, if desired, the user can download a GeoTIFF for further processing (e.g. QGIS). For downloading the clusters' GeoTIFF the user must click on the button called `Download clusters`.

![](etc/app.png)

### 4. Conclusions
Massive amounts of satellite imagery are made available every day by cloud providers such as AWS's Registry of Open Data, Microsoft's Planetary Computer, or Google's Earth Engine, and while there exists several tools to process satellite imagery, few are taking advantage of the STAC specification or new streaming-optimized geospatial storage formats. This demo app pretends to contribute to help fill this knowledge gap by providing a simple and effective tool to search and retrieve satellite imagery, apply a machine learning algorithm, and present a summary of the results in for of a bar chart and an interactive map.

The effectiveness of this algorithm lies in that there is no need to train the satellite image to generate a fast land cover map to help one understand the area under study. It is worth mentioning the satellite background shown in the map widget is not the original Sentinel-2 image used for calculating the clusters, so this is not a direct visual comparison between the raw imagery and the resulting clusters. This limitation was adopted in this demo app to avoid using too many computing resources, but in a larger scale production environment this can be easily improved.

