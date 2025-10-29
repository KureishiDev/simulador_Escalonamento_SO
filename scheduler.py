from collections import deque

class FifoScheduler:  #mais simples, quem chega primeiro roda primeiro
    def select_next_task(self, ready_queue, running_task=None): #se ja tem alguem rodando, deixa ele terminar
        if running_task:
            return running_task
        
        if not ready_queue: #se nao tem ninguem rodando e a fila ta vazia, fica ocioso
            return None
        return ready_queue.popleft() #se tem gente na fila, pega o primeiro que chegou, no caso o da esquerda

class PriorityScheduler:
    #escolhe pela prioridade (menor = mais importante)
    #ele preempta se chega alguem mais importante
    def select_next_task(self, ready_queue, running_task=None):
        #junta todos que podem rodar e/ou quem ta na fila e quem ta rodando caso seja o caso
        candidates = list(ready_queue)
        if running_task:
            candidates.append(running_task)
        
        #se nao tem nada, cpu fica ociosa.
        if not candidates:
            return None
        
        #acha quem tem o menor numero de prioridade da lista
        highest_priority_task = max(candidates, key=lambda task: task.priority)
        return highest_priority_task


#escolhe quem tem menos tempo faltando p/ terminar, tbm preemptivo, se chega alguem que termina mais rapido ele troca.
class SrtfScheduler:
    #mesma logica do de prioridades, junta todos que podem rodar (fila + quem ta na cpu).
    def select_next_task(self, ready_queue, running_task=None):
        candidates = list(ready_queue)
        if running_task:
            candidates.append(running_task)
            
        if not candidates:
            return None
        
        # --- lógica de desempate ---
        #chave de ordenação  p/ o caso de empate
    
        def sort_key(task):
            #o critério principal é o tempo restante (quem tem menos, ganha)
            remaining_time = task.remaining_time
            
            #critério de desempate: se o tempo for igual,
            #quem já estava rodando (running_task) tem preferência.
            #  0 p/ quem ta rodando e 1 p/ quem ta na fila,
            #assim o min() sempre vai pegar o 0 em caso de empate.
            is_running = 0 if task is running_task else 1
            
            #retorna uma tupla. o python ordena primeiro pelo tempo, depois pelo desempate.
            return (remaining_time, is_running)
        
        #acha a tarefa "mínima" usando a  chave de desempate
        shortest_remaining_task = min(candidates, key=sort_key)
        
    
        return shortest_remaining_task
