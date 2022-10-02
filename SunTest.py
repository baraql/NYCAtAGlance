import sun

COORDS = {'longitude': -73.986623, 'latitude': 40.722718}
date = (28, 5, 2022)

sun = sun.Sun()
sunrise = sun.getSunsetTime(date, COORDS)

print(12 + sunrise['hr'] - 4)
print(sunrise['min'])
