#How to run: python get_bmc_info.py <
#!/usr/bin/python

import csv
import sys
import Queue as queue
import operator
import decimal
import time

time0 = time.time()
def get_data_list_of_dicts(filename):
  list = []
  with open(filename) as f:
    f_csv = csv.DictReader(f)
    for row in f_csv:
      list.append(row)
  return list

def get_room_sizes(list_of_dicts):
  room_sizes_dict = {}
  for dict in list_of_dicts:
    room = dict["Facil ID 1"]
    status = dict["Status"]
    course = dict["Course ID"]
    campus = dict["Catalog"][0]
    if status == "E" and campus == "B" and not room == "":
      if room in room_sizes_dict:
        if course in room_sizes_dict[room]:
          room_sizes_dict[room][course] = room_sizes_dict[room][course] + 1
        else:
          room_sizes_dict[room][course] = 1
      else:
        room_sizes_dict[room] = {}
        room_sizes_dict[room][course] = 1

  room_capacities = {}
  for room in room_sizes_dict:
    capacity = 0
    for course in room_sizes_dict[room]:
      if room_sizes_dict[room][course] > capacity:
        capacity = room_sizes_dict[room][course]
    room_capacities[room] = capacity
  return room_capacities

def get_student_prefs_enrolled(list_of_dicts):
  student_prefs = {}
  for dict in list_of_dicts:
    student = dict["Student ID"]
    course = dict["Course ID"]
    status = dict["Status"]
    room = dict["Facil ID 1"]
    if status == "E" and room != "":
      if student in student_prefs:
        student_prefs[student].append(course)
      else:
        student_prefs[student] = [course]
  return student_prefs

def get_student_prefs(list_of_dicts):
  student_prefs = {}
  for dict in list_of_dicts:
    student = dict["Student ID"]
    course = dict["Course ID"]
    status = dict["Facil ID 1"]
    room = dict["Facil ID 1"]
    if room != "":
      if student in student_prefs:
        student_prefs[student].append(course)
      else:
        student_prefs[student] = [course]
  return student_prefs

def get_courses(list_of_dicts):
  courses = {}
  for dict in list_of_dicts:
    course = dict["Course ID"]
    prof = dict["Instructor ID"]
    campus = dict["Catalog"][0]
    room = dict["Facil ID 1"]
    if not course in courses and campus == "B" and room !="" and prof != '#Value!':
      courses[course] = dict
  return courses

def get_building(list_of_dicts):
  building = {}
  for dict in list_of_dicts:
    subject = dict["Subject"]
    room = dict["Facil ID 1"]
    if room == None or room == "":
      continue
    if subject in building:
        building[subject].append(room)
    else:
        building[subject] = [room]
  return building

def get_rooms(list_of_dicts):
  rooms = []
  for dict in list_of_dicts:
    room = dict["Facil ID 1"]
    if room == None or room == "":
      continue
    else:
      rooms.append(room)
  return rooms

# Issue: didn't handle the case where a course number is corresponded to multiple courses.
def get_subject_level(list_of_dicts):
    subject_level = {}
    for dict in list_of_dicts:
        course = dict["Course ID"]
        department = dict["Subject"]
        campus = dict["Catalog"][0]
        level = dict["Catalog"][1]
        if not course in subject_level and campus == "B":
            subject_level[course] = (department,level)
    return subject_level

def get_prof_courses(list_of_dicts):
  profs = {}
  for dict in list_of_dicts:
    prof = dict["Instructor ID"]
    course = dict["Course ID"]
    campus = dict["Catalog"][0]
    if not prof == "" and campus == "B" and prof != "#Value!":
      if prof in profs:
        if not course in profs[prof]:
          profs[prof].append(course)
      else:
        profs[prof] = [course]
  return profs

def get_prof_of_course(list_of_dicts):
  courses_to_profs = {}
  for dict in list_of_dicts:
    prof = dict["Instructor ID"]
    course = dict["Course ID"]
    campus = dict["Catalog"][0]
    if not prof == "" and campus == "B" and prof != "#Value!":
      if course in courses_to_profs:
        if not prof in courses_to_profs[course]:
          courses_to_profs[course].append(prof)
      else:
        courses_to_profs[course] = [prof]
  return courses_to_profs

def get_class_times(list_of_dicts):
  times = []
  for dict in list_of_dicts:
    start = dict["Srt1 AM/PM"]
    end = dict["End 1 AMPM"]
    days = dict["Days 1"]
    class_time = (start, end, days)
    campus = dict["Catalog"][0]
    if not class_time in times and campus == "B" and not start == "" \
        and not end == "" and not days == "":
      times.append(class_time)
  return times

