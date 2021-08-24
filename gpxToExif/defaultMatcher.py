import json

LAT="lat"
LNG="lng"

class DefaultMatcher:

    data={}

    def __init__(self,path="/resources/default-locations.json") -> None:
        with open(path,"r") as f:
            self.data=json.load(f)
    
    def getLatLng(self,name):
        if name is None or name not in self.data.keys():
            return None,None
        return self.data[name][LAT], self.data[name][LNG]
