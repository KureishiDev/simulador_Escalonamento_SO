from collections import deque


class FifoScheduler:
    def select_next_task(self, ready_queue, running_task=None):
        if running_task:
            return running_task

        if not ready_queue:
            return None
        return ready_queue.popleft()


class PriorityScheduler:
    def select_next_task(self, ready_queue, running_task=None):
        candidates = list(ready_queue)
        if running_task:
            candidates.append(running_task)

        if not candidates:
            return None

        highest_priority_task = min(candidates, key=lambda task: task.priority)
        return highest_priority_task


class SrtfScheduler:
    def select_next_task(self, ready_queue, running_task=None):
        candidates = list(ready_queue)
        if running_task:
            candidates.append(running_task)

        if not candidates:
            return None

        shortest_remaining_task = min(candidates, key=lambda task: task.remaining_time)
        return shortest_remaining_task
