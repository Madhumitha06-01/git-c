class CrewRunner:
    def __init__(self, name, task_list):
        self.name = name
        self.task_list = task_list

    def run_tasks(self):
        print(f"Running tasks for {self.name}:")
        for task in self.task_list:
            self.run_task(task)

    def run_task(self, task):
        print(f"Executing task: {task}")
