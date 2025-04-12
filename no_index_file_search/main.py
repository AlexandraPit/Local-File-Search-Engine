import multiprocessing

from master import Master
from worker import Worker, start_worker

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")

    worker_configs = [
        ("D:/an3sem2/IP", 3001),
        ("D:/an3sem2/SD", 3002),
        ("D:/an3sem2/FLT", 3003),
        ("D:/scoala", 3004),
    ]

    processes = []
    for path, port in worker_configs:
        p = multiprocessing.Process(target=start_worker, args=(path, port))
        p.start()
        processes.append(p)

    master = Master(["http://localhost:3001/api/search", "http://localhost:3002/api/search", "http://localhost:3003/api/search", "http://localhost:3004/api/search"])
    master.run()

    for p in processes:
        p.join()
