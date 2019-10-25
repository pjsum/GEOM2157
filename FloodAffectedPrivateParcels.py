# -*- coding: utf-8 -*-
"""
Created on Sun Oct 6 10:15:24 2019

@author: Paul Summers
@studentNo: s3490934
"""

#import required modules
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsFeatureRequest,
                       QgsProject,
                       QgsField,
                       QgsLayerTreeLayer)
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
from PyQt5.QtGui import QColor
import qgis.utils
import processing

#creation of the QgsProcessingAlgorithm subclass
class FloodAffectedPrivateParcels(QgsProcessingAlgorithm):

    #set the input constants
    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    INPUT4 = 'INPUT4'
    INPUT5 = 'INPUT5'
    INPUT6 = 'INPUT6'
    INPUT7 = 'INPUT7'
    INPUT8 = 'INPUT8'
    
    def tr(self, string):
        #create a translatable string with the self.tr() function
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        #create the algorithm instance
        return FloodAffectedPrivateParcels()

    def name(self):
        #set the algorithm name (unique ID)
        return 'floodaffectedprivateparcels'

    def displayName(self):
        #set the algorithm name (title in toolbox)
        return self.tr('Count flood-affected private parcels')

    def group(self):
        #set script group (location in toolbox)
        return self.tr('Example scripts')

    def groupId(self):
        #set script group (unique ID)
        return 'examplescripts'

    def shortHelpString(self):
        #set the script description (for GUI)
        return self.tr("This tool will provide counts for flood-affected private parcels and their relevant flood control overlays, as well as providing area (sqm) of projected flood inundation for a council, based on a given coastal inundation layer. It also outputs two new temporary layers, a “Flood-Affected Private Parcels” layer which has added zone and overlay attributes, and a “Flooded Area” layer, which has added zone and area attributes. \n Note: Please turn off Invalid Features Filtering before using this tool.")

    def initAlgorithm(self, config=None):
        #define the input vector feature sources (set allowable geometry type and text labels for GUI)
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT1,
                self.tr('Local Government Area (LGA) Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT2,
                self.tr('Parcels Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )   
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT3,
                self.tr('Address Points Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )   
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT4,
                self.tr('Planning Zones Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        ) 
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT5,
                self.tr('Planning Overlays Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )   
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT6,
                self.tr('Coastal Inundation Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )                   
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT7,
                self.tr('Coastline Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )     
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT8,
                self.tr('Watercourse Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )  

    def processAlgorithm(self, parameters, context, feedback):
        #retrieve the layer inputs
        source1 = self.parameterAsSource(
            parameters,
            self.INPUT1,
            context
        )
        source2 = self.parameterAsSource(
            parameters,
            self.INPUT2,
            context
        )
        source3 = self.parameterAsSource(
            parameters,
            self.INPUT3,
            context
        )
        source4 = self.parameterAsSource(
            parameters,
            self.INPUT4,
            context
        )
        source5 = self.parameterAsSource(
            parameters,
            self.INPUT5,
            context
        )
        source6 = self.parameterAsSource(
            parameters,
            self.INPUT6,
            context
        )
        source7 = self.parameterAsSource(
            parameters,
            self.INPUT7,
            context
        )
        source8 = self.parameterAsSource(
            parameters,
            self.INPUT8,
            context
        )

        #if a layer was not found, throw an exception to indicate that the algorithm encountered a fatal error
        if source1 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT1))
        if source2 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT2))
        if source3 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT3))
        if source4 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT4))
        if source5 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT5))
        if source6 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT6))
        if source7 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT7))
        if source8 is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT8))
        
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("1/5 - Checking CRS...")
        feedback.pushInfo('--------------------------------------------------------------------------')
        
        #get crs of each layer
        crs1 = source1.sourceCrs().authid()
        crs2 = source2.sourceCrs().authid()
        crs3 = source3.sourceCrs().authid()
        crs4 = source4.sourceCrs().authid()
        crs5 = source5.sourceCrs().authid()
        crs6 = source6.sourceCrs().authid()
        crs7 = source7.sourceCrs().authid()
        crs8 = source8.sourceCrs().authid()
        
        #check crs of each layer and stop script if not all matching
        if crs1 == crs2 and crs1 == crs3 and crs1 == crs4 and crs1 == crs5 and crs1 == crs6 and crs1 == crs7 and crs1 == crs8:
            feedback.pushInfo('CRS is ' + (crs1))            
            feedback.pushInfo('CRS is matching for all layers')
        else:   
            feedback.pushInfo('Please ensure matching CRS for all layers')
            feedback.pushInfo('CRS for INPUT1 is ' + (crs1))
            feedback.pushInfo('CRS for INPUT2 is ' + (crs2))
            feedback.pushInfo('CRS for INPUT3 is ' + (crs3))
            feedback.pushInfo('CRS for INPUT4 is ' + (crs4))
            feedback.pushInfo('CRS for INPUT5 is ' + (crs5))
            feedback.pushInfo('CRS for INPUT6 is ' + (crs6))
            feedback.pushInfo('CRS for INPUT7 is ' + (crs7))
            feedback.pushInfo('CRS for INPUT8 is ' + (crs8))
            return{}
         
        #check if script has been cancelled before next stage
        if feedback.isCanceled():
            return{}   
        
        #output current stage of script
        feedback.pushInfo('--------------------------------------------------------------------------') 
        feedback.pushInfo("2/5 - Preparing Layer Data...")
        feedback.pushInfo('--------------------------------------------------------------------------')

        #get the layer data from the inputs
        lgaLayer = parameters['INPUT1']
        parcelsLayer = parameters['INPUT2']
        addressLayer = parameters['INPUT3']
        zonesLayer = parameters['INPUT4']
        overlaysLayer = parameters['INPUT5']
        floodLayer = parameters['INPUT6']
        coastLayer = parameters['INPUT7']
        watercourseLayer = parameters['INPUT8']
        
        #clip flood area to LGA
        result = processing.run('native:clip', { 'INPUT': floodLayer, 'OUTPUT': 'memory:', 'OVERLAY': lgaLayer }, context=context, feedback=feedback)
        floodLayer = result["OUTPUT"]
        
        #create a flood check layer (coast and waterways)
        floodCheckList = [coastLayer,watercourseLayer]
        result = processing.run('native:mergevectorlayers', {"LAYERS": floodCheckList, "OUTPUT": 'memory:' }, context=context, feedback=feedback)
        floodCheckLayer = result["OUTPUT"]
        
        #clean up flood layer (keep only areas that intersect with flood check layer)
        result = processing.run('native:extractbylocation', { 'INPUT': floodLayer, 'INTERSECT': floodCheckLayer, 'METHOD': 0, 'OUTPUT': 'memory:', 'PREDICATE': [0] }, context=context, feedback=feedback)
        floodCleanedLayer = result["OUTPUT"]
        
        #get total area of LGA
        result = processing.run('qgis:exportaddgeometrycolumns', { 'CALC_METHOD': 0, 'INPUT': lgaLayer, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        lgaAreaLayer = result["OUTPUT"]
        
        #get zone areas that intersect with flood layer
        result = processing.run('native:extractbylocation', { 'INPUT': zonesLayer, 'INTERSECT': floodCleanedLayer, 'METHOD': 0, 'OUTPUT': 'memory:', 'PREDICATE': [0] }, context=context, feedback=feedback)
        zonesLayer = result["OUTPUT"]
        
        #add "ZONE_CLASS" field to zones layer
        zonesLayer.startEditing()
        zonesLayer.dataProvider().addAttributes([QgsField("ZONE_CLASS", QVariant.String)])
        zonesLayer.updateFields()
        zonesLayer.commitChanges()
        
        #add "ZONE_CLASS" attribute for each feature ("ZONE_CODE" without numeric digit)
        zFeatures = zonesLayer.getFeatures()
        zonesLayer.startEditing()
        for feature in zFeatures:
            ini_string = feature["ZONE_CODE"]
            res = ''.join([i for i in ini_string if not i.isdigit()]) 
            feature["ZONE_CLASS"] = res
            zonesLayer.updateFeature(feature)
        zonesLayer.commitChanges()
        
        #check if script has been cancelled before next stage
        if feedback.isCanceled():
            return{}      
        
        #output current stage of script
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("3/5 - Calculating Flooded Area...")
        feedback.pushInfo('--------------------------------------------------------------------------')
        
        #clip zones layer to the flooded area
        #NOTE: must turn off invalid features filtering in QGIS - otherwise this process won't work as some geometry is invalid
        result = processing.run('native:clip', { 'INPUT': zonesLayer, 'OUTPUT': 'memory:', 'OVERLAY': floodCleanedLayer }, context=context, feedback=feedback)
        floodedZonesLayer = result["OUTPUT"]
        
        #group by "ZONE_CLASS"
        result = processing.run('native:dissolve', { 'FIELD': ['ZONE_CLASS'], 'INPUT': floodedZonesLayer, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        floodedZonesLayerDissolved = result["OUTPUT"]
        
        #add area for each "ZONE_CLASS"
        result = processing.run('qgis:exportaddgeometrycolumns', { 'CALC_METHOD': 0, 'INPUT': floodedZonesLayerDissolved, 'OUTPUT': 'memory:Flooded Area' }, context=context, feedback=feedback)
        floodedZonesAreaLayer = result["OUTPUT"]
        
        #add the "Flooded Area" layer to the layers panel
        #first add the layer without showing it
        QgsProject.instance().addMapLayer(floodedZonesAreaLayer, False)
        #obtain the layer tree of the top-level group in the project
        layerTree = iface.layerTreeCanvasBridge().rootGroup()
        #insert the layer - the position is a number starting from 0, with -1 an alias for the end
        layerTree.insertChildNode(-1, QgsLayerTreeLayer(floodedZonesAreaLayer))
        
        #customise the symbology for the "Flooded Area" layer
        layer = QgsProject.instance().mapLayersByName("Flooded Area")[0]
        single_symbol_renderer = layer.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(150, 206, 250))
        symbol.symbolLayer(0).setStrokeColor(QColor.fromRgb(70, 130, 180))
        symbol.setOpacity(0.3)
        layer.triggerRepaint()
        qgis.utils.iface.layerTreeView().refreshLayerSymbology(layer.id())
        
        #check if script has been cancelled before next stage
        if feedback.isCanceled():
            return{}
        
        #output current stage of script
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("4/5 - Calculating Flood-Affected Private Parcels...")
        feedback.pushInfo('--------------------------------------------------------------------------')
        
        #get all flood-affected parcels
        result = processing.run('native:extractbylocation', { 'INPUT': parcelsLayer, 'INTERSECT': floodCleanedLayer, 'METHOD': 0, 'OUTPUT': 'memory:', 'PREDICATE': [0] }, context=context, feedback=feedback)
        floodAffectedParcelsOriginal = result["OUTPUT"]
        
        #create inside buffer on zones layer (to avoid zones touching other parcels when intersecting)
        result = processing.run('native:buffer', { 'DISSOLVE': False, 'DISTANCE': -1, 'END_CAP_STYLE': 0, 'INPUT': zonesLayer, 'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'OUTPUT' : 'memory:', 'SEGMENTS': 200 }, context=context, feedback=feedback)
        zonesLayerClean = result["OUTPUT"]
        
        #exclude irrelevant zones (public zones, PZ and UFZ)
        request = QgsFeatureRequest().setFilterExpression("\"ZONE_CLASS\" = \'PCRZ\' OR \"ZONE_CLASS\" = \'PPRZ\' OR \"ZONE_CLASS\" = \'PUZ\' OR \"ZONE_CLASS\" = \'RDZ\' OR \"ZONE_CLASS\" = \'CA\' OR \"ZONE_CLASS\" = \'PZ\' OR \"ZONE_CLASS\" = \'UFZ\'")
        ids = [f.id() for f in zonesLayerClean.getFeatures(request)]
        zonesLayerClean.startEditing()
        for fid in ids:
            zonesLayerClean.deleteFeature(fid)
        zonesLayerClean.commitChanges()
        
        #add zone data to parcels
        result = processing.run('qgis:joinattributesbylocation', { 'DISCARD_NONMATCHING': True, 'INPUT': floodAffectedParcelsOriginal, 'JOIN': zonesLayerClean, 'METHOD': 1, 'OUTPUT': 'memory:', 'PREDICATE': [0] }, context=context, feedback=feedback)
        floodAffectedParcelsAll = result["OUTPUT"]
          
        #delete parcels with duplicate geometries - a work-around because 'qgis:deleteduplicategeometries' was causing crashes on return{}
        result = processing.run('qgis:exportaddgeometrycolumns', { 'CALC_METHOD': 0, 'INPUT': floodAffectedParcelsAll, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        floodAffectedParcelsArea = result["OUTPUT"]
        result = processing.run('native:removeduplicatesbyattribute', { 'FIELDS': ['area','perimeter'], 'INPUT': floodAffectedParcelsArea, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        floodAffectedParcels = result["OUTPUT"]

        #delete irrelevant parcels by attribute
        #"PC_LOTNO" LIKE 'CM%' = driveways, carparking and building surrounds
        #"PC_LOTNO" LIKE 'R%' = park reserves
        #"PC_STAT" = 'P' = proposed parcels
        #"PC_CRSTAT" = 'C' = crown parcels
        #"PC_CRSTAT" = 'G' = road reserves
        #"PC_SPIC" = '200' = shared driveways
        request = QgsFeatureRequest().setFilterExpression("\"PC_LOTNO\" LIKE \'CM%\' OR \"PC_LOTNO\" LIKE \'R%\' OR \"PC_STAT\" = \'P\' OR \"PC_CRSTAT\" = \'C\' OR \"PC_CRSTAT\" = \'G\' OR \"PC_SPIC\" = \'200\'")
        ids = [f.id() for f in floodAffectedParcels.getFeatures(request)]
        floodAffectedParcels.startEditing()
        for fid in ids:
            floodAffectedParcels.deleteFeature(fid)
        floodAffectedParcels.commitChanges()
        
        #remove address points without a specified address number
        result = processing.run('native:extractbyexpression', {'EXPRESSION': '(\"BUNIT_ID1\" != \'0\' OR \"BUNIT_ID2\" != \'0\' OR \"FLOOR_NO_1\" != \'0\' OR \"FLOOR_NO_2\" != \'0\' OR \"HSE_NUM1\" != \'0\' OR \"HSE_NUM2\" != \'0\' OR \"DISP_NUM1\" != \'0\' OR \"DISP_NUM2\" != \'0\')', 'INPUT': addressLayer, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        addressLayerClean = result["OUTPUT"]

        #get parcels with a valid address point
        result = processing.run('native:extractbylocation', { 'INPUT': floodAffectedParcels, 'INTERSECT': addressLayerClean, 'METHOD': 0, 'OUTPUT': 'memory:', 'PREDICATE': [0] }, context=context, feedback=feedback)
        floodAffectedPrivateParcels = result["OUTPUT"]
        
        #remove parcels under 40sqm (indicates it is not a regular private land parcel)
        result = processing.run('native:extractbyexpression', { 'EXPRESSION': '(\"area\" > \'40\')', 'INPUT': floodAffectedPrivateParcels, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        finalParcelsAreaClean = result["OUTPUT"]
        
        #delete parcels with inner rings (indicates it is not a regular private land parcel)
        #add "POLY_RING" field to parcels layer
        finalParcelsAreaClean.startEditing()
        finalParcelsAreaClean.dataProvider().addAttributes([QgsField("POLY_RING", QVariant.Double)])
        finalParcelsAreaClean.updateFields()
        finalParcelsAreaClean.commitChanges()
        
        #add "POLY_RING" attribute for each feature (count rings for each polygon within feature geometry)
        pFeatures = finalParcelsAreaClean.getFeatures()
        finalParcelsAreaClean.startEditing()
        for feature in pFeatures:
            geometry = feature.geometry()
            polyCount = 0
            ringCount = 0
            if geometry.isMultipart():
                polygons = geometry.asMultiPolygon()
            else:
                polygons = geometry.asPolygon()
            for polygon in polygons:
                polyCount = polyCount + 1
                for ring in polygon:
                    ringCount = ringCount + 1
                count = (ringCount/polyCount)
                feature["POLY_RING"] = count
                finalParcelsAreaClean.updateFeature(feature) 
        finalParcelsAreaClean.commitChanges()
        
        #delete features with more rings than polygons (indicates it has an inner ring)
        request = QgsFeatureRequest().setFilterExpression("\"POLY_RING\" > \'1\'")
        ids = [f.id() for f in finalParcelsAreaClean.getFeatures(request)]
        finalParcelsAreaClean.startEditing()
        for fid in ids:
            finalParcelsAreaClean.deleteFeature(fid)
        finalParcelsAreaClean.commitChanges()
        
        #get relevant flood control overlays
        result = processing.run('native:extractbyexpression', { 'EXPRESSION': '(\"ZONE_CODE\" = \'SBO\' OR \"ZONE_CODE\" = \'LSIO\' OR \"ZONE_CODE\" = \'FO\')', 'INPUT': overlaysLayer, 'OUTPUT': 'memory:' }, context=context, feedback=feedback)
        relevantOverlays = result["OUTPUT"]
        
        #assign parcels with relevant flood control overlays (if intersection)
        result = processing.run('qgis:joinattributesbylocation', { 'DISCARD_NONMATCHING': False, 'INPUT': finalParcelsAreaClean, 'JOIN': relevantOverlays, 'METHOD': 1, 'OUTPUT': 'memory:Flood-Affected Private Parcels', 'PREDICATE': [0] }, context=context, feedback=feedback)
        finalParcels = result["OUTPUT"]
        
        #add the "Flood-Affected Private Parcels" layer to the layers panel
        #first add the layer without showing it
        QgsProject.instance().addMapLayer(finalParcels, False)
        #obtain the layer tree of the top-level group in the project
        layerTree = iface.layerTreeCanvasBridge().rootGroup()
        #insert the layer - the position is a number starting from 0, with -1 an alias for the end
        layerTree.insertChildNode(-1, QgsLayerTreeLayer(finalParcels))
        
        #customise the symbology for the "Flood-Affected Private Parcels" layer
        layer = QgsProject.instance().mapLayersByName("Flood-Affected Private Parcels")[0]
        single_symbol_renderer = layer.renderer()
        symbol = single_symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(225, 225, 225))
        symbol.symbolLayer(0).setStrokeColor(QColor.fromRgb(115, 115, 115))
        layer.triggerRepaint()
        qgis.utils.iface.layerTreeView().refreshLayerSymbology(layer.id())
        
        #check if script has been cancelled before next stage
        if feedback.isCanceled():
            return{}
        
        #output current stage of script
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("5/5 - Calculating statistics...")
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("FLOODED AREA (sqm):")
        feedback.pushInfo('--------------------------------------------------------------------------')

        #get lga area
        lgaFeatures = lgaAreaLayer.getFeatures()
        for feature in lgaFeatures:
            lgaArea = feature["area"]
        
        #get flooded lga area
        lgaFloodArea = 0
        zoneFeatures = floodedZonesAreaLayer.getFeatures()
        for feature in zoneFeatures:
            zoneArea = feature["area"]
            lgaFloodArea = lgaFloodArea + zoneArea
        
        #get flooded area percentage
        floodPercent = ((lgaFloodArea/lgaArea)*100)
        
        #ouput flooded lga area and percentage
        feedback.pushInfo('Flooded Area: ' + (str(round(lgaFloodArea, 2))))
        feedback.pushInfo((str(round(floodPercent, 2))) + '% of LGA Area')
        feedback.pushInfo('BY ZONE:')
        feedback.pushInfo('---------------------------------')
        
        #get and output flooded area for each "ZONE_CLASS"
        request = QgsFeatureRequest()
        clause = QgsFeatureRequest.OrderByClause('area', ascending=False)
        orderby = QgsFeatureRequest.OrderBy([clause])
        request.setOrderBy(orderby)
        zoneFeatures = floodedZonesAreaLayer.getFeatures(request)
        for feature in zoneFeatures:
            zoneName = feature["ZONE_CLASS"]
            zoneArea = feature["area"]
            feedback.pushInfo((zoneName) + ': ' + (str(round(zoneArea, 2))))
            lgaFloodArea = lgaFloodArea + zoneArea
        
        #output current stage of script
        feedback.pushInfo('--------------------------------------------------------------------------')
        feedback.pushInfo("FLOOD-AFFECTED PRIVATE PARCELS:")
        feedback.pushInfo('--------------------------------------------------------------------------')
        
        #get counts for ALL flood-affected private parcels and their flood overlays
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"area\" > \'0\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        allCount = finalParcels.selectedFeatureCount()
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        allCountSBO = finalParcels.selectedFeatureCount()
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        allCountLSIO = finalParcels.selectedFeatureCount()
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        allCountFO = finalParcels.selectedFeatureCount()
        
        #output total parcel counts and by flood overlay
        feedback.pushInfo('Flood-Affected Private Parcels: ' + (str(allCount)))
        feedback.pushInfo('With SBO Overlay: ' + (str(allCountSBO)))
        feedback.pushInfo('With LSIO Overlay: ' + (str(allCountLSIO)))
        feedback.pushInfo('With FO Overlay: ' + (str(allCountFO)))
        feedback.pushInfo('BY ZONE:')
        feedback.pushInfo('---------------------------------')
        
        #get counts for GRZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'GRZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        grzCount = finalParcels.selectedFeatureCount()
        if grzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'GRZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            grzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'GRZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            grzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'GRZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            grzCountFO = finalParcels.selectedFeatureCount()
        
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total General Residential (GRZ): ' + (str(grzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(grzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(grzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(grzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for RZ flood-affected private parcels and thier flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        rzCount = finalParcels.selectedFeatureCount()
        if rzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Residential (RZ): ' + (str(rzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(rzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(rzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(rzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for RGZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RGZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        rgzCount = finalParcels.selectedFeatureCount()
        if rgzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RGZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rgzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RGZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rgzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'RGZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            rgzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Residential Growth (RGZ): ' + (str(rgzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(rgzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(rgzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(rgzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for MUZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'MUZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        muzCount = finalParcels.selectedFeatureCount()
        if muzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'MUZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            muzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'MUZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            muzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'MUZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            muzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Mixed Use (MUZ): ' + (str(muzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(muzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(muzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(muzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for CZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        czCount = finalParcels.selectedFeatureCount()
        if czCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            czCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            czCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            czCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Commercial (CZ): ' + (str(czCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(czCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(czCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(czCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for BZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'BZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        bzCount = finalParcels.selectedFeatureCount()
        if bzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'BZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            bzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'BZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            bzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'BZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            bzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Commercial (BZ): ' + (str(bzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(bzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(bzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(bzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for INZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'INZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        inzCount = finalParcels.selectedFeatureCount()
        if inzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'INZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            inzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'INZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            inzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'INZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            inzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Industrial (INZ): ' + (str(inzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(inzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(inzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(inzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for SUZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'SUZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        suzCount = finalParcels.selectedFeatureCount()
        if suzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'SUZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            suzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'SUZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            suzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'SUZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            suzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Special Use (SUZ): ' + (str(suzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(suzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(suzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(suzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #get counts for CDZ flood-affected private parcels and their flood overlays (if applicable)
        processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CDZ\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
        cdzCount = finalParcels.selectedFeatureCount()
        if cdzCount > 0:
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CDZ\' AND \"ZONE_CODE_2\" = \'SBO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            cdzCountSBO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CDZ\' AND \"ZONE_CODE_2\" = \'LSIO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            cdzCountLSIO = finalParcels.selectedFeatureCount()
            processing.run('qgis:selectbyexpression', { 'EXPRESSION': '(\"ZONE_CLASS\" = \'CDZ\' AND \"ZONE_CODE_2\" = \'FO\')', 'INPUT': finalParcels, 'METHOD': 0 }, context=context)
            cdzCountFO = finalParcels.selectedFeatureCount()
            
            #output total parcel counts and by flood overlay
            feedback.pushInfo('Total Comprehensive Development (CDZ): ' + (str(cdzCount)))
            feedback.pushInfo('With SBO Overlay: ' + (str(cdzCountSBO)))
            feedback.pushInfo('With LSIO Overlay: ' + (str(cdzCountLSIO)))
            feedback.pushInfo('With FO Overlay: ' + (str(cdzCountFO)))
            feedback.pushInfo('---------------------------------')
        
        #end the script
        return{}
        