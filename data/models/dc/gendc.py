#! /usr/bin/env python3

import random

def model_type():
	return "DBAYES"

def variables(inputs, gates, health):
	total = inputs + gates + 2*health
	model_vars = [total]
	for i in range(total):
		model_vars.append(2)
	return model_vars

def prior(inputs, gates, health):
	total = health
	prior_vars = [total]
	i = 0
	for j in range(health):
		prior_vars.append(inputs + gates + i)
		i += 2
	return prior_vars

def transition(inputs, gates, health):
	total = 2*health
	transition_vars = [total]
	i = 0
	for j in range(health):
		transition_vars.append(inputs + gates + i)
		transition_vars.append(inputs + gates + i+1)
		i += 2
	return transition_vars

def sensor(inputs, gates, outputs):
	total = inputs + outputs
	sensor_vars = [total]
	for i in range(inputs):
		sensor_vars.append(i)
	output_gates = set()
	for j in range(outputs):
		output = random.randint(inputs, inputs+outputs-1)
		while output in output_gates:
			output = random.randint(inputs, inputs+outputs-1)
		sensor_vars.append(output)
		output_gates.add(output)
	return sensor_vars

def domain(inputs, gates, health):
	domains = []

	# inputs
	for i in range(inputs):
		domain = [1, i]
		domains.append(domain)

	# gates
	for j in range(inputs, inputs+gates):
		domain = []

		# choose gate type [and, or, not]
		gate_type = random.randint(1, 3)
		fan_in = 1
		if gate_type == 1 or gate_type == 2:
			fan_in = 2

		# domain width
		domain.append(fan_in + 2)

		# gate output variable
		domain.append(j)

		# gate input variables
		gate_inputs = {j}
		for l in range(fan_in):
			gate_input = random.randint(0, j-1)
			while gate_input in gate_inputs:
				gate_input = random.randint(0, j-1)
			domain.append(gate_input)
			gate_inputs.add(gate_input)

		# gate health variable
		gate_health = random.randint(0, health-1)
		domain.append(inputs + gates + 2*gate_health)

		domains.append(domain)
		
	# health
	curr = True
	for k in range(inputs+gates, inputs+gates+2*health):
		domain = []

		if curr:
			domain += [1, k]
		else:
			domain += [2, k, k-1]

		curr = not curr

		domains.append(domain)

	return domains

def factors(inputs, gates, health, domains):
	factors_lst = []

	# inputs
	for i in range(inputs):
		p = random.random()
		factor = [2, p, 1-p]
		factors_lst.append(factor)

	# gates
	for j in range(inputs, inputs+gates):
		domain = domains[j]
		width = domain[0]
		size = 2 ** (len(domain)-1)

		factor = [size]

		gate_type = ""
		if width == 3:
			gate_type = "not"
		elif width == 4:
			gate_type = random.choice(["and", "or"])

		instantiation = [0]*width
		for l in range(size):
			if instantiation[-1] == 0:
				factor.append(0.5)
			else:
				if gate_type == "not":
					if bool(instantiation[0]) == (not bool(instantiation[1])):
						factor.append(1.0)
					else:
						factor.append(0.0)
				elif gate_type == "and":
					if bool(instantiation[0]) == (bool(instantiation[1]) and bool(instantiation[2])):
						factor.append(1.0)
					else:
						factor.append(0.0)
				elif gate_type == "or":
					if bool(instantiation[0]) == (bool(instantiation[1]) or bool(instantiation[2])):
						factor.append(1.0)
					else:
						factor.append(0.0)

			# next instantiation
			for d in range(width-1, -1, -1):
				if instantiation[d] == 1:
					instantiation[d] = 0
				else:
					instantiation[d] = 1
					break

		factors_lst.append(factor)

	# health
	curr = True
	for k in range(inputs+gates, inputs+gates+2*health):
		factor = []

		if curr:
			p = random.random()
			factor = [2, p, 1-p]
		else:
			p1 = random.random()
			p2 = random.random()
			factor = [4, p1, p2, 1-p1, 1-p2]
		
		factors_lst.append(factor)

		curr = not curr

	return factors_lst

if __name__ == '__main__':
	import sys
	import functools
	if len(sys.argv) < 6:
		print("usage: {} <filename> <inputs> <gates> <outputs> <health>".format(sys.argv[0]))
		exit(-1)
	filename = sys.argv[1]
	inputs = int(sys.argv[2])
	gates = int(sys.argv[3])
	outputs = int(sys.argv[4])
	health = int(sys.argv[5])
	
	with open(filename, mode='w', encoding='utf-8') as model:
		# DBAYES
		model.write(model_type() + '\n\n')

		# variables
		model.write("# Variables\n")
		model_vars = list(map(str, variables(inputs, gates, health)))
		model.write(model_vars[0] + '\n')
		model.write(' '.join(model_vars[1:]) + '\n\n')

		# prior
		model.write("# Prior\n")
		prior_vars = list(map(str, prior(inputs, gates, health)))
		model.write(prior_vars[0] + '\n')
		model.write(' '.join(prior_vars[1:]) + '\n\n')

		# 2TBN
		model.write("# 2TBN\n")
		transition_vars = list(map(str, transition(inputs, gates, health)))
		model.write(transition_vars[0] + '\n')
		model.write(' '.join(transition_vars[1:]) + '\n\n')

		# sensor
		model.write("# Sensor\n")
		sensor_vars = list(map(str, sensor(inputs, gates, outputs)))
		model.write(sensor_vars[0] + '\n')
		model.write(' '.join(sensor_vars[1:]) + '\n\n')

		# domains
		model.write("# Domains\n")
		domains = domain(inputs, gates, health)
		for domain in domains:
			domain_vars = list(map(str, domain))
			model.write(' '.join(domain_vars) + '\n')
		model.write('\n')

		# factors
		model.write("# Factors\n")
		factors_lst = factors(inputs, gates, health, domains)
		for factor in factors_lst:
			factor_values = list(map(str, factor))
			model.write(' '.join(factor_values) + '\n')
		model.write('\n')