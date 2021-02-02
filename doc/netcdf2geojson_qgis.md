
# NetCDF to GeoJSON for web visualization

## Quick guide to produce a CSV

In QGIS 3.* (NetCDF Browser peut-être à installer moi j'ai pas eu besoin)

1. Import NetCDF file as Raster and select the following features :
   * latitude (1 feature, 1 channel)
   * longitude (1 feature, 1 channel)
   * TEB_CAN_T0X (6 features, 1 channel)
   * TEB_CAN_Z0X (6 features, 1 channel)
   * THT (1 feature, 32 channels)
   * ZS (1 feature, 1 channel)

2. Create a regular grid layer from raster ZS (or anyone feature)
   * see [QGIS documentation](https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorcreation.html#raster-pixels-to-points)

3. Merge attributes from each channel (latitude, longitude, TEB...) to each point
   * avec Point Sampling Tool

4. Save the regular grid in CSV. Then load it again using latitude and longitude attributes. You can use a local projection.

## CSV to GeoJSON

Use the following [script](../data/csv2geoJson.py) with your files

Then you can use this file to create the 3D scene with [Itowns](../README.md)

## Appendix : compute Meso-NH and TEB height

Calculer l’altitude des niveaux Meso-NH et TEB.
1.	Calculer l’altitude DE LA BASE (POINTS W) des niveaux Meso-NH à l’aide de la formule de Galchen à partir des valeurs de 
    * ZS (altitude du sol)
    * XZHAT (hauteur DE LA BASE (POINTS W) des niveaux Meso-NH au-dessus du sol, ZHAT dans le NetCDF)
    * H (dernière valeur de XZHAT)
2.	Calculer l’altitude du centre du niveau Meso-NH 2 à partir des altitudes des points W des niveaux Meso NH 2 et 3. L’altitude du centre du niveau Meso-NH 2 est identique à l’altitude du centre du niveau TEB 6. 
3.	Le niveau Meso-NH 1 n’est pas à représenter.
4.	A partir de l’altitude du centre du niveau Meso-NH 2, et de la hauteur au-dessus du vrai sol des niveaux TEB (TEB_CAN_Z0X dans le NetCDF), calculer l’altitude des centres des différents niveaux TEB.
