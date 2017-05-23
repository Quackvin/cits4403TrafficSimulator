import json
from matplotlib import pyplot as plt

with open('trafficData.json', 'r') as file:
    filedata = file.read()
    data = json.loads(filedata)
    print len(data)
    print data[-1]

    for i in data:
        try:
            print i['name']
        except:
            print 'no name'

    speedData = data[0]['speed']
    distanceData = data[0]['distance']


