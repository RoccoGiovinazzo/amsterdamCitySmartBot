import json
import urllib.request
from django.contrib.gis.geos import GEOSGeometry
import numpy as np
from bot.models import MultiPolygon, ParkingZone
from persistence import multiPolygonHandler, parkingZoneHandler, timeSlotHandler

def loadJSON():
    urld = 'https://amsterdam-maps.bma-collective.com/embed/parkeren/deploy_data/tarieven.json'
    r = urllib.request.urlopen(urld)
    data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
    geometryNames = []
    for singleData in data:
        geometryNames.append(singleData)
    #print(geometryNames)    
    data = convertData(data, geometryNames)
    #print(data)
    tot = parkingZoneHandler.getNumberOfParkingZone()
    for name in geometryNames:
        print(name)
        print(str(data[name]['tarieven']))
        pnt = GEOSGeometry(str(data[name]['location']))
        multiPolygonHandler.createMultiPolygon(name, pnt, 0)
        multiPolygon = multiPolygonHandler.getMultiPolygon(name)
        if tot == 0:
            extractCost(data[name]['tarieven'], multiPolygon)    

def extractCost(data, multiPolygon):

    for d in data:
        print(str(d))
        if str(d) == '0' or str(d) == '60' or str(d) == '120' or str(d) == '180' or str(d) == '240':
            print('Parcheggio con orario massimo')
            print('Ore massime: ' + str(d))
            prezzi = data[d]
            print('valore della chiave: ' + str(data[d]))
            for key1 in prezzi:
                print('Prezzo: ' + str(key1))
                parkingZone = ParkingZone()
                parkingZone.price = str(key1)
                parkingZone.maxHours = str(d)
                parkingZone.multi_polygon = multiPolygon
                parkingZoneHandler.saveParking(parkingZone)
                giorni = prezzi[key1]
                for key2 in giorni:
                    print('Orario: ' + str(key2))
                    print('Giorni: ' + str(giorni[key2]))
                    timeSlotHandler.createTimeSlot(str(key2), str(giorni[key2]), parkingZone)
        else:
            print('Parcheggio con orario normale')
            for key1 in d:
                print('Prezzo: ' + str(key1))
                print('Valore: ' + str(d[key1]))
                print(' ')
                parkingZone = ParkingZone()
                parkingZone.price = str(key1)
                parkingZone.maxHours = 0
                parkingZone.multi_polygon = multiPolygon
                parkingZoneHandler.saveParking(parkingZone)
                giorni = d[key1]
                for key2 in giorni:
                    print('Orario: ' + str(key2))
                    print('Giorni: ' + str(giorni[key2]))
                    timeSlotHandler.createTimeSlot(str(key2), str(giorni[key2]), parkingZone)

    
def convertData(data, geometryNames):
    i = 0
    
    for name in geometryNames:
        i = i + 1
        j = 0
        for subArray in data[name]['location']['coordinates']:
            arrayToModify = data[name]['location']['coordinates'][j][0]
            #print('CONTROLLO POLIGONI' + str(data[name]['location']['coordinates']))
            x = np.array(arrayToModify)
            y = x.astype(np.float)
            y = np.array(y).tolist()
            data[name]['location']['coordinates'][j][0] = y
            j = j + 1 
    return data
