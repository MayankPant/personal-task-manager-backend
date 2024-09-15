

def capitalize(input: str) -> str:
    try:
        return " ".join([input[0].upper() + input[1:] for input in input.split(" ")])
    except Exception as e:
        print(f"Error Occured: {e}")
        return ""
    
def parse_user_data(user_tasks) -> list:
    data = {}
    print(f"user tasks: {user_tasks} \n\n\n\n")
    total_tasks = len(user_tasks)
    pending_tasks = sum(1 for task in user_tasks if task.status == 'Pending')
    completed_tasks = sum(1 for task in user_tasks if task.status == 'Completed')
    in_progress = sum(1 for task in user_tasks if task.status == 'In Progress')
    
    user_tasks.order_by("-due_date")
    print(f"sorted user tasks: {user_tasks} \n\n\n\n\n")

    five_urgent_tasks = []
    for task in user_tasks[0:3]:
        five_urgent_tasks.append({
            "title" : task.title,
            "description":task.description,
            "due_date":task.due_date.strftime('%Y-%m-%d'),
            "status":task.status,
            "priority":task.priority,
            "created_at": task.created_at.strftime('%Y-%m-%d'),
            "updated_at":task.updated_at.strftime('%Y-%m-%d'),
        })
    data["total_tasks"] = total_tasks
    data["pending_tasks"] = pending_tasks
    data["completed_tasks"] = completed_tasks
    data["in_progress"] = in_progress
    data["five_urgent_tasks"] = five_urgent_tasks
    print(f"Parsed user data: {data}")
    return data

        
        