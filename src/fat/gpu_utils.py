import cupy as cp
import gc
import logging
from contextlib import contextmanager


@contextmanager
def gpu_memory_scope(*arrays: cp.ndarray):
    try:
        yield
    finally:
        for arr in arrays:
            try:
                del arr
            except Exception:
                pass
        cp.cuda.Stream.null.synchronize()
        gc.collect()
        cp.get_default_memory_pool().free_all_blocks()
        logging.info("Memória GPU liberada pelo context manager.")


def log_gpu_memory(stage: str) -> None:
    used = cp.get_default_memory_pool().used_bytes() / 1e6
    logging.info(f"[{stage}] Memória GPU usada: {used:.2f} MB")
