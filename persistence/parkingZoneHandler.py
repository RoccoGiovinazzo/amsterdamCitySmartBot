
from bot.models import MultiPolygon, ParkingZone

def createParking(price, maxHours, multiPolygon):
    parking = Parking()
    parking.price = price
    parking.maxHours = maxHours
    parking.multi_polygon = multiPolygon
    parking.save() 
    
def saveParking(parkingZone):
    parkingZone.save()
    
def getNumberOfParkingZone():
    list = ParkingZone.objects.all()
    print("NUMERO DI PARKING ZONE: " + str(len(list)))
    return len(list)

def getParkingZoneByName(name):
    list = ParkingZone.objects.filter(multi_polygon = name)
    return list