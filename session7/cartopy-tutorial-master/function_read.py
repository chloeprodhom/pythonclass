#import netcdf library
from netCDF4 import Dataset as nc 
#import date conversor netcdf
from netCDF4 import num2date, date2num 
from datetime import date, timedelta, datetime
import numpy as np
import os
import sys


#definimos una funcion que coge en argumento un fichiero unas latitude y longitude 
#y devuelve los datos correspondientes
def readregion3D(file, varname, lon_bnds, lat_bnds, level):
    """funcion que lee los datos 3D en una region
    filename: path de un fichiero netcdf
    varname: nombre de la variable
    lon_bnds: array, list o tuple que contiene los limites de la caja a selecionar
    lat_bnds: array, list o tuple que contiene los limites de la caja a selecionar
    return: var, time, lon, lat
    """
    
    #empezamos por leer el fichiero ncep de t2m global
    try :
        file = nc(file, "r") # open the netcdf file 
    except:
        print("el fichiero "+file+" no existe.")
        sys.exit(1)
        
    #leer time axis
    if "time" in file.variables.keys():
        timevar = file.variables["time"]
    else:
        print("no variable time in the file")
        sys.exit(1)
        
    dates = num2date(timevar[:], units=timevar.units) 
    #leer longitude
    if "lon" in file.variables.keys():    
        lon = file.variables["lon"][:]
    else:
        print("no variable lon in the file")
        sys.exit(1)
    #leer latitude
    if "lat" in file.variables.keys():    
        lat = file.variables["lat"][:]
    else:
        print("no variable lat in the file")
        sys.exit(1)
        
    #read level   
    if "level" in file.variables.keys():    
        lev = file.variables["level"][:]
    else:
        print("no variable level in the file")
        sys.exit(1)
        
    #check the existence and the dimension of varname
    if not(varname in file.variables.keys()):
        print("no variable "+varname+" in the file")
        sys.exit(1)
    elif len(file.variables[varname].shape)!=4:
        print("This function is done to read varable of size 4")
        sys.exit(1)
        
    #convitimos las listas en numpy array 
    lon_bnds = np.array(lon_bnds)
    lat_bnds = np.array(lat_bnds)
    # if longitude is written in negative convert it in value from 0 to 360 
    #(if it is consistent with the longitude of the file we want to read)
    #print(lon)
    lon_bnds = (lon_bnds + 360)%360
    #print(lon_bnds)
    #latitude correspondientes a la caja
    latbox = np.where((lat > lat_bnds[0])&(lat<lat_bnds[1]))[0]
    lat = lat[latbox]
    
    #find the level corresponding to the level weet want to read
    indlevel = (np.abs(lev-level)).argmin()

    if lon_bnds[0]>lon_bnds[1]:
        #print("I am here")
        #calculamos los limites de la caja al oeste de greenwitch
        lonbox1 = np.where((lon >= lon_bnds[0]))[0]
        #calculamos los limites de la caja al este de greenwitch
        lonbox2 = np.where((lon <= lon_bnds[1]))[0]
        #extraemos los datos del oeste de greenwitch
        var1 = file.variables[varname][:,indlevel,latbox,lonbox1]
        #extraemos los datos del este de greenwitch
        var2 = file.variables[varname][:,indlevel,latbox,lonbox2]
        #juntamos los dos cajas
        var = np.concatenate((var1, var2), axis = 2)
        lon = np.concatenate((lon[lonbox1], lon[lonbox2]), axis = 0)
    else:
        lonbox = np.where((lon >= lon_bnds[0]) & (lon <= lon_bnds[1]))[0]
        lon = lon[lonbox]
        var = file.variables[varname][:,indlevel,latbox,lonbox]
    return(var, dates, lon, lat)