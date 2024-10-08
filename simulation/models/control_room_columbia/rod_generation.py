import math

def generate_lprm(lprm):
	from simulation.models.control_room_columbia.neutron_monitoring import local_power_range_monitors

	exempt_lprms = {
		"56-49",
		"48-57",
	}

	if lprm in exempt_lprms: return

	local_power_range_monitors[lprm] = {
		"D": {
				"power": 0.00,
				
				"upscale_setpoint": 117.00,
				"downscale_setpoint": 25.00,
		},
		"C": {
				"power": 0.00,
				
				"upscale_setpoint": 117.00,
				"downscale_setpoint": 25.00,
		},
		"B": {
				"power": 0.00,
				
				"upscale_setpoint": 117.00,
				"downscale_setpoint": 25.00,
		},
		"A": {
				"power": 0.00,
				
				"upscale_setpoint": 117.00,
				"downscale_setpoint": 25.00,
		},
	}

def run(rods,buttons):
	x = 18
	y = 59
	rods_to_generate = 0
	rods_generated_row = 0
	rods_generated_total = 0

	# our reactor has a total of 185 rods
	while rods_generated_total < 185:
		# calculate how many control rods we need for each row, 
		# and our starting position on y (as the rods in a BWR core are in a circular pattern)
		if y == 59 or y == 3:
			rods_to_generate = 7
			x = 18
		elif y == 55 or y == 7:
			rods_to_generate = 9
			x = 14
		elif y == 51 or y == 11:
			rods_to_generate = 11
			x = 10
		elif y == 47 or y == 15:
			rods_to_generate = 13
			x = 6
		elif y <= 43 and y >= 19:
			rods_to_generate = 15
			x = 2

		while x <= 58 and y <= 59:
			# create rods
			while rods_generated_row < rods_to_generate:
				# there's probably a better way to do this...
				# i dont know obamacode, is there?
				x_str = str(x)
				if len(x_str) < 2:
					x_str = "0%s" % x_str

				y_str = str(y)
				if len(y_str) < 2:
					y_str = "0%s" % y_str

				rod_number = "%s-%s" % (x_str, y_str)

				rods[rod_number] = {
                        #TODO: set this back to 00.00. 48 is for testing.
						"insertion": 26.00,
						"scram": False,
						"accum_pressure": 1700.00, #normal pressure is around 1700 psig
						"accum_trouble": False,
						"accum_trouble_acknowledged": False,
						"reed_switch_fail" : False,
						"drift_alarm": False,
						"driftto": -15,
						"driving": False,
						"select": False,
						"x" : x,
						"y" : y,

						#physics stuff
	  					"neutrons" : 250000000000,
						"neutrons_last" : 250000000000,
				}

				if ((x/4) - 0.5) % 2 != 0: #generate LPRMs
					if ((y/4) - 0.75) % 2 != 0:
						lprm_x = str(x+2)
						if len(lprm_x) < 2:
							lprm_x = "0%s" % lprm_x

						lprm_y = str(y+2)
						if len(lprm_y) < 2:
							lprm_y = "0%s" % lprm_y

						generate_lprm("%s-%s" % (lprm_x, lprm_y))

				# increment y by 4 because we only have a control rod per every four fuel assemblies
				x += 4

				# keep track of how many rods we're generating
				rods_generated_row += 1
				rods_generated_total += 1

			# move on to the next row
			rods_generated_row = 0
			y -= 4
			break

