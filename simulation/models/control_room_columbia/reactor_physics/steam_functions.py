import math
import iapws

def getRegion1Data(temperature,pressure):

	pressure = min(pressure,1.0342e7)

	T = temperature+273.15 #Temperature, [K]
	P = pressure/1e6 #Pressure, [MPa]
	
		
	data = iapws.iapws97._Region1(T,P)


	return data


def getBoilingPointForWater(Pressure):
	Pressure = Pressure/1e6 #Pressure, [MPa]
	try:
		boiling_point_k = iapws.iapws97._TSat_P(Pressure)
	except:
		boiling_point_k = 373.15 #100c

	boiling_point_c = boiling_point_k - 273.15
	
	return min(max(100,boiling_point_c),350)

6
def vaporize(initialMass, temperature, pressure, delta):
	pressure = pressure+1
	boilingPoint = getBoilingPointForWater(pressure)

	data = getRegion1Data(temperature,pressure)

	specificHeatWater = data["cp"]
	specificVaporEnthalpy = data["h"]
	
	deltaSteamMass = ((temperature-boilingPoint) * specificHeatWater * initialMass) / specificVaporEnthalpy
	vaporizedMass = deltaSteamMass*delta

	return {"vm":vaporizedMass, "bp":boilingPoint}

