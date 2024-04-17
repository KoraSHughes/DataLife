import pandas as pd
import numpy as np
import os
import random

import uuid
from difflib import SequenceMatcher
from tqdm import tqdm


cwd = os.getcwd()
# School/Student Information
MAX_NUM_SCHOOLS = 12
LARGE_NUM = 9999999999  # used to set upperbound for sampling range

# stats on nyc schools
mean_school_cap = 145  # capacity
std_school_cap = 128.5
mean_ens = 2.453505  # ens = expected number of students applied per seat
std_ens = 4.072874

# distributions according to: https://www.schools.nyc.gov/enrollment/enroll-grade-by-grade/high-school
screen_dist = [94, 89.66, 82.75, 76.33]  # https://www.schools.nyc.gov/enrollment/enroll-grade-by-grade/high-school/screened-admissions
edopt_dist = [88.25, 77.5]  #https://www.schools.nyc.gov/enrollment/enroll-grade-by-grade/high-school/educational-option-ed-opt-admissions-method


# MAIN CLASSES
class Student:
    def __init__(self, seed, lottery="", schools=[], score=-1):
        # necessary info
        self.id = seed
        random.seed(seed) # set the seed
        
        if lottery != "": # signifies that this is a real student whose data we are inputting
            self.name = seed
            self.lottery = lottery
            self.schools = schools  # Note: can ignore given current simulation code
            self.num_schools = len(schools)
            
            self.selection_policy = -1
            self.ranking_policy = -1
        else:
            self.lottery = uuid.UUID(int=random.getrandbits(128), version=4).hex  # note: can do duplicate check if necessary

            seed_nums = random.sample(range(1, 3), 2)  # necessary to get 2 independent numbers
            # integer representation of how likely a student is to select a given school
            self.selection_policy = seed_nums[0]
            # integer representation of how highly a student is to rank a school, given they've already selected it
            self.ranking_policy = seed_nums[1]

            self.num_schools = MAX_NUM_SCHOOLS
            self.schools = []  # to be updated later based on self.selection_policy
            self.name = ""
        
        # calculate buckets for score-based decisions
        self.test_score = score if score != -1 else self.get_rand_score(seed)
        self.seat = seated(self.test_score)
        self.screen = screened(self.test_score)
        
        # extra / potential additions
        self.district = 0
        self.borough = None
        self.location = None
        
    def get_rand_score(self, new_seed):
        """ generates a random gpa based on assumed normal distribution of nyc highschool data """
        random.seed(new_seed)
        num = round(np.random.normal(68, 8.89, 1)[0], 2)
        if num < 0:
            num = 0
        elif num > 100:
            num = 100
        return num
    
    def update_choice(self, schools):
        """ used to update a student object with custom school information """
        self.schools = schools
        self.num_schools = len(schools)
        
    def info(self, simple=False):
        """ shows basic information generated from seed/id """
        basics = "ID: " + self.id + "\nLottery: " + self.lottery
        scores = "\nScores: " + str([self.test_score, self.seat, self.screen])
        policies = "\nPolicies: " + str([self.selection_policy, self.ranking_policy])
        if simple:
            return basics
        else:
            return basics + scores + policies
        
    def to_list(self):
        """ export all data for dataframe conversion """
        return [self.id, self.lottery, self.selection_policy, self.ranking_policy, self.num_schools, 
                self.test_score, self.seat, self.screen,
                self.name, self.district, self.borough, self.location]
        
    def __str__(self):
        """ return unique hashable identifier """
        return self.id
#     sorted(students, key=lambda x: int(x.lottery, 16))
        
        
class School:
    def __init__(self, seed, cap=-1, pop=-1, like=-1, name=""):
        # necessary info
        self.dbn = seed  # ID
        random.seed(seed) # set the seed
        
        self.policy = random.randint(1,3)
        self.capacity = self.get_rand_cap(seed) if cap<0 else cap
        
        # NOTE: popularity is how likely a school is to be on a student's list
        if pop == -1:  # weighted by mean & std of popularity / mean capacity
            np.random.seed(seed_stoi(seed))
            new_pop = np.random.normal(mean_ens, std_ens, 1)[0]
            if new_pop < 0:
                new_pop = 0
            self.popularity = round(self.capacity * new_pop, 2)
        else:
            self.popularity = pop
        # NOTE: likeability is how high on a students list a given school should appear
        self.likeability = random.randint(1,MAX_NUM_SCHOOLS) if like == -1 else like    
        
        # extra info
        self.name = name
        self.district = 0
        self.borough = None
        self.location = None
        
    def get_rand_cap(self, new_seed):
        """ generate a random school capacity based on normal distribution of nyc highschool data """
        np.random.seed(seed_stoi(new_seed))
        num = round(np.random.normal(mean_school_cap, std_school_cap, 1)[0])  
        if num < 1:
            num = 1
        return num    
        
    def info(self, simple=False):
        """ display basic info """
        basics = "ID: " + self.dbn
        if self.name != "":
            basics += ", Name: " + self.name
        basics += "\nPolicy: " + str(self.policy)
        additional = "\nCap/Pop/Like: " + str([self.capacity, self.popularity, self.likeability])
        return basics + additional if not simple else ""
    
    def to_list(self):
        """ export all information"""
        return [self.dbn, self.capacity, self.policy, self.popularity, self.likeability,
                self.name, self.district, self.borough, self.location]
        
    def __str__(self):
        """ return unique hashable id """
        return self.dbn
    

