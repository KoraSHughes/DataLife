from heapq import heappop, heappush, heappushpop
import bisect

class Student:
	def __init__(self, identifier, ranking):
		self.identifier = identifier
		self.ranking = ranking
		self.last_proposal = -1
		self.matched = False

	def propose(self):
		# Here, last_proposal identifies the current temporary allocation: if a student proposes, it is safe to
		# assume they will be accepted by the last school they proposed to until they are explicitly rejected.
		# If last_proposal is equal to the length of the ranking, then the student is unmatched.
		# The matched flag is still needed in order to avoid unnecessary proposals by students who are already matched.

		self.last_proposal += 1
		self.matched = True
		return self.ranking[self.last_proposal]

	def handle_rejection(self):
		self.matched = False

	def can_propose(self):
		"""
		Returns `True` if and only if the student can propose to a new school, namely if the student does not have a
		temporary allocation and still has some schools they haven't proposed to in their ranking.
		"""
		return (not self.matched and self.last_proposal < len(self.ranking)-1)

	def get_result(self):
		"""
		Returns the identifier of the school the student was matched with, or `None` if the student was unmatched.
		"""
		return None if not self.matched else self.ranking[self.last_proposal]

class School:
	def __init__(self, identifier, ranking, priority_students, priority_seats, total_seats):
		self.identifier = identifier

		self.ranking_list = ranking
		self.ranking = {rank: id for id, rank in enumerate(ranking)}
		self.priority_dict = {id: id in priority_students for id in ranking}

		self.priority_list = []
		self.non_priority_list = []
		self.priority_seats = priority_seats
		self.total_seats = total_seats

	def check_proposal(self, student_id) -> bool:
		"""
		Returns `True` if a proposal received by the specified student will be accepted, `False` otherwise.
		"""

		# If the school has residual capacity, the proposal will be accepted regardless of rank.
		if len(self.priority_list) + len(self.non_priority_list) < self.total_seats:
			return True

		rank = self.ranking.get(student_id)
		has_priority = self.priority_dict.get(student_id)

		# If the proposing student has priority and the priority list has residual capacity, the proposal will be accepted.
		if has_priority and len(self.priority_list) < self.priority_seats:
			return True

		# If the school has provisionally accepted at least one competing student that ranks worse than the proposing
		# student, then the proposal will be accepted, otherwise it will be rejected.
		# Competing students are restricted to students in the non-priority list for non-priority proponents.
		outranks_priority = rank < -self.priority_list[0][0]
		outranks_non_priority = len(self.non_priority_list) > 0 and rank < -self.non_priority_list[0][0]
		return (has_priority and outranks_priority) or outranks_non_priority

	def handle_proposal(self, student_id) -> Student | None:
		"""
		Handles the proposal received by the specified student and returns the identifier of the student that is rejected
		as a result, if applicable. If no student is rejected as a consequence of this proposal, returns `None`.

		Parameters:
		- student_id: the identifier of the proposing student.

		Returns: the identifier of the rejected student, or `None` if no student was rejected.
		"""

		rank = self.ranking.get(student_id)
		item = (-rank, student_id)  # student_rank is negated since heapq implements a min heap
		has_priority = self.priority_dict.get(student_id)

		# If the school has residual capacity, accept the proposing student and reject no one. Non-priority students will
		# be placed in the non-priority list, while priority students can be placed anywhere, depending on availability.
		if len(self.priority_list) + len(self.non_priority_list) < self.total_seats:
			if not has_priority:
				heappush(self.non_priority_list, item)
				return None

			# Note that a priority student can be only placed in the priority list in two cases:
			# 1. if there are any remaining priority seats, or
			if len(self.priority_list) < self.priority_seats:
				heappush(self.priority_list, item)
				return None

			# 2. if they outrank at least one student currently in the priority list, who will be bumped to non-priority.
			bumped = heappushpop(self.priority_list, item)
			heappush(self.non_priority_list, bumped)
			return None

		# If all seats have been filled but the proposing student has priority and there are any remaining priority seats,
		# accept the proposing student and reject the lowest-ranking non-priority student.
		if has_priority and len(self.priority_list) < self.priority_seats:
			heappush(self.priority_list, item)
			reject = heappop(self.non_priority_list)[1]
			return reject[1]

		# If all seats have been filled and there are no remaining priority seats, accept the proposing student on a
		# provisional basis, then reject the lowest-ranking among the qualifying competing students.
		if has_priority:

			# If the proposing student has priority, every student qualifies as competition; if the initially rejected student
			# was in the priority list, then the proponent will take their place in the priority list, and the initially
			# rejected student will be compared to students in the non-priority list to determine the actual rejected student.
			reject_priority = heappushpop(self.priority_list, item)
			reject_overall = heappushpop(self.non_priority_list, reject_priority)
			return reject_overall[1]

		# If the proposing student does not have priority, only students in the non-priority list qualify as competition,
		# even if they have priority (this means all priority seats have been filled by better ranked priority students).
		reject = heappushpop(self.non_priority_list, item)
		return reject[1]

	def get_result(self):
		"""
		Returns the identifiers of the students matched with the school, along with the number of available spots, divided
		into priority and non-priority.
		"""
		return self.priority_list, self.non_priority_list, self.priority_seats, self.total_seats

