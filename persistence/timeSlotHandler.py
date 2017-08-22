
from bot.models import MultiPolygon, ParkingZone, TimeSlot

def createTimeSlot(hours, days, parking):
    timeSlot = TimeSlot()
    timeSlot.hours = hours
    timeSlot.days = days
    timeSlot.parking = parking
    timeSlot.save()
    
def getTimeSlotById(id):
    list = TimeSlot.objects.filter(parking_id = id)
    return list