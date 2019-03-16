# Created by Jianwei Huang
#Generated trajectory set as .shp from GPS row .csv file
#Input 'road_file': the city road network trajectory belongs to remove outlier points. %Shapefile
#Input 'Taxi_pointset': the GPS trajectory points dataset which have been sorted by car id and time.
#output New_shp_file: the GPS trajectory polyline set as output.
#output New_csv_file: the new GPS trajectory points dataset which related to GPS trajectory polyline.

import gdal
import ogr,osr
from math import *
import os

def calcDistance(lat1, lon1, lat2, lon2):
    #Calculate the great circle distance between two points  on the earth (specified in decimal degrees)
    EARTH_RADIUS = 6378.137
    #
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine
    dlon = lon1 - lon2
    dlat = lat1 - lat2
    s = 2 * asin(sqrt(pow(sin(dlat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon / 2), 2)))
    s = s * EARTH_RADIUS
    #s = round(s * 10000) / 10000;
    return s

def ExtarctBoxFromShp(shpfile):
    driver=ogr.GetDriverByName('ESRI Shapefile')
    dataSource=driver.Open(shpfile,0)
    layer=dataSource.GetLayer()
    minX,maxX,minY,maxY=layer.GetExtent()
    return minX,maxX,minY,maxY

def ClearTrajectory(Trajectory,minX,maxX,minY,maxY):
    Prepoint=Trajectory[0]
    l=len(Trajectory)

    for i in range(0,l):
        line=Trajectory[i]
        lat=float(line[3])
        lot=float(line[4])
        if lat < minX or lat>maxX or lot<minY or lot>maxY:
            Trajectory=[]
            break;
        if i>0:
            lat1=float(Prepoint[3])
            lot1=float(Prepoint[4])
            distance=calcDistance(lat1,lot1,lat,lot)
            if distance>1:
                Trajectory=[]
                break
            else:
                Prepoint=line
    if len(Trajectory)>2:
        return Trajectory
    else:
        Trajectory=[]
        return Trajectory
def PointClear(txt_file,Taxi_pointset,minX,maxX,minY,maxY,new_layer):
    PointData=open(Taxi_pointset,'r')
    head=PointData.readline()
    # head=head+',polyline_ID'
    # head=head.split('\,')
    # head=head[1:]
    head2='CarId,date,lat,lot,Direction,Speed,state,Polyline_id'
    txt_file.write(head2+'\n')
    Trajectory=[]
    k=0
    for line in PointData.readlines():
        line=line.strip('\n')
        line=line.split(',')
        CarId=line[1]
        lat=line[3]
        lot=line[4]
        state=line[-1]
        if len(Trajectory)!=0:
            line2=Trajectory[-1]
            CarId2=line2[1]
            state2=line2[-1]
            # if CarId == CarId2 and state == '1':
            if CarId==CarId2 and state==state2:
                Trajectory.append(line)
            else:
                Trajectory=ClearTrajectory(Trajectory,minX,maxX,minY,maxY)
                l=len(Trajectory)
                if l!=0:
                    Multiline = ogr.Geometry(ogr.wkbLineString)
                    feature = ogr.Feature(new_layer.GetLayerDefn())
                    for i in range(0,l):
                        row=Trajectory[i]
                        txt_file.write(row[1]+','+row[2]+','+row[3]+','+row[4]+','+row[5]+','+row[6]+','+row[-1]+','+str(k)+'\n')
                        if i==0:
                            feature.SetField('CarId',row[1])
                            feature.SetField('startLat',row[3])
                            feature.SetField('startLot',row[4])
                            #time=row[2].split(' ')
                            feature.SetField('startTime',row[2])
                            feature.SetField('state',row[-1])
                            feature.SetField('id',k)

                            Multiline.AddPoint(float(row[3]),float(row[4]))
                        elif i==l-1:
                            feature.SetField('endLat',row[3])
                            feature.SetField('endLot',row[4])
                            #time=row[2].split(' ')
                            feature.SetField('endTime',row[2])
                            Multiline.AddPoint(float(row[3]),float(row[4]))
                            feature.SetGeometry(Multiline)
                            layer.CreateFeature(feature)
                        else:
                            Multiline.AddPoint(float(row[3]),float(row[4]))
                    k += 1
                Trajectory=[]
        # elif len(Trajectory)==0 and line[-1]=='1':
        elif len(Trajectory) == 0:
            Trajectory.append(line)

if __name__ == '__main__':

    road_file=r''
    Taxi_pointset=r''
    New_shp_file=r''
    New_csv_file=r''
    txt_file=open(New_csv_file,'w')
    driver=ogr.GetDriverByName('ESRI Shapefile')
    data_source=driver.CreateDataSource(New_shp_file)
    srs=osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    layer=data_source.CreateLayer('20140509Trajectory',srs,ogr.wkbLineString)
    field_carid=ogr.FieldDefn('CarId',ogr.OFTInteger64)
    layer.CreateField(field_carid)
    field_startLat=ogr.FieldDefn('startLat',ogr.OFTReal)
    layer.CreateField(field_startLat)
    field_startLot = ogr.FieldDefn('startLot', ogr.OFTReal)
    layer.CreateField(field_startLot)
    field_endLat = ogr.FieldDefn('endLat', ogr.OFTReal)
    layer.CreateField(field_endLat)
    field_endLot = ogr.FieldDefn('endLot', ogr.OFTReal)
    layer.CreateField(field_endLot)
    field_startTime=ogr.FieldDefn('startTime',ogr.OFTString)
    layer.CreateField(field_startTime)
    field_endTime=ogr.FieldDefn('endTime',ogr.OFTString)
    layer.CreateField(field_endTime)
    field_state=ogr.FieldDefn('state',ogr.OFTReal)
    layer.CreateField(field_state)
    field_id=ogr.FieldDefn('id',ogr.OFTReal)
    layer.CreateField(field_id)

    minX,maxX,minY,maxY=ExtarctBoxFromShp(road_file)
    PointClear(txt_file,Taxi_pointset,minX,maxX,minY,maxY,layer)
    txt_file.close()

    print(0)