class Matching:
	def __init__(self, students, schools):
		self.students = {student['identifier']: Student(**student) for student in students}
		self.schools = {school['identifier']: School(**school) for school in schools}

	def run_new(self):
		students_to_match = list(self.students.copy().items())

		while students_to_match:
			identifier, student = students_to_match.pop(0)

			accepted = False
			while (not accepted and student.can_propose()):
				if student.can_propose():
					tgt = student.propose()
					tgt_school = self.schools.get(tgt)
					accepted = tgt_school.check_proposal(identifier)

			if accepted:
				reject = tgt_school.handle_proposal(identifier)
				if reject:
					students_to_match.append((reject, self.students.get(reject)))

		self.get_results()

	def run(self, verbose=True):
		complete = False
		rounds = 0

		while not complete:
			complete = True

			for student in self.students.values():

				if student.can_propose():
					target = student.propose()
					tgt_school = self.schools.get(target)
					rejected = tgt_school.handle_proposal(student.identifier)

					if rejected is not None:
						complete = False
						rejected_student = self.students.get(rejected)
						rejected_student.handle_rejection()

			rounds += 1
			if verbose:
				print(f'\nResults after round {rounds}:')
				self.get_results()

	def get_results(self):
		print()
		print('*** Students ***')
		for id, student in self.students.items():
			res = student.get_result()
			if res is None:
				print(f'Student {id} was unmatched.')
			else:
				print(f'Student {id} was matched with school {res}.')

		print()
		print('*** Schools ***')
		for id, school in self.schools.items():
			priority, non_priority, pr_seats, seats = school.get_result()
			print()
			print(f'School {id} filled {len(priority)} out of {pr_seats} available seats, '
						f'and {len(priority) + len(non_priority)} out of {seats} available seats.')
			print(f'It accepted the following students as priority: {[s[1] for s in priority]}.')
			print(f'It accepted the following students as non-priority: {[s[1] for s in non_priority]}.')

if __name__ == '__main__':
	students = [
		{'identifier': 'A', 'ranking': ['R', 'B', 'Y']},
		{'identifier': 'B', 'ranking': ['R', 'B', 'Y']},
		{'identifier': 'C', 'ranking': ['B', 'R', 'Y']},
		{'identifier': 'D', 'ranking': ['B', 'R', 'Y']},
		{'identifier': 'E', 'ranking': ['R', 'Y', 'B']},
		{'identifier': 'F', 'ranking': ['B', 'Y', 'R']}
	]

	schools = [
		{
			'identifier': 'R',
			'ranking': ['F', 'C', 'E', 'A', 'D', 'B'],
			'priority_students': ['A', 'B', 'D', 'E'],
			'priority_seats': 2,
			'total_seats': 2
		},
		{
			'identifier': 'B',
			'ranking': ['A', 'B', 'C', 'D', 'E', 'F'],
			'priority_students': ['B', 'C', 'D', 'F'],
			'priority_seats': 2,
			'total_seats': 2
		},
		{
			'identifier': 'Y',
			'ranking': ['F', 'E', 'A', 'B', 'C', 'D'],
			'priority_students': ['F', 'D'],
			'priority_seats': 2,
			'total_seats': 2
		}
	]

	match = Matching(students, schools)
	match.run()
	# TODO match.run_new() needs fixing but run() is more than fine for now, there's only a slight difference