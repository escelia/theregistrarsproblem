#How to run: python get_mock_data.py <student_prefs file> <constraint file>
#!/usr/bin/python
import sys
import operator
import time
import decimal
time0 = time.time()
timeslots = []
courses_to_profs = {}
student_prefs = {}

#read data from preference file
with open(sys.argv[1], 'r') as prefs_file:
    # student_prefs = {}
    student_nums = int(prefs_file.next().split()[1])
    for student in range(1, student_nums+1):
        splitted = prefs_file.next().split()
        student_prefs[student] = [splitted[1]]
        for course in range(2, 5):
            student_prefs[student].append(splitted[course])

#read data from constraint file
with open(sys.argv[2], 'r') as constraints_file:
    timeslot_nums = int(constraints_file.next().split()[2])
    # timeslots = []
    for timeslot in range(1, timeslot_nums+1):
        timeslots.append(timeslot)
    room_nums = int(constraints_file.next().split()[1])
    room_capacities = {}
    capacities = 0
    for room in range(1, room_nums+1):
        room_capacities[room] = int(constraints_file.next().split()[1])
        capacities = capacities + room_capacities[room]
    course_nums =  int(constraints_file.next().split()[1])
    prof_nums = int(constraints_file.next().split()[1])
    # courses_to_profs = {}
    for course in range(1, course_nums+1):
        courses_to_profs[course] = int(constraints_file.next().split()[1])

popularity = {}
for key in student_prefs:
  for course in student_prefs[key]:
    if not course in popularity:
      popularity[course] = 1
    else:
      popularity[course] += 1
sorted_d = sorted(popularity.items(), reverse=True, key=operator.itemgetter(1))
# print sorted_d[0][0]

timetable = {}
temp = {}
a = 0
total_courses = len(popularity)
total_rooms = room_nums
course_to_timeslot = {}
course_to_room = {}
# print(courses_to_profs)

for room in room_capacities:
  timetable[room] = {}

for room in room_capacities:
  for timeslot in timeslots:
    timetable[room][timeslot] = {}

for room in room_capacities:
  if not room == "":
    if a < total_courses:
      for timeslot in timeslots:
        if a < total_courses:
          course = int(sorted_d[a][0])
          # print courses_to_profs[21]
          if course in courses_to_profs:
            teacher = courses_to_profs[course]
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

              if teacher not in temp:
                temp[teacher]= timeslot
          a = a + 1
        else:
          break
    else:
      break


# remaining = {}
capacity = {}
schedule = {}
max_satisfaction = student_nums*4
achieved_satisfaction = 0


# fill in "remaining"
# for student in student_prefs:
#   if student in remaining:
#     continue
#   else:
#     remaining[student] = [len(student_prefs[student])]

for room in timetable:
  capacity[room] = {}

for room in timetable:
  for timeslot in timetable[room]:
    capacity[room][timeslot] = {}

sc = 1
#fill in "capacity"
for room in timetable:
  for timeslot in timetable[room]:
    if room != '':
        capacity[room][timeslot] = room_capacities[room]

# print(capacity
# print(student_prefs)

for student in student_prefs:
  # print(student)
  # student = int(student)
  # print ("student: " + str(student))
  timeslots = {}
  for cour in student_prefs[student]:
    course = int(cour)
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
              stu_course = int(student_course)
              if stu_course in course_to_room and stu_course in course_to_timeslot:
                  if stu_course == course:
                      break
                  if not course in schedule[student] and course_to_timeslot[course][0] != course_to_timeslot[stu_course][0] and capacity[room_used][timeslot_used] > 0:
                      valid = True
                  else:
                      valid= False
                      break
          if valid:
                      schedule[student].append(course)
                      achieved_satisfaction = achieved_satisfaction + 1
                      # if student in remaining:
                      #     remaining[student][0] = remaining[student][0] - 1
                      if room_used in capacity:
                          if timeslot_used in capacity[room_used]:
                              capacity[room_used][timeslot_used] = capacity[room_used][timeslot_used] - 1
                              # print(capacity[room_used][timeslot_used])

f = open("schedule.txt", 'w')
f.write("Course\t" + "Room\t" + "Teacher\t" + "Time\t" + "Students" + "\n")
for course in course_to_room:
   towrite = str(course) + "\t" + str(course_to_room[course][0]) + "\t" + str(courses_to_profs[course]) + "\t" + str(course_to_timeslot[course][0]) + "\t"
   for student in schedule:
     # print schedule[student]
     if course in schedule[student]:
       towrite = towrite + str(student) + " "
   towrite = towrite + "\n"
   f.write(towrite)
# print(schedule)
time1 = time.time()
print "Runtime: " + str(time1 - time0) +" sec"
satisfaction = decimal.Decimal(achieved_satisfaction) / decimal.Decimal(max_satisfaction)
print "Student satisfaction: " + str(round(satisfaction,5))