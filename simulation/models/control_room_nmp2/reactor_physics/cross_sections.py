import math

MicroscopicCrossSections = {	
	"Fuel" : {
		"U235" : {
			"Thermal" : {
				"Scattering" : 10,
				"Capture" : 99,
				"Fission" : 583,
			},
			"Fast" : {
				"Scattering" : 4,
				"Capture" : 0.09,
				"Fission" : 1,
			}
		},
		"U238" : {
			"Thermal" : {
				"Scattering" : 9,
				"Capture" : 2,
				"Fission" : 0.00002,
			},
			"Fast" : {
				"Scattering" : 5,
				"Capture" : 0.07,
				"Fission" : 0.3,
			}
		},
		"Pu239" : {
			"Thermal" : {
				"Scattering" : 8,
				"Capture" : 269,
				"Fission" : 748,
			},
			"Fast" : {
				"Scattering" : 5,
				"Capture" : 0.05,
				"Fission" : 2,
			}
		},
	},
	"Absorber" : {
		"B10" : {
			"Thermal" : {
				"Scattering" : 2,
				"Capture" : 200,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 2,
				"Capture" : 0.4,
				"Fission" : 0,
			}
		},
		"Cd113" : {
			"Thermal" : {
				"Scattering" : 100,
				"Capture" : 30,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 4,
				"Capture" : 0.05,
				"Fission" : 0,
			}
		},
		"Xe135" : {
			"Thermal" : {
				"Scattering" : 400,
				"Capture" : 2600000,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 5,
				"Capture" : 0.0008,
				"Fission" : 0,
			}
		},
		"In115" : {
			"Thermal" : {
				"Scattering" : 2,
				"Capture" : 100,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 4,
				"Capture" : 0.02,
				"Fission" : 0,
			}
		},
	},
	"StructuralMaterials" : {
		"Zr90" : {
			"Thermal" : {
				"Scattering" : 5,
				"Capture" : 0.006,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 5,
				"Capture" : 0.006,
				"Fission" : 0,
			}
		},
		"Fe56" : {
			"Thermal" : {
				"Scattering" : 10,
				"Capture" : 2,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 20,
				"Capture" : 0.003,
				"Fission" : 0,
			}
		},
		"Cr52" : {
			"Thermal" : {
				"Scattering" : 3,
				"Capture" : 0.5,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 3,
				"Capture" : 0.002,
				"Fission" : 0,
			}
		},
		"Ni58" : {
			"Thermal" : {
				"Scattering" : 20,
				"Capture" : 3,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 3,
				"Capture" : 0.008,
				"Fission" : 0,
			}
		},
		"O16" : {
			"Thermal" : {
				"Scattering" : 4,
				"Capture" : 0.0001,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 3,
				"Capture" : 0.0000000003,
				"Fission" : 0,
			}
		},
	},
	"Moderator" : {
		"H1" : {
			"Thermal" : {
				"Scattering" : 20,
				"Capture" : 0.2,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 4,
				"Capture" : 0.00004,
				"Fission" : 0,
			}
		},
		"H2" : {
			"Thermal" : {
				"Scattering" : 4,
				"Capture" : 0.0003,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 3,
				"Capture" : 0.000007,
				"Fission" : 0,
			}
		},
		"C12" : {
			"Thermal" : {
				"Scattering" : 5,
				"Capture" : 0.002,
				"Fission" : 0,
			},
			"Fast" : {
				"Scattering" : 2,
				"Capture" : 0.00001,
				"Fission" : 0,
			}
		},
	}
}

MacroscopicCrossSections = {
	"Moderator" : {
		"H1" : {
			"Capture" : MicroscopicCrossSections["Moderator"]["H1"]["Thermal"]["Capture"]
		},
		"H2" : {
			"Capture" : MicroscopicCrossSections["Moderator"]["H2"]["Thermal"]["Capture"]
		},
		"C12" : {
			"Capture" : MicroscopicCrossSections["Moderator"]["C12"]["Thermal"]["Capture"] * 10000000000000000000000.1331046540671051
		},
	},
	"Poisons" : {
		"Xe135" : {
			"Capture" : MicroscopicCrossSections["Absorber"]["Xe135"]["Thermal"]["Capture"] * 2000000000000000000000.629160592592593
		}
	},
	"Absorbers" : {
		"B10" : {
			"Capture" : MicroscopicCrossSections["Absorber"]["B10"]["Thermal"]["Capture"] * 10000000000000000000000.38506
		}
	}
}

