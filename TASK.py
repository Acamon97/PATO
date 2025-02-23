

def perform_command(command):
    global tasks
    global listeningToTask
    global askingAQuestion
    global should_run
    global listening_for_trigger_word
    if command:
        print("Command: ", command)
        if listeningToTask:
            tasks.append(command)
            listeningToTask = False
            respond("Adding " + command + " to your task list. You have " + str(len(tasks)) + " currently in your list.")
        elif "add a task" in command:
            listeningToTask = True
            respond("Sure, what is the task?")
        elif "list tasks" in command:
            respond("Sure. Your tasks are:")
            for task in tasks:
                respond(task)
        elif "take a screenshot" in command:
            pyautogui.screenshot("screenshot.png")
            respond("I took a screenshot for you.")
        elif "open chrome" in command:
            respond("Opening Chrome.")
            webbrowser.open("http://www.youtube.com/@JakeEh")
        elif "ask a question" in command:
            askingAQuestion = True
            respond("What's your question?")
            return
        elif askingAQuestion:
            askingAQuestion = False
            respond("Thinking...")
            print("User command: ", command)
            output = model.generate(command, max_tokens=200)
            print("Output: ", output)
            respond(output)
        elif "exit" in command:
            should_run = False
        else:
            respond("Sorry, I'm not sure how to handle that command.")
    listening_for_trigger_word = True
