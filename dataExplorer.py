import json
from matplotlib import pyplot as plt

with open('newtrafficData.json', 'r') as file:
    filedata = file.read()
    data = json.loads(filedata)

    for i in data:
        try:
            print i['name']
        except:
            print 'no name'

    fig1 = plt.figure(1)
    fig1.canvas.set_window_title('2 Lanes Average Distance Between cars for 64 cars')

    plt.figure(1)
    plt.subplot(221)
    plt.plot(data[3]['distance'][0])
    plt.title('road1')
    plt.ylabel('averge distance between car start points')
    plt.xlabel('time')

    plt.subplot(222)
    plt.plot(data[3]['distance'][1])
    plt.title('road2')
    plt.ylabel('averge distance between car start points')
    plt.xlabel('time')

    plt.subplot(223)
    plt.plot(data[3]['distance'][2])
    plt.title('road3')
    plt.ylabel('averge distance between car start points')
    plt.xlabel('time')

    plt.subplot(224)
    plt.plot(data[3]['distance'][3])
    plt.title('road4')
    plt.ylabel('averge distance between car start points')
    plt.xlabel('time')

    fig2 = plt.figure(2)
    fig2.canvas.set_window_title('2 Lanes Average Speed for 64 cars')

    plt.figure(2)
    plt.subplot(221)
    plt.plot(data[3]['speed'][0])
    plt.title('road1')
    plt.ylabel('average speed')
    plt.xlabel('time')

    plt.subplot(222)
    plt.plot(data[3]['speed'][1])
    plt.title('road2')
    plt.ylabel('average speed')
    plt.xlabel('time')

    plt.subplot(223)
    plt.plot(data[3]['speed'][2])
    plt.title('road3')
    plt.ylabel('average speed')
    plt.xlabel('time')

    plt.subplot(224)
    plt.plot(data[3]['speed'][0])
    plt.title('road4')
    plt.ylabel('average speed')
    plt.xlabel('time')

    plt.show()

