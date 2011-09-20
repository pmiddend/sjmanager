#!/usr/bin/env python3

import sjmanager.util
import timeit

for program in ["python", "bash", "ls", "jabberwocky"]:
	print(
			'Testing whether "{}" can be found in path: {}'.format(
				program,
				sjmanager.util.program_in_path(program) or "No"
				))

print(
"timing 10000 iterations of this test: ")
print(
	timeit.timeit(
	"""
	import sjmanager.util
	for program in ["python", "bash", "ls", "jabberwocky"]:
					sjmanager.util.program_in_path(program)
	""", number=10000)
)