stoi_limit = 2**32 - 1
def seed_stoi(s):
    """ somewhat janky conversion of string to int for numpy random states 
    (since np.random.seed() cant take a string) """
    res = 1
    for c in s:
        res += abs(ord(c))
        if res > stoi_limit:
            res -= 2*abs(ord(c))
    return res


def match_schools(all_schools, lst):
    """ matches schools based on edit distance """
    result = []
    for name in lst:
        dists = [(str(schol), SequenceMatcher(None, name, schol.name).ratio()) for schol in all_schools.values()]
        result.append(max(dists, key=lambda x: x[1])[0])  # add the school with the min edit distance
    return result


def add_fake_gpa(students):
    """ adds a gpa attribute based on the students ELA and Math scores """
    students["fake_gpa"] = students["Math_score"] + students["ELA_score"]
    max_score = max(students["fake_gpa"])
    students["fake_gpa"] = students["fake_gpa"].apply(lambda score: round(4*score/max_score, 2))  # gpa-normalized
    return students

def get_distributions():
    """ returns quantile distribution of gpa based on real data 
    used for seat/screen calculations """
    student_df = pd.read_csv(cwd+"/Data/student_info_with_demographics.csv")
    student_df = add_fake_gpa(student_df)
    
    edopt_dist = [student_df["fake_gpa"].quantile(i/3) for i in range(2, 0, -1)]
    screen_dist = [student_df["fake_gpa"].quantile(i/5) for i in range(4, 0, -1)]
    return edopt_dist, screen_dist
# edopt_dist, screen_dist = get_distributions()
def set_place(x, dist):
    """ returns a number representing which placement of a number x based on a distribution dist """
    for i, num in enumerate(dist):
        if x >= num:
            return i+1
    return len(dist)+1

# USED FOR SEAT/SCREEN CALCULATIONS
seated = lambda x: set_place(x, edopt_dist) 
screened = lambda x: set_place(x, screen_dist)

# GENERATION FUNCTIONS
def generate_students(seed, size=71250):
    """ generate students based on seeded random sampling """
    random.seed(seed)
    return [Student("Student #"+str(i)) for i in random.sample(range(LARGE_NUM*size), size)]

def generate_schools(seed, size=437):
    """ generate schools based on seeded random sampling """
    random.seed(seed)
    return [School("School #"+str(i)) for i in random.sample(range(LARGE_NUM*size), size)]

def generate_nyc_schools(seed, school_info_dir="Data/schools_info.npy"):
    """ generate schools based on nyc school applicant data """
    school_info = np.load(school_info_dir, allow_pickle=True).item()
    # {name: (dbn, capacity, true applicants, total applicants)}
    new_schools = []
    for name, info in school_info.items():  # NOTE: can add seeded variance in popularity & likeability
        tmp_like = 0 if info[3]==0 else round(info[2]/info[3], 3)  # applicant rate (proxy for true_ar)
        # NOTE: popularity can also be total_applicants/capacity but we want capacity-weighted for this implementaiton
        schol = School(info[0], info[1], info[3], tmp_like, name)
        new_schools.append(schol)
    random.seed(seed)
    random.shuffle(new_schools)  # shuffle because order can affect tiebreakers
    return new_schools


# SIMULATIONS
def simulate_student_choices(students, schools):
    """ takes in a dict of students and schools and generates choices based on student.selection_policy
     ordered by student.ranking_policy 
     Note: also outputs a school_to_student helper dict such that {school.dbn: set(school_id)}
     """
    choices = dict([[str(stud), []] for stud in students])
    
    # generate lists of schools for each strategy & shuffle
    full_random = list(schools.keys())
    popularity_weights = [schools[schol].popularity for schol in full_random]
    
    school_to_student = dict([[str(schol), set()] for schol in schools])  # helper for school choices
    for stud in tqdm(students.values()):
        # for each student, choose schools depending on strategy based on seed
        ranks = []
        random.seed(str(stud))
        if stud.selection_policy == 1:  # fully randomized
            ranks = random.choices(population=full_random, k=stud.num_schools)
        else:  # popularity weighted randomized
            ranks = random.choices(population=full_random, weights=popularity_weights, k=stud.num_schools)
        
        # order based on student policy
        if stud.ranking_policy != 1:  # rank by likeability
            ranks.sort(key=lambda schol: schools[schol].likeability, reverse=True)
            # NOTE: ties are handled by how the list was previously sorted which is depended on the seed
        choices[str(stud)] = ranks
        
        for schol_id in ranks:  # add ranks to helper
            school_to_student[schol_id].add(str(stud))
    return choices, school_to_student

