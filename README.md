# A streamlit app for performing k-means clustering on the 10-m bands of the Sentinel-2 satellite.
## Contents
1. Introduction
2. Installation
3. Usage
4. Results
5. Next steps

### 1. Introduction
Until recently, satellite image processing required to locally store these datasets for performing any pre-processing or analyses. Nowadays, recent advances in streaming protocols for geospatial information, in particular cloud-optimized GeoTIFFs ([COG](https://www.cogeo.org/)), and specifications for indexing and discovering geospatial datasets such as the SpatioTemporal Asset Catalog ([STAC](https://stacspec.org/)) specification, have created a new paradigm in remote sensing for data retrieval, processing, and analysis, where one can process satellite imagery on-premises or in the cloud, without downloading these massive datasets.

This repository contains an example of how to perform a cluster analysis (i.e. unsupervised classification) on a Sentinel-2 satellite image, using its fours 10-m spatial resolution bands. The algorithm used was [k-means](https://en.wikipedia.org/wiki/K-means_clustering) and the clusters can be generated anywhere in the world where there is availability of Sentinel-2 imagery. The imagery is searched and retrieved from a public AWS catalog, the clusters are calculated and a bar chart and a map show these results in the app interface.

### 2. Installation
A `conda` environment was created, and the following Python libraries were installed using the command `conda env create -f environment.yml`:
- streamlit
- pystac_client
- rasterio
- numpy
- pandas
- matplotlib
- altair
- folium
- scikit-learn

### 3. Usage
The Streamlit app contains two main elements, the sidebar on the left and the results area on the right. On the sidebar the user must specify the following parameters:
- Longitude:            central longitude of the area of interest, expressed in decimal degrees
- Latitude:             central latitude of the area of interest, expressed in decimal degrees
- Start date:           satellite image start acquisition date   
- End date:             satellite image end acquisition date
- Maximum cloud cover:  maximum cloud cover, expresed as percentage
- Image width/heigh:    size of the area of interest, expressed in kilometers
- Number of clusters:   desired number of clusters

Once all the parameters have been specified, clicking on the `Calculate clusters` button will generate on the results area, a bar chart showig the area (in hectares) covered by each cluster, and a map where the user can turn on and off the clusters to compare them with the underlying satellite imagery.

Finally, if desired, the user can download the clusters GeoTIFF for further processing or carrtographic production (e.g. QGIS). For downloading the clusters the user must click on the button called `Download clusters`.

![](etc/app.png)

### 4. Results
Several random locations were tested during the creation of this app, at the results shown are accurate, as far as an unsupervised classification could be. This means that with no training on these images one is able of generating a simple and effective land cover map to have a better understanding of the area of interest and the changing dynamics occuring there.

### 5. Next steps
The code provided in this repository is aimed to be used as a starting point in the search, retrieval, and analysis of satellite imagery using COGs and the STAC specification, to leverage powerful analystics to be applied to several business cases that can benefit from it.

I you need more information, [contact me](https://twitter.com/julionovoa_) on Twitter.