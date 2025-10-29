import time
from collections import deque
from task import Task
from scheduler import FifoScheduler, PriorityScheduler, SrtfScheduler


class Simulator:
    def __init__(self, config_file_path):
        self.global_tick = 0
        self.running_task = None
        self.task_list = []
        self.original_task_list = [] #copia da lista p/ mostrar na janela ver dados
        self.ready_queue = deque()
        self.scheduler = None
        self.scheduling_algorithm_name = "N/A"
        self.quantum = 0 #para o projeto b
        self._load_tasks_from_file(config_file_path)

    def _load_tasks_from_file(self, file_path):
        try:
            with open(file_path, "r") as f:
                first_line = f.readline().strip().split(";")
                self.scheduling_algorithm_name = first_line[0].upper()
                self.quantum = int(first_line[1])

                if self.scheduling_algorithm_name in ("FIFO", "FCFS"):
                    self.scheduler = FifoScheduler()
                elif self.scheduling_algorithm_name == "PRIOP":
                    self.scheduler = PriorityScheduler()
                elif self.scheduling_algorithm_name == "SRTF":
                    self.scheduler = SrtfScheduler()
                else:
                    self.scheduler = FifoScheduler()

                for line in f:
                    parts = line.strip().split(";")
                    task_id, color, arrival_time, duration = parts[0:4]
                    priority = parts[4] if len(parts) > 4 else "99"
                    events = parts[5:] if len(parts) > 5 else []
                    new_task = Task(
                        task_id, color, arrival_time, duration, priority, events
                    )
                    self.task_list.append(new_task)

            self.original_task_list = list(self.task_list)

        except Exception as e: 
            print(f"Erro ao ler o arquivo de configuração: {e}")
            self.task_list = []
            self.original_task_list = []

    def _check_for_new_arrivals(self): #checa se vem tarefa pronta no tick
        for task in self.task_list[:]:
            if task.arrival_time == self.global_tick:
                task.status = "PRONTO"
                self.ready_queue.append(task)
                self.task_list.remove(task)
                print(
                    f"Tick {self.global_tick}: Tarefa {task.task_id} chegou e está PRONTA."
                )

    def _is_simulation_complete(self): #acaba se nao tem mais tarefa p/ chegar
        return not self.task_list and not self.ready_queue and self.running_task is None

    def tick(self): #roda o tick-tack 
        if self._is_simulation_complete():
            print(f"\n--- Simulação Concluída em {self.global_tick} ticks ---")
            return None

        print(f"Tick {self.global_tick}:")

        self._check_for_new_arrivals()
        #decisao do escalonador
        best_candidate = self.scheduler.select_next_task(
            self.ready_queue, self.running_task
        )
        #compara o melhor candidato com quem ja esta rodando, p/ ver se precisa trocar
        if self.running_task != best_candidate:
            #se tinha alguem rodando e ele n é o melhor...
            if self.running_task:
                print(f"  > Tarefa {self.running_task.task_id} foi PREEMPTADA.")
                self.running_task.status = "PRONTO"
                self.ready_queue.append(self.running_task)

            self.running_task = best_candidate #melhor candidato vira a tarefa que vai rodar
            if self.running_task: #se for ninguem
                if self.running_task in self.ready_queue:
                    self.ready_queue.remove(self.running_task) #tira da fila, vai p pseudo cpu

                self.running_task.status = "EXECUTANDO"
                #se for a primeira vez rodando, flagga -1
                if self.running_task.start_time == -1:
                    self.running_task.start_time = self.global_tick
                print(
                    f"  > Tarefa {self.running_task.task_id} (Prio:{self.running_task.priority} | Restante:{self.running_task.remaining_time}) começou/continuou a EXECUTAR."
                )

        task_that_ran_this_tick = None #guarda quem rodou nesse tick p desenhar depois, começando com ninguem
        if self.running_task:
            #avisa que esta rodando
            print(f"  > Tarefa {self.running_task.task_id} está executando...")
            #diminui o tempo p/ terminar
            self.running_task.remaining_time -= 1
            #marca como tarefa que rodou neste tick
            task_that_ran_this_tick = self.running_task

            if self.running_task.remaining_time <= 0:   #checa se terminou
                self.running_task.status = "TERMINADO"
                self.running_task.finish_time = self.global_tick + 1
                print(f"  > Tarefa {self.running_task.task_id} TERMINOU.")
                self.running_task = None
        else:
            print("  > CPU Ociosa.")

        self.global_tick += 1 #avança o relogio global p proximo round
        return task_that_ran_this_tick
