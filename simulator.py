import time
from collections import deque
from task import Task #representa cada processo 
from scheduler import FifoScheduler, PriorityScheduler, SrtfScheduler #algoritmos que implementei em scheduler.py

class Simulator:
    def __init__(self, config_file_path): #inicializa o simulador
        self.global_tick = 0
        self.running_task = None     #ngm na cpu
        self.task_list = []          #onde as tarefas ficam esperando
        self.original_task_list = [] #guarda uma copia da lista original p a funcionalidade |ver dados|
        self.ready_queue = deque()   #fila de quem ta pronto
        self.scheduler = None        #inicializa em nenhum algoritmo, dps que le o arquivo, muda
        self.scheduling_algorithm_name = "N/A"
        self.quantum = 0
        self._load_tasks_from_file(config_file_path)  #carrega as tarefas do txt

    def _load_tasks_from_file(self, file_path): #funcao que le o txt
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().strip().split(';')
                self.scheduling_algorithm_name = first_line[0].upper()
                self.quantum = int(first_line[1])
                
                if self.scheduling_algorithm_name in ('FIFO', 'FCFS'):
                    self.scheduler = FifoScheduler()
                elif self.scheduling_algorithm_name == 'PRIOP':
                    self.scheduler = PriorityScheduler()
                elif self.scheduling_algorithm_name == 'SRTF':
                    self.scheduler = SrtfScheduler()
                else:
                    self.scheduler = FifoScheduler() #se nao reconhecer usa fifo mesmo

                for line in f: #le as linhas, uma pra cada tarefa
                    parts = line.strip().split(';')
                    task_id, color, arrival_time, duration = parts[0:4]
                    priority = parts[4] if len(parts) > 4 else '99'
                    events = parts[5:] if len(parts) > 5 else []
                    new_task = Task(task_id, color, arrival_time, duration, priority, events)
                    self.task_list.append(new_task)
             
            self.original_task_list = list(self.task_list) #copia para a janela |ver dados|

        except Exception as e:          #tratando excecao
            print(f"Erro ao ler o arquivo de configuração: {e}")
            self.task_list = []
            self.original_task_list = []

    def _check_for_new_arrivals(self): #a cada tick a funcao checa se alguma tarefa nova chegou
        for task in self.task_list[:]:
            if task.arrival_time == self.global_tick: #se o tempo de chegada bate com o tempo atual
                task.status = 'PRONTO' #marca a tarefa como pronta
                self.ready_queue.append(task) #joga na fila de prontos
                self.task_list.remove(task) #tira a lista de espera
                print(f"Tick {self.global_tick}: Tarefa {task.task_id} chegou e está PRONTA.") #print/log pra checar

    def _is_simulation_complete(self): #verifica se a simulacao completou
        return not self.task_list and not self.ready_queue and self.running_task is None

    def tick(self): #aqui roda o passo a passo da simulacao
        if self._is_simulation_complete():
            print(f"\n--- Simulação Concluída em {self.global_tick} ticks ---")
            return None #avisa a interface grafica que acabou

        print(f"Tick {self.global_tick}:") 
        
        self._check_for_new_arrivals() #ve se chegou alguem novo
        
        best_candidate = self.scheduler.select_next_task(self.ready_queue, self.running_task) #chama o algoritmo de escalonamento p decidir quem vai rodar
                                                                                              #considerando quem ta na fila e/ou rodando p/ preemptivos
        if self.running_task != best_candidate: # compara o melhor candidato com quem tá rodando pra ver se precisa trocar (preempção)
            if self.running_task:
                print(f"  > Tarefa {self.running_task.task_id} foi PREEMPTADA.")
                self.running_task.status = 'PRONTO'
                self.ready_queue.append(self.running_task) #joga de volta na fila
            
            self.running_task = best_candidate #quem ganha a cpu?
            if self.running_task:
                 # se o escolhido veio da fila, tira ele de lá
                if self.running_task in self.ready_queue:
                    self.ready_queue.remove(self.running_task)
                
                self.running_task.status = 'EXECUTANDO'
                 # se é a primeira vez rodando, marca o tempo de início (pra calcular tempo de resposta depois)
                if self.running_task.start_time == -1:
                    self.running_task.start_time = self.global_tick
                print(f"  > Tarefa {self.running_task.task_id} (Prio:{self.running_task.priority} | Restante:{self.running_task.remaining_time}) começou/continuou a EXECUTAR.")
        #executa um tick da tarefa que tá na cpu
        task_that_ran_this_tick = None
        if self.running_task:
            print(f"  > Tarefa {self.running_task.task_id} está executando...")
            self.running_task.remaining_time -= 1
            task_that_ran_this_tick = self.running_task 
        #verifica se a tarefa terminou
            if self.running_task.remaining_time <= 0:
                self.running_task.status = 'TERMINADO'
                self.running_task.finish_time = self.global_tick + 1 
                print(f"  > Tarefa {self.running_task.task_id} TERMINOU.")
                self.running_task = None
        else:
            print("  > CPU Ociosa.")
       #avança o relogio
        self.global_tick += 1
        return task_that_ran_this_tick
