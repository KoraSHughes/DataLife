from heapq import heappop, heappush, heappushpop
import numpy as np
import time

def average_lottery_number(numbers: list[str]) -> str:
	numbers_int = [int('0x' + n[:8], 0) for n in numbers]
	avg = sum(numbers_int) // len(numbers_int)
	return f'{avg:#010x}'[2:]

class Student:
	def __init__(self, identifier, ranking, lottery_number):
		self.identifier = identifier
		self.ranking = ranking
		self.lottery_number = lottery_number
		self.last_proposal = -1
		self.matched = False

	def propose(self):
		# Here, last_proposal identifies the current temporary allocation: if a student proposes, it is safe to
		# assume they will be accepted by the last school they proposed to until they are explicitly rejected.
		# If last_proposal is equal to the length of the ranking, then the student is unmatched.
		# The matched flag is still needed in order to avoid unnecessary proposals by students who are already matched.

		self.last_proposal += 1
		return self.ranking[self.last_proposal]

	def update_match(self, matched: bool):
		self.matched = matched

	def can_propose(self):
		"""
		Returns `True` if and only if the student can propose to a new school, namely if the student does not have a
		temporary allocation and still has some schools they haven't proposed to in their ranking.
		"""
		return not self.matched and self.last_proposal < len(self.ranking)-1

	def get_result(self):
		"""
		Returns the identifier of the school the student was matched with and the position of the school in the
		preference list (0-based), or `(None, None)` if the student was unmatched.
		"""
		if not self.matched:
			return None, None
		else:
			return self.ranking[self.last_proposal], self.last_proposal

class School:
	def __init__(self, identifier, ranking, total_seats):
		self.identifier = identifier

		self.ranking_list = ranking
		self.ranking = {student_id: rank for rank, student_id in enumerate(ranking)}

		self.non_priority_list = []
		self.total_seats = total_seats
		self.applications_received = 0

	def check_proposal(self, student_id) -> bool:
		"""
		Returns `True` if a proposal received by the specified student will be accepted, `False` otherwise.

		Parameters:
		- student_id: the identifier of the proposing student.
		"""

		self.applications_received += 1

		# If the school has residual capacity, the proposal will be accepted regardless of rank.
		if len(self.non_priority_list) < self.total_seats:
			return True

		# If the school has provisionally accepted at least one student that ranks worse than the proposing student, then
		# the proposal will be accepted, otherwise it will be rejected.
		rank = self.ranking.get(student_id)
		return rank < -self.non_priority_list[0][0]

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

		# If the school has residual capacity, accept the proposing student and reject no one.
		if len(self.non_priority_list) < self.total_seats:
			heappush(self.non_priority_list, item)
			return None

		# If all seats have been filled, accept the proposing student on a provisional basis, then reject the lowest-ranking
		# among the provisionally accepted students.
		reject = heappushpop(self.non_priority_list, item)
		return reject[1]

	def prefers_to_matches(self, student_id):
		rank = self.ranking.get(student_id)
		worst_match_rank = self.non_priority_list[0][0]
		return rank < -worst_match_rank

	def get_result(self) -> tuple[list, list, int, int, int]:
		"""
		Returns the identifiers of the students matched with the school, along with the number of available spots.
		"""
		return [], self.non_priority_list, 0, self.total_seats, self.applications_received