# One possibility for how to find out which labs go with which courses.
# Currently catches some "labs" that aren't actually labs for those courses.
# Course '333' seems especially to be a strange corner case.
# The issue may also be that this doesn't take sections into account in matching.
#def get_lab_courses(list_of_dicts):
#  lab_courses = {}
#  student_courses = get_student_prefs_enrolled(list_of_dicts)
#  courses = get_courses(list_of_dicts)
#  for dict in list_of_dicts:
#    course = dict["Course ID"]
#    dept = dict["Subject"]
#    level = dict["Level"]
#    student = dict["Student"]
#    units = dict["Unit Taken"]
#    campus = dict["College"]
#    if units == "0" and campus == "H":  # we think this is a lab class
#      all_courses = student_courses[student]
#      for enrolled_course in all_courses:
#        if not enrolled_course == course and enrolled_course in courses:
#          course_dict = courses[enrolled_course]
#          enrolled_dept = course_dict["Subject"]
#          enrolled_level = course_dict["Level"]
#          enrolled_units = course_dict["Unit Taken"]
#          enrolled_campus = course_dict["College"]
#          if enrolled_units > 0 and enrolled_dept == dept and enrolled_level == level \
#              and enrolled_campus == campus:
#            print enrolled_course + " " + course
#            if enrolled_course in lab_courses:
#              if not course in lab_courses[enrolled_course]:
#                lab_courses[enrolled_course].append(course)
#            else:
#              lab_courses[enrolled_course] = [course]
#  return lab_courses

def write_building_to_file(list_of_dicts, filename):
    building = get_building(list_of_dicts)
    f = open(filename, 'w')
    f.write("Building\t" + str(len(building)) + "\n")
    for subject in building:
        towrite = subject + "\t"
        for room in building[subject]:
            towrite = towrite + room + " "
        towrite = towrite + "\n"
        f.write(towrite)

def write_prefs_to_file(list_of_dicts, filename):
  student_prefs = get_student_prefs_enrolled(list_of_dicts)
  f = open(filename, 'w')
  f.write("Students\t" + str(len(student_prefs)) + "\n")
  for student in student_prefs:
    towrite = student + "\t"
    for course in student_prefs[student]:
      towrite = towrite + course + " "
    towrite = towrite + "\n"
    f.write(towrite)

def write_class_times_to_file(list_of_dicts, f):
  class_times = get_class_times(list_of_dicts)
  f.write("Class Times\t" + str(len(class_times)) + "\n")
  i = 1
  for (start, end, days) in class_times:
    f.write(str(i) + "\t" + start + " " + end + " " + days + "\n")
    i = i + 1

def write_rooms_to_file(list_of_dicts, f):
  room_capacities = get_room_sizes(list_of_dicts)
  f.write("Rooms\t" + str(len(room_capacities)) + "\n")
  for room in room_capacities:
    f.write(room + "\t" + str(room_capacities[room]) + "\n")

def write_num_classes_to_file(list_of_dicts, f):
  num_classes = len(get_courses(list_of_dicts))
  f.write("Classes\t" + str(num_classes) + "\n")

def write_teachers_to_file(list_of_dicts, f):
  prof_courses = get_prof_courses(list_of_dicts)
  num_profs = len(prof_courses)
  courses = get_courses(list_of_dicts)
  subject_level = get_subject_level(list_of_dicts)
  building = get_building(list_of_dicts)
  f.write("Teachers\t" + str(num_profs) + "\n")
  for course in courses:
    f.write(course + "\t")
    f.write(courses[course]["Instructor ID"] + "\t")
    f.write(subject_level[course][0] + "\t")
    for b in building[subject_level[course][0]]:
        f.write(b + "\t")
    f.write("\n")

def write_constraints_to_file(list_of_dicts, filename):
  f = open(filename, 'w')
  write_class_times_to_file(list_of_dicts, f)
  write_rooms_to_file(list_of_dicts, f)
  write_num_classes_to_file(list_of_dicts, f)
  write_teachers_to_file(list_of_dicts, f)
  f.close()

if len(sys.argv) != 4:
  print ("Usage: " + sys.argv[0] + " <enrollment.csv> <student_prefs.txt> <constraints.txt>")
  exit(1)
list_of_dicts = get_data_list_of_dicts(sys.argv[1])
# print(list_of_dicts[3])
# print("--------------------")
# write_prefs_to_file(list_of_dicts, sys.argv[2])
# print(list_of_dicts[3])
# print("--------------------")
# write_constraints_to_file(list_of_dicts, sys.argv[3])
# print(list_of_dicts[3])

# courses = get_courses(list_of_dicts)
# print(courses['002153'])

prefs = get_student_prefs_enrolled(list_of_dicts)
# print(prefs)
popularity = {}
for key in prefs:
  for course in prefs[key]:
    if not course in popularity:
      popularity[course] = 1
    else:
      popularity[course] += 1

sorted_d = sorted(popularity.items(), reverse=True, key=operator.itemgetter(1))

# print(sorted_d)
room_sizes = get_room_sizes(list_of_dicts)
# print(room_sizes)
timeslots = get_class_times(list_of_dicts)
# print(timeslots)
prof_courses = get_prof_courses(list_of_dicts)
# print(prof_courses)
courses_to_profs = get_prof_of_course(list_of_dicts)
# print(courses_to_profs)
rooms = get_rooms(list_of_dicts)
# print(rooms)
student_prefs = get_student_prefs(list_of_dicts)
# print(student_prefs)
room_capacities = get_room_sizes(list_of_dicts)
# print(room_capacities)

