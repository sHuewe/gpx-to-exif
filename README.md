# GPX To Exif
This python project adds gps information from gpx files to images. 

## Setup
The project uses docker and docker-compose. If you have installed these dependencies, just clone this repo, put your data to ./source and ./target, modify docker-compose to the timezone of your pictures and run 
```
docker-compose up
```

## What is the meaning of the timezone?
In line 13 from docker-compose you have to provide the correct timezone. Exif data only have stored the plane date-string without offering information about the used timezone. This is why you have to provide this information to the script.

## What about the source folder?
The source folder should contain one or multiple gpx-files which cover the timespan from the images in the target folder. All valid gpx files according to [gpx version 1.1](https://en.wikipedia.org/wiki/GPS_Exchange_Format) are recognized. A suitable android app to provide gpx files is the [Secure GPX Tracker app](https://play.google.com/store/apps/details?id=de.shuewe.locationsaver).
