import heapq
import random
import time


class Scheduler:
    """ The purpose of this class is to provide a way for tasks to be scheduled in a thread-safe manner.

    FL Studio's midi script does not allow usage of the threading library in Python. As such, we need to implement
    a scheduler that runs on the OnIdle loop of the midi script. This allows one to schedule future tasks without
    needing to worry about additional boiler-plate code. The only requirement is that this class's Refresh method
    must be hooked up to midiscript's the OnIdle event.
    """
    def __init__(self):
        self._tasks_pq = []
        self._random = random.Random()
        self._seq = 0

    def ScheduleTask(self, task, delay=0):
        time_ms = time.monotonic() * 1000
        # Sequence + random break ties so heap never compares the callable.
        self._seq += 1
        entry = (time_ms + delay,
                 self._seq,
                 int(self._random.random() * 16777215),
                 task)
        heapq.heappush(self._tasks_pq, entry)
        return entry

    def CancelTask(self, entry):
        try:
            self._tasks_pq.remove(entry)
            heapq.heapify(self._tasks_pq)
            return True
        except ValueError:
            # Entry was already removed and executed.
            return False

    def Idle(self):
        time_ms = time.monotonic() * 1000
        while self._tasks_pq:
            entry = heapq.heappop(self._tasks_pq)
            if entry[0] > time_ms:
                # Entry delay condition not met. Put back on queue and wait until next refresh cycle.
                heapq.heappush(self._tasks_pq, entry)
                return
            task = entry[-1]
            task()
