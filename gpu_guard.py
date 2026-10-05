import subprocess


MIN_FREE_VRAM_MIB = 6200
MAX_CPU_USAGE_PERCENT = 50
MAX_GPU_USAGE_PERCENT = 30


def get_system_resources():
    """
    Return current GPU VRAM, CPU usage, and GPU usage.

    Returns None if the required system information cannot
    be obtained.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.free,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (
        FileNotFoundError,
        subprocess.SubprocessError,
        OSError,
    ):
        return None

    lines = [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    try:
        gpu_values = [
            int(value.strip())
            for value in lines[0].split(",")
        ]
    except ValueError:
        return None

    if len(gpu_values) != 2:
        return None

    free_vram_mib = gpu_values[0]
    gpu_usage_percent = gpu_values[1]

    try:
        cpu_result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_Processor | "
                "Measure-Object -Property LoadPercentage -Average).Average",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (
        FileNotFoundError,
        subprocess.SubprocessError,
        OSError,
    ):
        return None

    cpu_output = cpu_result.stdout.strip()

    try:
        cpu_usage_percent = float(cpu_output)
    except ValueError:
        return None

    return {
        "free_vram_mib": free_vram_mib,
        "cpu_usage_percent": cpu_usage_percent,
        "gpu_usage_percent": gpu_usage_percent,
    }


def require_system_resources():
    """
    Raise RuntimeError if the system does not appear idle enough
    to safely start the LLM.

    This fails closed if system resource information cannot
    be obtained.
    """
    resources = get_system_resources()

    if resources is None:
        raise RuntimeError(
            "Could not determine current system resource usage. "
            "Refusing to start the LLM."
        )

    free_vram_mib = resources["free_vram_mib"]
    cpu_usage_percent = resources["cpu_usage_percent"]
    gpu_usage_percent = resources["gpu_usage_percent"]

    if free_vram_mib < MIN_FREE_VRAM_MIB:
        raise RuntimeError(
            f"Only {free_vram_mib:,} MiB of GPU VRAM is free; "
            f"{MIN_FREE_VRAM_MIB:,} MiB is required. "
            "Refusing to start the LLM."
        )

    if cpu_usage_percent >= MAX_CPU_USAGE_PERCENT:
        raise RuntimeError(
            f"CPU usage is {cpu_usage_percent:.1f}%; "
            f"maximum allowed is below "
            f"{MAX_CPU_USAGE_PERCENT}%. "
            "Refusing to start the LLM."
        )

    if gpu_usage_percent >= MAX_GPU_USAGE_PERCENT:
        raise RuntimeError(
            f"GPU usage is {gpu_usage_percent}%; "
            f"maximum allowed is below "
            f"{MAX_GPU_USAGE_PERCENT}%. "
            "Refusing to start the LLM."
        )

    return resources