class PrioritySchool(School):
	def __init__(self, identifier, ranking, priority_students, priority_seats, total_seats):
		super().__init__(identifier, ranking, total_seats)

		self.priority_dict = {student_id: student_id in priority_students for student_id in ranking}
		self.priority_list = []
		self.priority_seats = priority_seats

	def check_proposal(self, student_id) -> bool:
		"""
		Returns `True` if a proposal received by the specified student will be accepted, `False` otherwise.

		Parameters:
		- student_id: the identifier of the proposing student.
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

	def get_result(self) -> tuple[list, list, int, int, int]:
		"""
		Returns the identifiers of the students matched with the school, along with the number of available spots, divided
		into priority and non-priority.
		"""
		return self.priority_list, self.non_priority_list, self.priority_seats, self.total_seats, self.applications_received

class Matching:
	def __init__(self, students, lottery_nums, schools, capacities):
		self.students = {
			student_id: Student(student_id, ranking, lottery_nums[student_id]) for student_id, ranking in students.items()
		}
		self.schools = {
			school_id: School(school_id, ranking, capacities[school_id]) for school_id, ranking in schools.items()
		}

	def run(self):
		students_to_match = list(self.students.copy().items())

		while students_to_match:
			identifier, student = students_to_match.pop(0)

			matched = False
			while not matched and student.can_propose():
				tgt = student.propose()
				tgt_school = self.schools.get(tgt)
				matched = tgt_school.check_proposal(identifier)

			if matched:
				student.update_match(True)
				reject = tgt_school.handle_proposal(identifier)
				if reject:
					reject_obj = self.students.get(reject)
					reject_obj.update_match(False)
					students_to_match.append((reject, reject_obj))

	def check_stability(self):
		print()
		print('*** Stability check ***')

		# First: verify that the outcome is stable, i.e. there are no (student, school) pairs that would rather be
		# matched together than with their current matches
		unstable_pairs = []
		for student_id, student in self.students.items():
			matched_school, rank = student.get_result()
			# If rank == 0 then the student is matched with their preferred school, thus the pair is stable
			if rank is None or rank > 0:
				preferred_schools = student.ranking if rank is None else student.ranking[:rank]
				i = 0
				found_unstable = False
				while not found_unstable and i < len(preferred_schools):
					school_id = preferred_schools[i]
					school = self.schools[school_id]
					i += 1
					if school.prefers_to_matches(student.lottery_number):
						found_unstable = True
						unstable_pairs.append((student_id, matched_school))

		num_unstable = len(unstable_pairs)
		print()
		print(f'The outcome is {"stable" if num_unstable == 0 else "unstable"} ({num_unstable} unstable pairs).')

	def get_results(self, stage, save_to_disk=True):
		print()
		print('*** Students ***')
		bins = {i: [] for i in range(13)}
		matches = {}

		for id, student in self.students.items():
			school, rank = student.get_result()
			matches[id] = (school, rank+1 if rank is not None else None)
			if rank is None:
				bins[12].append(student.lottery_number)
			else:
				bins[rank].append(student.lottery_number)

		counts, averages, ranges = [0] * 13, [0] * 13, [(0, 0)] * 13
		for i, lottery_nums in bins.items():
			count = len(lottery_nums)
			average = average_lottery_number(lottery_nums)
			best, worst = min(lottery_nums), max(lottery_nums)
			counts[i] = count
			averages[i] = average
			ranges[i] = (best, worst)

			if i == len(bins)-1:
				print(f'Unmatched: {count}.')
			else:
				print(f'Matched to choice #{i+1}: {count}.')
			print(f'\tAverage lottery number: {average}-xxxx-xxxx-xxxx-xxxxxxxxxxxx')
			print(f'\tBest lottery number: {best}')
			print(f'\tWorst lottery number: {worst}')

		if save_to_disk:
			path = 'BackEnd/Data/Simulation/'
			np.save(path + f'bin_counts_stage{stage}.npy', counts)
			np.save(path + f'bin_averages_stage{stage}.npy', averages)
			np.save(path + f'bin_ranges_stage{stage}.npy', ranges)
			np.save(path + f'matches_stage{stage}.npy', matches)

		return counts, averages, ranges, matches

def run_simulation(students, lottery, schools, capacities, stage):
	match = Matching(students, lottery, schools, capacities)
	match.run()
	return match.get_results(stage, save_to_disk=False)

if __name__ == '__main__':
	stage = 1

	path = 'BackEnd/Data/Generated/'
	start = time.time()
	students = np.load(path + f'student_rankings_stage{stage}.npy', allow_pickle=True).item()
	lottery = np.load(path + 'student_lottery_nums.npy', allow_pickle=True).item()
	schools = np.load(path + 'school_rankings_open.npy', allow_pickle=True).item()
	capacities = np.load(path + 'school_capacities.npy', allow_pickle=True).item()

	match = Matching(students, lottery, schools, capacities)
	load_time = time.time() - start
	print(f'Loading done in {load_time:.2f} seconds.')

	start = time.time()
	match.run()
	match_time = time.time() - start
	print()
	print(f'Matching done in {match_time:.2f} seconds.')

	match.get_results(stage)
	match.check_stability()