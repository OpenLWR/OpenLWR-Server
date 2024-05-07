import math

NeutronModeratingParameters = {
	"H20" : 0.920,
	"D2O" : 0.509,
	"C" : 0.152,
}

def getNeutronVelocity(avg_Neutron_Energy):
	return 1.386*(10**6)*math.sqrt(avg_Neutron_Energy) # km/s

def getNeutronDensity(neutronAmount, volume):
	return neutronAmount/volume # cm2


def getNeutronFlux(neutronDensity, neutronVelocity):
	return neutronDensity * neutronVelocity # n/cm2/s


def getNeutronEnergy(temperature):
	return 1.386*(10**6)*(temperature+273.15) # MeV


def getReactionRate(neutronFlux, macroscopicCrossSectionU235):
	return neutronFlux/(2.43*macroscopicCrossSectionU235)/202.5


def getThermalPower(reactionRate, Volume):
	return reactionRate*Volume*202.5*1.602e-13
