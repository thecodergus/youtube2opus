import cupy as cp


def new_interpolation_algorithm(data: cp.ndarray, upscale_factor: int) -> cp.ndarray:
    return cp.repeat(data, upscale_factor)


def initialize_ist(data: cp.ndarray, threshold: float) -> cp.ndarray:
    return cp.where(cp.abs(data) > threshold, data, 0)


def iterative_soft_thresholding(
    data: cp.ndarray, max_iter: int, threshold: float
) -> cp.ndarray:
    data_thres = initialize_ist(data, threshold)
    for _ in range(max_iter):
        data_fft = cp.fft.fft(data_thres)
        data_fft_thres = cp.where(cp.abs(data_fft) > threshold, data_fft, 0)
        data_thres = cp.fft.ifft(data_fft_thres).real
        harmonics = cp.sin(cp.linspace(0, 2 * cp.pi, len(data_thres)))
        data_thres += 0.1 * harmonics
    return data_thres


def lms_filter(
    signal: cp.ndarray,
    desired: cp.ndarray,
    mu: float = 0.001,
    num_taps: int = 32,
    block_size: int = 2048,
) -> cp.ndarray:
    n: int = len(signal)
    w: cp.ndarray = cp.zeros(num_taps, dtype=cp.float32)
    filtered_signal: cp.ndarray = cp.zeros(n, dtype=cp.float32)
    num_blocks: int = (n - num_taps) // block_size

    for b in range(num_blocks):
        start: int = num_taps + b * block_size
        end: int = start + block_size
        X: cp.ndarray = cp.stack(
            [signal[start - i : end - i] for i in range(num_taps)], axis=1
        )
        y: cp.ndarray = X @ w
        e: cp.ndarray = desired[start:end] - y
        w = w + 2 * mu / block_size * X.T @ e
        filtered_signal[start:end] = y
    return filtered_signal


def chunked_block_lms_filter(
    signal: cp.ndarray,
    desired: cp.ndarray,
    mu: float = 0.001,
    num_taps: int = 32,
    block_size: int = 2048,
    chunk_size: int = 10**6,
) -> cp.ndarray:
    n: int = len(signal)
    filtered_signal: cp.ndarray = cp.zeros(n, dtype=cp.float32)
    for chunk_start in range(0, n, chunk_size):
        chunk_end = min(chunk_start + chunk_size, n)
        filtered_signal[chunk_start:chunk_end] = lms_filter(
            signal[chunk_start:chunk_end],
            desired[chunk_start:chunk_end],
            mu=mu,
            num_taps=num_taps,
            block_size=block_size,
        )
    return filtered_signal


def normalize_signal(signal: cp.ndarray) -> cp.ndarray:
    if signal.size == 0:
        raise ValueError("Sinal vazio não pode ser normalizado.")
    return signal / cp.max(cp.abs(signal))


def process_channel(
    channel: cp.ndarray, upscale_factor: int, max_iter: int, threshold: float
) -> cp.ndarray:
    expanded = new_interpolation_algorithm(channel, upscale_factor)
    ist = iterative_soft_thresholding(expanded, max_iter, threshold)
    return expanded + ist


def upscale_channels(
    channels: cp.ndarray, upscale_factor: int, max_iter: int, threshold: float
) -> cp.ndarray:
    results = []
    for ch in channels.T:
        out = process_channel(ch, upscale_factor, max_iter, threshold)
        results.append(out)
        del ch, out
        cp.cuda.Stream.null.synchronize()
        cp.get_default_memory_pool().free_all_blocks()
        cp.fft.config.get_plan_cache().clear()
    return cp.column_stack(results)
