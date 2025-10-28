
# aqui temos a classe task, que serve como o bloco de controle de processo (tcb)
# ela guarda todas as informações sobre uma tarefa específica.

class Task:

    def __init__(self, task_id, color, arrival_time, duration, priority_str, events_list=None):
      
        self.task_id = task_id #atributos lidos do txt
        self.color = color
        self.arrival_time = int(arrival_time)
        self.duration = int(duration)
        
        # a prioridade da tarefa. números menores são mais importantes
        self.priority = int(priority_str) if priority_str else 0
        #se não passar lista de eventos, cria uma lista vazia
        self.events = events_list if events_list is not None else []

       #quanto tempo de cpu ainda falta. começa igual à duração total
        self.remaining_time = self.duration  
        self.status = 'NOVO'  
        # o "tick" em que a tarefa executou pela primeira vez, comeca em -1 p saber que nunca rodou
        self.start_time = -1      
        # o "tick" em que a tarefa executou pela primeira vez, comeca em -1 p saber que nao terminou
        self.finish_time = -1    
        #p calcular tempo de espera
        self.waiting_since = -1   

    def __repr__(self):
       
        return (f"Task({self.task_id}, Chegada:{self.arrival_time}, "
                f"Duração:{self.duration}, Prio:{self.priority})")
