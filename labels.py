# a python script to create center points for labels for the
# Military Grid Reference System (MGRS) zones

from osgeo import ogr
from osgeo import osr
import os
import sys

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def PolygonCentroids(inLayer, outLayer, outLayerName):

   # we're working only with Shapefiles
   driver = ogr.GetDriverByName("ESRI Shapefile")
   
   # set shapefile, driver, and datasource (ds) for the input
   in_layer = inLayer
   ds = driver.Open(in_layer, 0)
   in_layer = ds.GetLayer()
   in_srs = in_layer.GetSpatialRef()
   
   # output SpatialReference
   out_srs = osr.SpatialReference()
   out_srs.ImportFromEPSG(3857)
   
   # create the CoordinateTransformation
   coordTrans = osr.CoordinateTransformation(in_srs, out_srs)

   # set the output layer (shapefile)... we're putting the labels
   # at the centroids
   out_layer = outLayer
   
   # remove output file if already there
   if os.path.exists(out_layer):
       driver.DeleteDataSource(out_layer)
   
   # create the output shapefile
   ods = driver.CreateDataSource(out_layer)
   out_layer = ods.CreateLayer(outLayerName, out_srs, geom_type = ogr.wkbPoint)
   
   # add input file fields to output file
   in_layer_defs = in_layer.GetLayerDefn()
   for i in range(0, in_layer_defs.GetFieldCount()):
       defn = in_layer_defs.GetFieldDefn(i)
       out_layer.CreateField(defn)
   
   # get the label layer feature definition
   labels_defs = out_layer.GetLayerDefn()

   # grab totals for progress bar
   field_count = labels_defs.GetFieldCount()
   total = in_layer.GetFeatureCount() * field_count

   # loop create the new layer
   for i in range(0, in_layer.GetFeatureCount()):

       # grab current in_layer feature and define new out_layer feature
       in_feat = in_layer.GetFeature(i);
       out_feat = ogr.Feature(labels_defs)
   
       # populate the feature field data
       for j in range(0, field_count):
           out_feat.SetField(labels_defs.GetFieldDefn(j).GetNameRef(),
                   in_feat.GetField(j))

           progress(i*field_count + j, total, "processed")
   
       # get the geometry and the centroids... transforming for
       # for the preferred SRS
       geom = in_feat.GetGeometryRef()
       geom.Transform(coordTrans)
       centroid = geom.Centroid()
       out_feat.SetGeometry(centroid)
       out_layer.CreateFeature(out_feat)
   
       # reset the pointers
       in_feat = None
       out_feat = None
   
   
   # close and reset
   in_layer.ResetReading()
   ds = None
   ods = None


# apply the function to the two sets
print("\nProcessing MGRS 100km Zones")
PolygonCentroids("MGRS_100km_world.shp", "MGRS_100km_world_labels.shp", "MGRS_100km_labels")
print("\nProcessing MGRS Grid Zone Designators (GZD)")
PolygonCentroids("MGRS_GZD_world.shp", "MGRS_GZD_world_labels.shp", "MGRS_GZD_labels")