def simulate_school_choices(school_to_student, students, schools):
    """ takes in a dict of students and schools as well as the student's rankings and generatings 
        the school's choices based on them
    """
    choices = {}
    # sort students by school policy
    for schol_id, student_ids in tqdm(school_to_student.items()):
        ranks = []
        if schools[schol_id].policy == 1:
            ranks = sorted(student_ids, key=lambda stud_id: students[stud_id].lottery)
        elif schools[schol_id].policy == 2:
            ranks = sorted(student_ids, key=lambda stud_id: (students[stud_id].seat, students[stud_id].lottery))
        else:
            ranks = sorted(student_ids, key=lambda stud_id: (students[stud_id].screen, students[stud_id].lottery))
        choices[schol_id] = ranks
    return choices


def oneshot(seed, nyc=True, num_schools=437, num_students=71250, verbose=False):
    """ runs a basic simulation that generates schools and students and simulates their preferences:
        - student_preference_profile = {student_id : [school_ids_ranked]}
        - school_preference_profile = {school ids : [student_ids_ranked]} 
        - students = {student_id : [self.id, self.lottery, self.selection_policy, self.ranking_policy,
                                    self.num_schools,  self.test_score, self.seat, self.screen, 
                                    self.name, self.district, self.borough, self.location] }
        - schools = {school_dbn : [self.dbn, self.policy, self.popularity, self.likeability,
                                    self.name, self.district, self.borough, self.location] }
                                
        seed determines the simulation state,
        nyc determines if you want to use real nyc school data from 2023 (overrides num_schools on True)
        num_students & num_schools are self-explanatory
    """
    random.seed(seed)
    student_seed, school_seed = random.sample(range(LARGE_NUM), 2)
    if verbose: print("Base Seed", seed, "created student seed", student_seed, "and school seed", school_seed)
    
    # generate students and schools
    students = dict([[str(stud), stud] for stud in generate_students(student_seed, num_students)])
    if nyc:
        schools = dict([[str(schol), schol] for schol in generate_nyc_schools(school_seed)])
    else:
        schools = dict([[str(schol), schol] for schol in generate_schools(school_seed, num_schools)])
    if verbose: 
        total_seats = sum([schol.capacity for schol in schools.values()])
        print("Generated", len(schools), "schools and", len(students), "students with", total_seats, "seats\n")
    
    if verbose: print("Student choices simulating...")
    student_preference_profile, school_to_student = simulate_student_choices(students, schools)
    
    if verbose: print("School choices simulating...")
    # Note: no random seed since lottery# informs the tiebreaks
    school_preference_profile = simulate_school_choices(school_to_student, students, schools)
    
    return student_preference_profile, school_preference_profile, students, schools


def oneshot_with_input(seed, lottery_num, my_schools, gpa=-1, student_name="injected_student", verbose=False):
    """ runs a simulation based on NYC data with a single student as input
    Note: for student, lottery# & schools required, percentile scale gpa recommended, name possible
    """
    assert len(my_schools) <= MAX_NUM_SCHOOLS, "you can only rank "+str(MAX_NUM_SCHOOLS)+" schools"
    
    # tldr to a normal oneshot() simulation, then add in the student before the school preferences are simulated
    random.seed(seed)
    student_seed, school_seed = random.sample(range(LARGE_NUM), 2)
    if verbose: print("Base Seed", seed, "created student seed", student_seed, "and school seed", school_seed)
    
    students = dict([[str(stud), stud] for stud in generate_students(student_seed)])
    schools = dict([[str(schol), schol] for schol in generate_nyc_schools(school_seed)])
    if verbose: 
        total_seats = sum([schol.capacity for schol in schools.values()])
        print("Generated", len(schools), "schools and", len(students), "students with", total_seats, "seats\n")
    
    if verbose: print("Student choices simulating...")
    student_preference_profile, school_to_student = simulate_student_choices(students, schools)
    
    # inject student into data
    if verbose: print("Injecting new student into data...")
    choices = match_schools(schools, my_schools)  # match choices with schools in present data set
    new_student = Student(student_name, lottery_num, choices, gpa)  # make student obj
    students[str(new_student)] = new_student  # add student to data
    student_preference_profile[str(new_student)] = choices  # add student's list to preference profile
    for schol in choices:  # add student's choices to school dict
        school_to_student[schol].add(str(new_student))  # Note: make sure there is no student with an identical id
    
    if verbose: print("School choices simulating...")
    school_preference_profile = simulate_school_choices(school_to_student, students, schools)
    
    return student_preference_profile, school_preference_profile, students, schools


if __name__ == '__main__':
    simstate = 1
    student_prefs, school_prefs, students, schools = oneshot(simstate, True)
    print("STUDENT PREFERENCES:")
    print(student_prefs)
    print("\nSCHOOL PREFERENCES:")
    print(school_prefs)