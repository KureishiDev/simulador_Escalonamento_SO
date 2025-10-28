class Task:

    def __init__(
        self, task_id, color, arrival_time, duration, priority_str, events_list=None
    ):

        self.task_id = task_id
        self.color = color
        self.arrival_time = int(arrival_time)
        self.duration = int(duration)

        self.priority = int(priority_str) if priority_str else 0

        self.events = events_list if events_list is not None else []

        self.remaining_time = self.duration
        self.status = "NOVO"

        self.start_time = -1
        self.finish_time = -1
        self.waiting_since = -1

    def __repr__(self):

        return (
            f"Task({self.task_id}, Chegada:{self.arrival_time}, "
            f"Duração:{self.duration}, Prio:{self.priority})"
        )
