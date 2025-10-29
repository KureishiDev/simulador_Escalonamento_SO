class Task: 
    #classe pseudo tcb

    def __init__(
        self, task_id, color, arrival_time, duration, priority_str, events_list=None
    ):
         #dados que vem do arquivo txt
        self.task_id = task_id
        self.color = color
        self.arrival_time = int(arrival_time)
        self.duration = int(duration)
        
        self.priority = int(priority_str) if priority_str else 0
        #isso aqui fica para o projeto B
        self.events = events_list if events_list is not None else []
        # começa igual ao tempo total dela
        self.remaining_time = self.duration
        self.status = "NOVO"
        # a hora (tick) que ela rodou pela primeira vez (pra calcular tempo de resposta)
        # começa com -1 pra gente saber que nunca rodou
        self.start_time = -1
        # que terminou
        self.finish_time = -1
        # que entrou na fila de prontos
        self.waiting_since = -1

    def __repr__(self): # isso  define como a tarefa aparece se der um print nela

        return (
            f"Task({self.task_id}, Chegada:{self.arrival_time}, "
            f"Duração:{self.duration}, Prio:{self.priority})"
        )
