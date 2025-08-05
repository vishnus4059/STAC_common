<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" minScale="1e+08" maxScale="0" version="3.22.4-Białowieża" hasScaleBasedVisibilityFlag="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal fetchMode="0" enabled="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option value="false" type="bool" name="WMSBackgroundLayer"/>
      <Option value="false" type="bool" name="WMSPublishDataSourceUrl"/>
      <Option value="0" type="int" name="embeddedWidgets/count"/>
      <Option value="Value" type="QString" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option value="" type="QString" name="name"/>
      <Option name="properties"/>
      <Option value="collection" type="QString" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" enabled="false" maxOversampling="2" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer alphaBand="-1" nodataColor="" opacity="1" type="paletted" band="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry value="1" label="V-shape river valleys, Deep narrow canyons" color="#313695" alpha="255"/>
        <paletteEntry value="2" label="Lateral midslope incised drainages, Local valleys in plains" color="#4575b4" alpha="255"/>
        <paletteEntry value="3" label="Upland incised drainages, Stream headwaters" color="#a50026" alpha="255"/>
        <paletteEntry value="4" label="U-shape valleys" color="#e0f3f8" alpha="255"/>
        <paletteEntry value="5" label="Broad Flat Areas" color="#fffc00" alpha="255"/>
        <paletteEntry value="6" label="Broad open slopes" color="#feb24c" alpha="255"/>
        <paletteEntry value="7" label="Mesa tops" color="#f46d43" alpha="255"/>
        <paletteEntry value="8" label="Upper Slopes" color="#d73027" alpha="255"/>
        <paletteEntry value="9" label="Local ridge/hilltops within broad valleys" color="#91bfdb" alpha="255"/>
        <paletteEntry value="10" label="Lateral midslope drainage divides, Local ridges in plains" color="#800000" alpha="255"/>
        <paletteEntry value="11" label="Mountain tops, high ridges" color="#4d0000" alpha="255"/>
        <paletteEntry value="12" color="#ffffff" alpha="255"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation colorizeBlue="128" colorizeStrength="100" colorizeOn="0" saturation="0" invertColors="0" colorizeGreen="128" grayscaleMode="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
