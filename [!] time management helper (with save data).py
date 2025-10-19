#this is my code.

import pickle #file handling
from datetime import datetime #assigns a date & time to save data

def yes_no(): #reduces redundancy in code, as I use this exact loop many times
    while True:
        try:
            choice=input(">>>  ").lower()
            if choice not in ("yes","no"):
                raise ValueError
            else:
                break
        except ValueError:
            print("\tEnter 'yes' or 'no'!")
    return choice

def display_it_all_nicely(wants,needs):
    if needs:
        print("\nYou need to do:")
        for task in needs:
            text="\t"+str(task["name"])+" ~ "+str(task["time"])+" mins"#+"(score:"+str(task["score"])+")"
            if task["priority"]:
                text=text+"  (!)"
            print(text)
    if wants:
        print("\nYou want to do:")
        for task in wants:
            text="\t"+str(task["name"])+" ~ "+str(task["time"])+" mins"#+"(score:"+str(task["score"])+")"
            if task["priority"]:
                text=text+"  (!)"
            print(text)

def get_save_data():

    print("Would you like to use previous data? (yes/no)")
    if yes_no()=="no":
        print("Proceeding without save data")
        return [],[]

    try:
        with open("ProductivitySaveData.pkl", "rb") as file:
            imported_data=pickle.load(file)

        if not imported_data: #checks if file is empty
            print("No recovery data found.")
            return [],[]
        
    except FileNotFoundError:
        print("\nSorry, a problem was encountered locating the save data file.")
        print("Please check that 'ProductivitySaveData.pkl' is saved in the same folder as this code!")
        input("\n[ENTER] to proceed without save data.")
        return [],[]
    
    except Exception:
        print("\nSorry, it looks like the save data file is corrupted.")
        print("Retrieving your past data will not be possible.")
        input("[ENTER] to proceed without save data.")
        return [],[]

    #no file-related problem encountered    
    print("Data found from",imported_data["date"])
    print("Would you like to import it and continue? (yes/no)")
    if yes_no()=="no":
        print("Proceeding without save data")
        return [],[]
    else:
        wants=imported_data["wants_list"]
        needs=imported_data["needs_list"]
        display_it_all_nicely(wants,needs)
        return wants, needs
    

def get_tasks(request):
    #'request' follows foramt [wanttodo/needtodo,highprioritytask/taskyouwanttocompletemorethanothers,examples]
    print("\n------------------------------------------------------------------")
    print(f"\nBelow, enter activities you {request[0]} within this time:")
    print("[ENTER] once you are done.\n")
    arr=[]
    
    while True:
        try:
            task_name=input(">>>  ").title()
            if task_name=="":
                print(f"\tAre you sure you have entered all {request[0]} tasks? Proceed? (yes/no)")
                if yes_no()=="yes":
                    break
                else:
                    print(f"\tOk, you're not done yet. Enter your task below: {request[2]} etc.")
                    task_name=input(">>>  ").title()
            
            print(f"\tHow many minutes would you like to assign for <<{task_name}>>")
            while True:
                try:
                    task_time=int(input(">>>  ")) # Will raise ValueError if not an integer
                    if task_time<1 or task_time>300:
                        raise ValueError # Raised if outside the valid range
                    break
                except ValueError:
                    print("\tPlease enter a whole number in the accepted range (1~300)")

            print(f"\tIs this a {request[1]}? (yes/no)")
            priority=(yes_no()=="yes") #called a "ternary conditional expression" wow so cool
            
            arr.append({"time": int(task_time), "priority": priority, "name": task_name})
            print("\n\tTask added! Next:")
            
        except Exception:
            print("\n\tSomething went wrong, please try entering that task again!")
            print(f"\tBelow, enter activities you {request[0]} ([ENTER] once you are done)") 

    print(f"Great! You have successfully added all your {request[0]} tasks")
    return arr

def priority_score(task):

    priority_multiplier=5 if task["priority"] else 1  #this line can be changed to adjust preferences
    #prioritised tasks are flagged as 5 times more important
    #i.e. a priority task that takes 60mins has same score as non-priority task that takes 12 minutes
    #the higher the score, the more important it is

    dampener=5#this line can be changed to adjust preferences
    #The dampener acts to smooth out the harsh logarithmic scaling of priority/time
    #without it, short&easy tasks are aggressively favoured over others
    #This results in longer tasks being pushed towards the bottom (despite being important)
    #i.e. The dampener can be thought of as a 'minimum effective time' for all tasks
    
    time=task["time"]+dampener
    score=round(priority_multiplier/time,3)
    return score
    
################################# main code #############################

def main():

    print("\nThis is the TIME MANAGEMENT HELPER. Let's get started!")
    wants,needs=get_save_data()

    loop_response="*"
    while loop_response=="*":

        needs.extend(get_tasks(["NEED to do","high priority task","chores, habits, to-dos,"]))
        wants.extend(get_tasks(["WANT to do","task you want to complete more than others","hobbies, rewards, very low priority tasks,"]))

        #calculating priority score then sorting task items based on it:
        for need in needs:
            need["score"]=priority_score(need)
        for want in wants:
            want["score"]=priority_score(want)
        needs.sort(key=lambda task: task["score"], reverse=True)
        wants.sort(key=lambda task: task["score"], reverse=True)

        display_it_all_nicely(wants,needs)

        print("Input (*) to add more tasks, or [ENTER] to exit/save.")
        loop_response=input(">>>  ")

    #user exits main loop
    print("\n------------------------------------------------------------------")
    print("\nWould you like to save the above data? (yes/no)")
    print("DISCLAIMER: THIS OVERWRITES PREVIOUS FILE DATA")

    if yes_no()=="yes":
        now=datetime.now()
        #dd/mm/yyyy format (because I say so)
        save_date= str(now.day) +"/"+ str(now.month) +"/"+ str(now.year) +" at "+ str(now.strftime("%H:%M"))
        try:
            dump_data={"date":save_date,"wants_list":wants,"needs_list":needs}
            pickle.dump(dump_data, open("ProductivitySaveData.pkl", "wb"))
            print("Save successful!")
            
        except Exception:
            print("Sorry, a problem was encountered whilst saving to the file.")
            print("Saving your data will not be possible right now.")
        
    else:
        print("Current data discarded.")

    input("\n[ENTER] twice to quit window.")
    quit()
   
            
main()

