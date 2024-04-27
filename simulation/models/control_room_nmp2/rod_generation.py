import math

def run(rods):
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
						"insertion": 48.00,
						"scram": False,
						"accum_pressure": 1400.00, #normal pressure is around 1400 psig
						"accum_trouble": False,
						"accum_trouble_acknowledged": False,
						"drift_alarm": False,
						"driving": False,
						"select": False,
				}
				# increment y by 4 because we only have a control rod per every four fuel assemblies
				x += 4

				# keep track of how many rods we're generating
				rods_generated_row += 1
				rods_generated_total += 1

			# move on to the next row
			rods_generated_row = 0
			y -= 4
			break
