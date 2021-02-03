# Web visualization of NetCDF with Itowns

This following projet show you the processus to make a web base visualization of your NetCDF temperature info.

The processus would be the same to render other NetCDF feature as the wind.

## Example

See the example for [Paris](https://cboucheign.github.io/netcdf-itowns/)

> [Source code here](index.html)

## Overview

1. [Export the temperature dataset to a GeoJSON](#extract)
2. [Create your Itowns scene](#itowns)
    * [Source code](index.html) for Paris
    * [Itowns](http://www.itowns-project.org/itowns/docs/#tutorials/Create-a-simple-globe) documentation

Other project in IGN look for a direct integration of NetCDF data in Itowns. We will update this guide.

<a id="extract"></a>

## Extract NetCDF temperature to GeoJson

### 1.1 CSV using QGIS

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
   * using Point Sampling Tool

4. Save the regular grid in CSV. Then load it again using latitude and longitude attributes (WGS:84).

### 1.2 CSV to GeoJSON

Edit the following [script](../data/csv2geoJson.py) with your csv files.

### 1.3 Appendix : compute Meso-NH and TEB height

Calculer l’altitude des niveaux Meso-NH et TEB.

1.	Calculer l’altitude DE LA BASE (POINTS W) des niveaux Meso-NH à l’aide de la formule de Galchen à partir des valeurs de 
    * ZS (altitude du sol)
    * XZHAT (hauteur DE LA BASE (POINTS W) des niveaux Meso-NH au-dessus du sol, ZHAT dans le NetCDF)
    * H (dernière valeur de XZHAT)
2.	Calculer l’altitude du centre du niveau Meso-NH 2 à partir des altitudes des points W des niveaux Meso NH 2 et 3. L’altitude du centre du niveau Meso-NH 2 est identique à l’altitude du centre du niveau TEB 6. 
3.	Le niveau Meso-NH 1 n’est pas à représenter.
4.	A partir de l’altitude du centre du niveau Meso-NH 2, et de la hauteur au-dessus du vrai sol des niveaux TEB (TEB_CAN_Z0X dans le NetCDF), calculer l’altitude des centres des différents niveaux TEB.

<a id="itowns"></a>

## Itowns 3D scene

Create a new Scene 

```js
view = new itowns.PlanarView(viewerDiv, extent, {
    disableSkirt: true,
    placement: { heading: 0, range: 4000, tilt: 45 }
});
view.tileLayer.maxSubdivisionLevel = 18;
view.tileLayer.minSubdivisionLevel = 0;
view.isDebugMode = true;
setupLoadingScreen(viewerDiv, view);
```

Add an elevation Layer

```js
// On ajoute un flux WMS pour le MNT du Geoportail (il n'y a pas de flux MNT en WMTS dispo)
const sourceMNT = new itowns.WMSSource({
    url: "https://wxs.ign.fr/3ht7xcw6f7nciopo16etuqp2/geoportail/r/wms",
    version: "1.3.0",
    name: "ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES",
    style: "",
    format: "image/x-bil;bits=32",
    projection: 'EPSG:2154',
    extent: extent,
    zoom: { min: 0, max: 14 },
});
const layerMNT = new itowns.ElevationLayer('MNT', { source: sourceMNT });
view.addLayer(layerMNT);
```

Add scene layer (orthophoto and urban buildings)


```js
const sourceOrtho = new itowns.WMSSource({
    url: "https://wxs.ign.fr/3ht7xcw6f7nciopo16etuqp2/geoportail/r/wms",
    version: "1.3.0",
    name: "HR.ORTHOIMAGERY.ORTHOPHOTOS",
    style: "",
    format: "image/jpeg",
    projection: 'EPSG:2154',
    extent: extent,
    zoom: { min: 0, max: 14 },
});
const layerOrtho = new itowns.ColorLayer('Ortho', { source: sourceOrtho });
view.addLayer(layerOrtho);

var wfsBuildingSource = new itowns.WFSSource({
    url: 'https://wxs.ign.fr/3ht7xcw6f7nciopo16etuqp2/geoportail/wfs?',
    version: '2.0.0',
    typeName: 'BDTOPO_BDD_WLD_WGS84G:bati_remarquable,BDTOPO_BDD_WLD_WGS84G:bati_indifferencie,BDTOPO_BDD_WLD_WGS84G:bati_industriel',
    projection: 'EPSG:2154',
    ipr: 'IGN',
    format: 'application/json',
    zoom: { min: 8, max: 8  },
    extent: extentBati,
});
var wfsBuildingLayer = new itowns.GeometryLayer('wfsBuilding', new itowns.THREE.Group(), {
    update: itowns.FeatureProcessing.update,
    convert: itowns.Feature2Mesh.convert({
        color: colorBuildings,
        altitude: altitudeBuildings,
        extrude: extrudeBuildings }),
    filter: acceptFeature,
    overrideAltitudeInToZero: true,
    source: wfsBuildingSource,
});
view.addLayer(wfsBuildingLayer);
```

Add a temperature layer

```js
// Add a geometry layer, which will contain the points to display
var Temperature = new itowns.GeometryLayer('Temperature', new itowns.THREE.Group(), 
{
    onMeshCreated: function(mesh){
        mesh.material.size = 100;
        }
});
Temperature.update = itowns.FeatureProcessing.update;
Temperature.convert = itowns.Feature2Mesh.convert({
    color: function(p){
        const tempMin = 290;
        const tempMax = 330;
        const Blue = new itowns.THREE.Color("rgb(0, 0, 255)");
        const Red = new itowns.THREE.Color("rgb(255, 0, 0)");
        const alpha = Math.min(255, Math.max(0,(p.temp-tempMin)/(tempMax-tempMin)));
        return Blue.lerpHSL(Red, alpha);
    }
    });
    // Use a FileSource to load a single file once
    Temperature.source = new itowns.FileSource({
    url: 'data/lambert_O_paris_centre.geojson',
    projection: 'EPSG:2154',
    format: 'application/json',
    zoom: { min: 0, max: 10 },
});
view.addLayer(Temperature).then(function menu(layer) {
    var gui = debug.GeometryDebug.createGeometryDebugUI(menuGlobe.gui, view, layer);
    debug.GeometryDebug.addWireFrameCheckbox(gui, view, layer);
});
```

## License

> TODO

