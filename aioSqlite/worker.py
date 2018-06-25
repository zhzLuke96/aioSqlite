import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count


class ThreadWorker:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=cpu_count())

    def run(self, func, *args, **kwargs):
        return self.executor.submit(func, *args, **kwargs)

    def shoutdown(self):
        self.executor.shutdown()


def ThreadWrapper(func, *args, **kwargs):
    return ThreadWorker().run(func, *args, **kwargs)


async def ThreadAsyncWrapper(func, *args, **kwargs):
    tw = ThreadWorker()
    future = tw.run(func, *args, **kwargs)
    while True:
        if future.done():
            return future.result()
        else:
            await asyncio.sleep(0.001)


class AsyncWorker:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        ThreadWrapper(self.loop.run_forever)

    def run(self, task):
        return asyncio.run_coroutine_threadsafe(task, self.loop)

    async def wait(self, task):
        future = self.run(task)
        while True:
            if future.done():
                return future.result()
            else:
                await asyncio.sleep(0.001)

    def quit(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


def test1():
    import random
    import string
    g_S = ""

    async def testFunc(s):
        global g_S
        t = int(random.random() * 10)
        await asyncio.sleep(t)
        g_S += s
        print(str(t) + " s,print", s)
        t = int(random.random() * 10)
        await asyncio.sleep(t)
        g_S += s
        return t, s
    try:
        wk1 = ThreadWorker()
        tasks1 = [wk1.run(testFunc(t)) for t in string.ascii_letters]

        wk2 = ThreadWorker()
        tasks2 = [wk2.run(testFunc(t)) for t in string.digits]

        print([t.result() for t in tasks1])
        print([t.result() for t in tasks2])
        print("global", g_S)
        wk1.quit()
        wk2.quit()
    except KeyboardInterrupt:
        pass


def test2():
    import random
    from time import sleep, time
    start = time()

    def randSleep():
        st = int(random.random() * 5)
        sleep(st)
        print("wait", st)
        return st

    async def testfunc(name):
        st = await ThreadAsyncWrapper(randSleep)
        print(name, st)
    try:
        ak = AsyncWorker()
        tasks = [ak.run(testfunc(t)) for t in ["a", "b", "c"]]
        print([t.result() for t in tasks])
        ak.quit()
    except KeyboardInterrupt:
        pass
    print("use time", time() - start)


if __name__ == '__main__':
    test2()
