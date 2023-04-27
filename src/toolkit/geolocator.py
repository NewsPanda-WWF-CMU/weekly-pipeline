import pandas as pd 

def get_geomap():
    geomap = {}
    print("Reading CMU_XY.xlsx location files.....")
    pas = pd.read_excel("./reference-files/CMU_XY.xlsx", sheet_name="PAs")
    for n,x,y in zip(pas["NAME"], pas.X, pas.Y):
        geomap[n] = (x,y)
    kba = pd.read_excel("./reference-files/CMU_XY.xlsx", sheet_name="KBA")
    for n,x,y in zip(kba["IntName"], kba.X, kba.Y):
        geomap[n] = (x,y)
    tiger_heartlands = pd.read_excel("./reference-files/CMU_XY.xlsx", sheet_name="Tiger Heartlands")
    for n,x,y in zip(tiger_heartlands["Site Name"], tiger_heartlands.X, tiger_heartlands.Y):
        geomap[n] = (x,y)


    # Manually encode state centroids:
    # Coordinates taken from Wikipedia state pages
    
    ### Switch these two coordinates
    geomap["Andhra Pradesh"] = (80.65, 16.50)
    geomap["Arunachal Pradesh"] = (93.37, 27.06)
    geomap["Assam"] = (91.77, 26.14)
    geomap["Chhattisgarh"] = (81.60, 21.25)
    geomap["Goa"] = (73.83, 15.50)
    geomap["Gujarat"] = (72.41, 23.13)
    geomap["Haryana"] = (76.47, 30.44)
    geomap["Himachal Pradesh"] = (77.10, 31.61)
    geomap["Jammu and Kashmir"] = (76.50, 34.00)
    geomap["Jharkhand"] = (85.33, 23.35)
    geomap["Karnataka"] = (77.50, 12.97)
    geomap["Kerala"] = (76.00, 10.00)
    geomap["Madhya Pradesh"] = (77.95, 23.47)
    geomap["Maharashtra"] = (72.82, 18.97)
    geomap["Manipur"] = (93.91, 24.66)
    geomap["Meghalaya"] = (91.88, 25.57)
    geomap["Mizoram"] = (92.8, 23.36)
    geomap["Nagaland"] = (94.12, 25.67)
    geomap["Orissa"] = (85.82, 20.27)
    geomap["Punjab"] = (75.84, 30.79)
    geomap["Rajasthan"] = (73.8, 26.6)
    geomap["Sikkim"] = (88.30, 27.33)
    geomap["Tamil Nadu"] = (80.27, 13.09)
    geomap["Telangana"] = (78.475, 17.366)
    geomap["Tripura"] = (91.28, 23.84)
    geomap["Uttar Pradesh"] = (80.91, 26.85)
    geomap["Uttarakhand"] = (78.06, 30.33)
    geomap["West Bengal"] = (87.75, 22.98)


    return geomap


################################################################################

# # importing geopy library
# from geopy.geocoders import Nominatim
 
# # calling the Nominatim tool
# loc = Nominatim(user_agent="GetLoc")

# # ===== OUTPUT: =====
# # Corbett National Park, Dhoomakot, Pauri Garhwal, Uttarakhand, India
# # Latitude =  29.5573817 
# # Longitude =  78.84257645094397

# def get_long_lat(locs):
#     address, long, lat = [], [], []
#     for l in locs:
#         getLoc = loc.geocode(l)
#         try:
#             a = getLoc.address
#             if a.split(',')[-1].strip()=="India":
#                 address.append(getLoc.address)
#                 long.append(getLoc.longitude)
#                 lat.append(getLoc.latitude)
#         except: 
#             continue
#     return address, long, lat


# from geopy.geocoders import Nominatim
# import time
# from pprint import pprint
# app = Nominatim(user_agent="tutorial")
# location = app.geocode("Valmiki Tiger Reserve").raw
# # print raw data
# pprint(location)