#necessary imports:
import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql
#import modules:
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Vaccine import Vaccine
#I import:
import random

#class Appointment:
class Appointment:
    def __init__(self, a_id, date, c_username, p_username, vaccine_name):
        #its own keys:
        self.a_id = a_id
        self.date = date
        #all the foreign keys: -- remain undecided...
        self.c_username = c_username
        self.p_username = p_username
        self.vaccine_name = vaccine_name 
    
    #getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_appointment_details = "SELECT a_id, date, c_username, p_username, Vaccine_name FROM Appointments WHERE a_id = %s"
        try:
            cursor.execute(get_appointment_details, self.a_id)
            for row in cursor:
                self.date = row['date']
                self.c_username = row['c_username']
                self.p_username = row['p_username']
                self.vaccine_name = row['Vaccine_name']
                return self
        except pymssql.Error:
            # print("Error occurred when getting Appointment")
            raise
        finally:
            cm.close_connection()
        return None
    
    #get keys that is unique for Appointment table:
    def get_a_id(self):
        return self.a_id
    
    def get_date(self):
        return self.date
    
    #get/connect foreign data entry: 
    def get_caregiver(self):
        # Use self.c_username to fetch the Caregiver object from the database
        caregiver = Caregiver(self.c_username) #create a caregiver instance
        caregiver.get() #getter method in Caregiver class 
        return caregiver
    
    def get_patient(self):
        patient = Patient(self.p_username)
        patient.get()
        return patient
    
    def get_vaccine(self):
        vaccine = Vaccine(self.vaccine_name)
        vaccine.get()
        return vaccine 

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        #save new data entry to appointment:
        add_appointments = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(add_appointments, (self.a_id, self.date, self.p_username, self.c_username, self.vaccine_name))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection() 
    
    #generate ID:
    def generate_id():
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        while True:
            appointment_id = random.randint(10000000, 99999999)
            check_id_query = "Select Count(*) from Appointments Where a_id = %s"
            cursor.execute(check_id_query,(appointment_id,))
            result = cursor.fetchone()[0]

            if result == 0:
                break
        cm.close_connection()
        return appointment_id
    
    #get appointment with p_username:
    def get_patient_appointment(p_username):
        #connect with db:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        #query appointment table:
        get_appointment_db = "Select a_id, Vaccine_name, date, c_username from Appointments Where p_username = %s Order by a_id"
        appointments = [] #store a list of appointment
        #somthing is wrong that my list didn't append the following: 
        try:
            cursor.execute(get_appointment_db, p_username)
            for row in cursor:
                a_id = row['a_id']
                date = row['date']
                #row[2] is p_username
                c_username = row['c_username']
                vaccine_name = row['Vaccine_name'] #align with python, but not sql...
                appointment = Appointment(a_id, date, c_username, p_username, vaccine_name)#create instance of appointment 
                appointments.append(appointment)
        except pymssql.Error as e:
            print("Error occurred when updating caregiver availability")
            raise e
        finally:
            cm.close_connection()
        return appointments #return the whole list 



    











#def __init__(): not sure if I import foreign keys in the right way

# secure all the features:
# reserve <data><vaccine>: create a_id
# cancel <a_id>: delete a_id
# I am worried: Is my getter methods for foreign key reseasonable?
# in save_to_db() method, I stored all the attributes including the foreign keys. 