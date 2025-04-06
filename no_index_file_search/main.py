import multiprocessing

from master import Master
from worker import Worker, start_worker

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Required for Windows

    # Example setup
    worker_configs = [
        ("D:/an3sem2", 3001),
        ("/texts1", 3002)
    ]

    processes = []
    for path, port in worker_configs:
        p = multiprocessing.Process(target=start_worker, args=(path, port))
        p.start()
        processes.append(p)

    master = Master(["http://localhost:3001/api/search"])
    master.run()

    for p in processes:
        p.join()
