import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

class ThreadWorker:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=cpu_count())
        self.executor.submit(self.loop.run_forever)

    def run(self, task):
        return asyncio.run_coroutine_threadsafe(task,self.loop)

    def quit(self):
        self.loop.stop()
        self.executor.shutdown()
