class Course:
    def __init__(self, id , name , levels , departments , assigned_lecturer):
        self.id = id
        self.name = name
        self.levels = levels
        self.departments = departments
        self.assigned_lecturer = assigned_lecturer
        



class Room:
    def __init__(self, name, capacity, type):
        self.name = name
        self.capacity = capacity
        self.type = type 



class Lecturer:
    def __init__(self , name , max_hours_per_day , type):
        self.name = name
        self.max_hours_per_day = max_hours_per_day
        self.type = type

class TimeSlot:
    def __init__(self, day, time_range):
        self.day = day
        self.time_range = time_range


class ScheduleSession:
    def __init__(self, course, room, lecturer, timeslot):
        self.course = course
        self.room = room
        self.lecturer = lecturer
        self.timeslot = timeslot








        
