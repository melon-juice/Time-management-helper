
def get_tasks(request):
    #request follows foramt [wanttodo/needtodo,highprioritytask/taskyouwanttoprioritisecompleting,examples]
    print(f"\nBelow, enter activities you {request[0]} within this time:")
    print("[ENTER] once you are done.\n")    
    while True:
        try:
            task_name=input(">>>  ").title()
            if task_name=="":
                print(f"\tAre you sure you have entered all {request[0]} tasks? Proceed? (yes/no)")
                while True:
                    try:
                        choice=input(">>>  ").lower()
                        if choice not in ("yes","no"):
                            raise ValueError
                        else:
                            break
                    except ValueError:
                        print("\tEnter 'yes' or 'no'!")
                    
                if choice=="yes":
                    break
                else:
                    print(f"\tOk, you're not done yet. Enter your task below: {request[2]} etc.")
                    task_name=input(">>>  ").title()
            
            print(f"\tHow many minutes would you like to assign for <<{task_name}>>")
            while True:
                try:
                    task_time_int=int(task_time) # Will raise ValueError if not an integer
                    if task_time_int<1 or task_time_int>300:
                        raise ValueError # Raised if outside the valid range
                    break
                except ValueError:
                    print("\tPlease enter a whole number in the accepted range (1~300)")

            print(f"\tIs this a {request[1]}? (yes/no)")
            while True:
                try:
                    importance=input(">>>  ").lower()
                    if importance not in ("yes","no"):
                        raise ValueError
                    else:
                        if importance=="yes":
                            priority=True
                            break
                        else:
                            priority=False
                            break
                            
                except ValueError:
                    print("\tEnter 'yes' or 'no'!")
            
            arr=[]
            arr.append({"time": int(task_time), "priority": priority, "name": task_name})
            print("\n\tTask added! Next:")
            
        except Exception:
            print("\n\tSomething went wrong, please try entering that task again!")
            print(f"\tBelow, enter activities you {request[0]} ([ENTER] once you are done)") 

    print(f"Great! You have successfully added all your {request[0]} tasks")
    return arr

def priority_score(task):

    priority_multiplier=5 if task["priority"] else 1 #prioritised tasks are flagged as 5 times more important

    score=round(float(priority_multiplier/int(task["time"])),3) #the higher the score, the more important it is
    #priority task that takes 60mins is same importance as non-priority task that takes 12 minutes

    return score
    
        
################################# main code #############################

def main():
    needs=[]
    wants=[]

    loop_response="*"
    while loop_response=="*":

        needs.extend(get_tasks(["need to do","high priority task","chores, habits, to-dos,"]))
        wants.extend(get_tasks(["want to do","task you want to prioritise over others","hobbies, rewards, very low priority tasks,"]))
        
        for need in needs:
            need["score"]=priority_score(need)
        for want in wants:
            want["score"]=priority_score(want)

        needs.sort(key=lambda task: task["score"], reverse=True)
        wants.sort(key=lambda task: task["score"], reverse=True)

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

        print("Input (*) to add more tasks, or [ENTER] to exit the program.")
        loop_response=input(">>>  ")
            
main()

