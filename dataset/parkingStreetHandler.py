from bot.models import User
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon as GEOPolygon
from persistence import cronologyHandler, userHandler, multiPolygonHandler, parkingZoneHandler, timeSlotHandler
import polyline
from staticmap import StaticMap, Polygon, Line, IconMarker, CircleMarker
from PIL import Image, ImageDraw, ImageColor
#from shapely.geometry import Polygon as shapelyPolygon
from smartBot import settings
from allauth.socialaccount.providers import google
import googlemaps
import random
import telegram
from telegram.keyboardbutton import KeyboardButton

listOfColorName = ['Red', 'Blue', 'Purple', 'Green', 'Yellow', 'Brown', 'Orange', 'Grey']

def getAllPolygonsInCircleArea(geoCircle):
    list = []
    listOfColor = []
    listOfMultiPolygon = []
    multiPolygons = multiPolygonHandler.getAllMultiPolygon()
    for multiP in multiPolygons:
        coordinates = multiP.poly.coords
        i = 0
        color = getRandomColor()
        while i < len(coordinates):
            geoPoly = GEOPolygon(coordinates[i][0])
            if geoCircle.intersects(geoPoly):
               list.append(geoPoly)
               listOfColor.append(color)
               listOfMultiPolygon.append(multiP)
            i = i + 1
    return list, listOfColor, listOfMultiPolygon 

def getRandomColor():
    r = lambda: random.randint(0,255)
    color = '#%02X%02X%02X' % (r(),r(),r())
    return color
   
def buildParkingZoneMessage(listPolygon):
    text = ''
    i = 0
    for polygon in listPolygon:
        listOfParkingZone = parkingZoneHandler.getParkingZoneByName(polygon.name)
        for parkingZone in listOfParkingZone:
            text += '<b>The price for the ' + listOfColorName[i] + ' zone is: </b>' + parkingZone.price + ' Euro \n'
            if parkingZone.maxHours == 0:
                text += 'You can stay as much as you want in the following time: \n'
            elif parkingZone.maxHours == 60:
                text += 'You can stay for only 1 Hour in the following time: \n'
            elif parkingZone.maxHours == 120:
                text += 'You can stay for only 2 Hours in the following time: \n'
            elif parkingZone.maxHours == 180:
                text += 'You can stay for only 3 Hours in the following time: \n'
            elif parkingZone.maxHours == 240:
                text += 'You can stay for only 4 Hours in the following time: \n'
            listOfTimeSlot = timeSlotHandler.getTimeSlotById(parkingZone.id)
            print(listOfTimeSlot)
            for timeSlot in listOfTimeSlot:
                text += timeSlot.days + ': ' + timeSlot.hours + '\n'
        i = i + 1    
    return text
            
def location(bot, update):
    # Colors: Red, Blue, Purple, Green, Yellow, Brown, Orange, Grey
    
    listOfColor = ['#8B0000', '#0000FF', '#8A2BE2', '#228B22', '#FFD700', '#8B4513', '#D2691E', '#808080']
    print("parkingStreetHandler.location")
    user = User.objects.get(chat_id=update.message.chat_id)
    point = Point(user.lon, user.lat)
    #Distance in KM to search the parkings close by
    radius = 0.5
    radius = radius/40000*360
    circle = point.buffer(radius)
    print('valori cerchio: ' + str(circle))
    shape = multiPolygonHandler.getMultiPolygonByPoint(point)
    #shape = multiPolygonHandler.getAllMultiPolygon()
    #print(shape)
    m = StaticMap(600, 800, 12, 12, tile_size=256)
    #icon_flag = IconMarker((user.lon, user.lat), './bot/static/images/marker.png', 100, 100)
    marker_outline = CircleMarker((user.lon, user.lat), 'white', 22)
    marker = CircleMarker((user.lon, user.lat), 'Red', 18)
    m.add_marker(marker_outline)
    m.add_marker(marker)
    #m = StaticMap(width=600, height=800)
    circleLine = Line(circle[0], color='red', width=3)
    geoCircle = GEOPolygon(circle[0])
    #DISEGNA IL CERCHIO PER CONTROLLARE I PARCHEGGI LIMITROFI
    m.add_line(circleLine)
    listPolygon, listOfColor2, listOfMultiPolygon = getAllPolygonsInCircleArea(geoCircle)
    i = 0
    if len(listPolygon) is not 0:
        for p in listPolygon:
            polygonLine = Line(p[0], color=listOfColor[i], width=3)
            m.add_line(polygonLine)
            i = i + 1
        image = m.render(zoom=14)
        fileName = 'ParkingStreet' + str(update.message.chat_id) + '.png'
        image.save(fileName)
        baseDir = settings.BASE_DIR
        picture = open(baseDir + '/' + fileName, 'rb')
        text = buildParkingZoneMessage(listOfMultiPolygon)
        btn_keyboard1 = KeyboardButton(text="Find another parking")
        btn_keyboard2 = KeyboardButton(text="Find closest electric charge point")
        btn_keyboard3 = KeyboardButton(text="Show my profile")
        btn_keyboard4 = KeyboardButton(text="That's all, thanks")
        custom_keyboard = [[btn_keyboard1],[btn_keyboard2],[btn_keyboard3], [btn_keyboard4]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendPhoto(chat_id=update.message.chat_id, photo = picture)
        bot.sendMessage(chat_id=update.message.chat_id, text=text, parse_mode='HTML')
        bot.sendMessage(chat_id=update.message.chat_id, text='What do you want to do now?', reply_markup=reply_markup)
        userHandler.setUserBotActived(update.message.chat_id, True)
    else:
        btn_keyboard1 = KeyboardButton(text="Find another parking")
        btn_keyboard2 = KeyboardButton(text="Find closest electric charge point")
        btn_keyboard3 = KeyboardButton(text="Show my profile")
        btn_keyboard4 = KeyboardButton(text="That's all, thanks")
        custom_keyboard = [[btn_keyboard1],[btn_keyboard2],[btn_keyboard3], [btn_keyboard4]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id, text='There is no parking info close to your position.')
        bot.sendMessage(chat_id=update.message.chat_id, text='What do you want to do now?', reply_markup=reply_markup)
        userHandler.setUserBotActived(update.message.chat_id, True)

    