timetable = {}
temp = {}
a = 0
total_courses = len(popularity)
total_rooms = len(rooms)
course_to_timeslot = {}
course_to_room = {}
# print(courses_to_profs)

for dict in list_of_dicts:
  room = dict["Facil ID 1"]
  timetable[room] = {}

for dict in list_of_dicts:
  room = dict["Facil ID 1"]
  for timeslot in timeslots:
    timetable[room][timeslot] = {}

for dict in list_of_dicts:
  room = dict["Facil ID 1"]
  if not room == "":
    if a < total_courses:
      for timeslot in timeslots:
        if a < total_courses:
          # course = list(popularity.keys())[a]
          course = sorted_d[a][0]
          if course in courses_to_profs:
            teacher = courses_to_profs[course][0]
            if(not teacher in temp or temp[teacher] != timeslot):
              timeslot_to_courses = {timeslot : course}
              if course in course_to_timeslot:
                course_to_timeslot[course].append(timeslot)
              else:
                course_to_timeslot[course] = [timeslot]

              if course in course_to_room:
                course_to_room[course].append(room)
              else:
                course_to_room[course] = [room]

              timetable[room][timeslot] = course
              # if room in timetable and timeslot in timetable[room]:
              #   # print(1)
              #   timetable[room][timeslot].append(course)
              # elif room in timetable:
              #   # print(2)
              #   # print(room)
              #   timetable[room].append(timeslot_to_courses)
              # else:
              #   # print(3)
              #   timetable[room] = [timeslot_to_courses]

              if not teacher in temp:
                temp[teacher]=timeslot
              a = a + 1
        else:
          break
    else:
      break


remaining = {}
capacity = {}
schedule = {}
max_satisfaction = len(list_of_dicts)
achieved_satisfaction = 0


# fill in "remaining"
for dict in list_of_dicts:
  student = dict["Student ID"]
  if student in student_prefs:
    if student in remaining:
      continue
    else:
      remaining[student] = [len(student_prefs[student])]

for room in timetable:
  capacity[room] = {}

for room in timetable:
  for timeslot in timetable[room]:
    capacity[room][timeslot] = {}

#fill in "capacity"
for room in timetable:
  for timeslot in timetable[room]:
    if room != '':
      capacity[room][timeslot] = room_capacities[room]

# print(capacity)

for dict in list_of_dicts:
  student = dict["Student ID"]
  if student in student_prefs:
    timeslots = {}
    for course in student_prefs[student]:
      # print(1)
      # print course
      # print course_to_room[16]
      if course in course_to_room and course in course_to_timeslot:
        # print("course " + str(course))
        room_used = course_to_room[course][0]
        # print("room " + str(room_used))
        timeslot_used = course_to_timeslot[course][0]
        # print("timeslot " + str(timeslot_used))
        if not student in schedule:
          if capacity[room_used][timeslot_used] > 0:
            schedule[student] = [course]
            achieved_satisfaction = achieved_satisfaction + 1
            # if student in remaining:
            #   remaining[student][0] = remaining[student][0] - 1
            if room_used in capacity:
              if timeslot_used in capacity[room_used]:
                capacity[room_used][timeslot_used] = capacity[room_used][timeslot_used] - 1
                # print(capacity[room_used][timeslot_used])

        else:
          valid = False
          for student_course in student_prefs[student]:
            if student_course in course_to_room and student_course in course_to_timeslot:
              if student_course == course:
                break
              if not course in schedule[student] and course_to_timeslot[course][0] != course_to_timeslot[student_course][
                0] and capacity[room_used][timeslot_used] > 0:
                valid = True

              else:
                valid = False
                break
          if valid:
            schedule[student].append(course)
            achieved_satisfaction = achieved_satisfaction + 1
            # if student in remaining:
            #   remaining[student][0] = remaining[student][0] - 1
            if room_used in capacity:
              if timeslot_used in capacity[room_used]:
                capacity[room_used][timeslot_used] = capacity[room_used][timeslot_used] - 1
                # print(capacity[room_used][timeslot_used])

f = open("Spring2015_schedule.txt", 'w')
f.write("Course\t" + "Room\t" + "Teacher\t" + "Time\t" + "Students" + "\n")
for course in course_to_room:
  towrite = str(course) + "\t" + str(course_to_room[course][0]) + "\t" + str(courses_to_profs[course]) + "\t" + str(course_to_timeslot[course][0]) + "\t"
  for student in schedule:
      # print schedule[student]
      if course in schedule[student]:
        towrite = towrite + str(student) + " "
  towrite = towrite + "\n"
  f.write(towrite)

time1 = time.time()
print "Runtime: " + str(time1 - time0) +" sec"
satisfaction = decimal.Decimal(achieved_satisfaction) / decimal.Decimal(max_satisfaction)
print "Student satisfaction: " + str(round(satisfaction,5))