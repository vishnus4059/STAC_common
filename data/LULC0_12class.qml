<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" version="3.22.4-Białowieża" minScale="1e+08" maxScale="0" styleCategories="AllStyleCategories">
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
      <resampling zoomedOutResamplingMethod="nearestNeighbour" zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false"/>
    </provider>
    <rasterrenderer nodataColor="" opacity="0.145" alphaBand="-1" band="1" type="paletted">
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
        <paletteEntry value="0" label="clear" alpha="0" color="#000000"/>
        <paletteEntry value="1" label="built up" alpha="255" color="#ff0000"/>
        <paletteEntry value="2" label="kharif water" alpha="255" color="#74ccf4"/>
        <paletteEntry value="3" label="kharif and rabi water" alpha="255" color="#1ca3ec"/>
        <paletteEntry value="4" label="kharif and rabi and zaid water" alpha="255" color="#0f5e9c"/>
        <paletteEntry value="5" label="croplands" alpha="255" color="#f1c232"/>
        <paletteEntry value="6" label="Tree/Forests" alpha="255" color="#38761d"/>
        <paletteEntry value="7" label="barren lands" alpha="255" color="#a9a9a9"/>
        <paletteEntry value="8" label="Single Kharif Cropping" alpha="255" color="#bad93e"/>
        <paletteEntry value="9" label="Single Non-Kharif Cropping" alpha="255" color="#f59d22"/>
        <paletteEntry value="10" label="Double Cropping" alpha="255" color="#ff9371"/>
        <paletteEntry value="11" label="Triple Cropping" alpha="255" color="#b3561d"/>
        <paletteEntry value="12" label="Shrubs_Scrubs" alpha="255" color="#a9a9a9"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast contrast="0" gamma="1" brightness="0"/>
    <huesaturation invertColors="0" colorizeOn="0" saturation="0" colorizeGreen="128" colorizeBlue="128" colorizeRed="255" colorizeStrength="100" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
