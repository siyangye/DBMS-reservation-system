from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    #create_patient <username> <password>
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    #input:  date, (table: Availability)
    #output: caregiver: username, vaccine:name, doses. (table: caregiver; Vaccines)
    # Separate each attribute with a space.

    #check 1: If not logged in yet: 
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    #check 2:
    if len(tokens) != 2:
        print("Please try again!")
        return
    
    date = tokens[1]

    caregiver = None
    try:
        # caregiver = Caregiver() #create an instance
        caregivers = Caregiver.get_available_caregivers(date) # list: get the instance that match input date
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    if caregivers is None:
        print("There is no available caregiver for the date.")
        return
    
    try:
        vaccines = Vaccine.get_all_vaccines()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    if vaccines is None:
        print("There is no available vaccines.")
        return 
   
    for caregiver in caregivers:
        for vaccine in vaccines:
            print(f"Caregiver:{caregiver.get_username()} Date:{date} Vaccine name:{vaccine.get_vaccine_name()} doses:{vaccine.get_available_doses()}")

def reserve(tokens):
    #input: date vaccine
    #output: caregiver_username, a_id

    #check 1: if Patient not logged in:
    global current_patient
    global current_caregiver
    if current_patient is None:
        print("Please login first!")
        return
    #check 2: if Caregiver loggin in:
    if current_caregiver is not None:
        print("Please login as a patient!")
        return
    #check 3: arguments:
    if len(tokens) != 3:
        print("Please try again!")
        return
    """
    TODO: check: no available Caregiver
    TODO: no available vaccine
    """
    date = tokens[1]
    vaccine_name = tokens[2]

    caregivers = Caregiver.get_available_caregivers(date)
    #check: available Caregiver
    if caregivers is None:
        print("No Caregiver is available!")
        return 

    #check: available vaccine:
    vaccine = Vaccine(vaccine_name, None) #create an instance for vacccine.
    #update the available_doses:
    vaccine = vaccine.get() #updated instance, calling function on instance, not Class!

    if vaccine.get_available_doses() <= 0:
        print("Not enough available doses!")
        return
    
    #output the available result:
    caregiver = caregivers[0] #choose the first available in table. 
    c_username = Caregiver.get_username(caregiver) #problem?
    p_username = current_patient.get_username()
    print(p_username)
    print(c_username)
    #generate ID:
    appointment_id = Appointment.generate_id()
    #create a row/instance for Appointment table:
    appointment = Appointment(
        a_id=appointment_id,
        date = date,
        c_username = c_username,
        p_username = p_username,
        vaccine_name=vaccine_name)
    #save it to db:
    try:
        appointment.save_to_db()
    except pymssql.Error as e:
        print("Apponitment table update failed.")
        print("Db-Error:", e) #ok I failed here, but why 
        return #why quit?
    except Exception as e:
        print("Apponitment table update failed.")
        print("Error:", e)
        return
    # print("success!")
    
    #delete a row/instance for Availability table:
    ##process the format of data:
    date_whole= date.split("-")
    month = int(date_whole[0])
    day = int(date_whole[1])
    year = int(date_whole[2])

    

    try:
        d = datetime.datetime(year, month, day)
        caregiver.delete_availability(d)
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e) #debug point 
        return #why quit?
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return
    
    print(f"Appointment ID:{appointment_id}, Caregiver username:{c_username}")



def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    # TODO: Part 2
    # '''
    # pass
    #input: (patient/caregiver username)
    #For caregivers, you should print the appointment ID, vaccine name, date, and patient name. Order by the appointment ID. Separate each attribute with a space.
    # For patients, you should print the appointment ID, vaccine name, date, and caregiver name. Order by the appointment ID. Separate each attribute with a space.
    #check 1: user not log in:
    global current_caregiver
    global current_patient
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    #check 2: wrong input:
    if len(tokens) != 1:
        print(" Wrong input usage!")
        return 
    #CASE 1: input- patient
    if current_patient is not None: #patient is logged in!
        #get the patient username:
        p_username = Patient.get_username(current_patient)
        #get appointment that match p_username:
        appointment = Appointment.get_patient_appointment(p_username) #did I make sure I get all the instance?
        # return appointment
        #if no match, print message: 
        # if len(appointment) == 0:
            # print("No appointment made yet!")
        
        



    #CASE 2: input- patient





def logout(tokens):
    #check if the argument is correct:
    if len(tokens) > 1:
        print("Logout command does not take any additional arguments. ")
        return
    
    #check if patient/ cargiver is logged in already: 
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    #logout the current user:
    current_caregiver = None 
    current_patient = None
    print("Successfully logged out!")

def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()

#what is the debug code?
#edge case:if one does is already reserved by a patient, it shouldn't be reserved by another 