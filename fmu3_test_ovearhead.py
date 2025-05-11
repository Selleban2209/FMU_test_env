import os
import sys
import time
import statistics
import psutil  # For proper memory measurement
from fmpy import read_model_description, extract
from fmpy.fmi3 import FMU3Slave
import logging

def benchmark_fmu(fmu_path, with_rtlola=True, runs=10):
    """Benchmark FMU execution with and without RTLola"""
    results = {
        'step_times': [],
        'total_time': [],
        'memory_usage': []
    }

    for _ in range(runs):
        start_time = time.perf_counter()
        process = psutil.Process()  

        # Setup FMU
        model_description = read_model_description(fmu_path)
        unzip_dir = extract(fmu_path)

        fmu = FMU3Slave(
            guid=model_description.guid,
            unzipDirectory=unzip_dir,
            modelIdentifier=model_description.coSimulation.modelIdentifier,
            instanceName="instance1",
        )
        vrs = {var.name: var.valueReference for var in model_description.modelVariables}
        fmu.instantiate(loggingOn=False)  # Disable logging for benchmarking

        if with_rtlola:
            fmu.setString([vrs['rtlola_spec']], ["specifications/bouncing_ball_spec.lola", "h"])

        # Initialize
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()

        # Simulation loop
        current_time = 0.0
        step_size = 1e-3
        stop_time =5.0
        step_times = []

        while current_time < stop_time - step_size:
            step_start = time.perf_counter()
            fmu.doStep(current_time, step_size)
            step_times.append(time.perf_counter() - step_start)

            #if with_rtlola:
               # _ = fmu.getString([vrs["rtlola_output"]])[0]  # Force RTLola processing

            current_time += step_size

        # Record results
        results['step_times'].extend(step_times)
        results['total_time'].append(time.perf_counter() - start_time)
        results['memory_usage'].append(process.memory_info().rss / 1024)  # KB

        fmu.terminate()
        fmu.freeInstance()

    return results

def analyze_overhead(baseline, rtlola_results):
    """Calculate overhead percentages"""
    metrics = {
        'avg_step_time': {
            'base': statistics.mean(baseline['step_times']) * 1000,  # Convert to ms
            'rtlola': statistics.mean(rtlola_results['step_times']) * 1000,
            'unit': 'ms'
        },
        'total_time': {
            'base': statistics.mean(baseline['total_time']),
            'rtlola': statistics.mean(rtlola_results['total_time']),
            'unit': 's'
        },
        'memory': {
            'base': statistics.mean(baseline['memory_usage']) / 1024,  # Convert to MB
            'rtlola': statistics.mean(rtlola_results['memory_usage']) / 1024,
            'unit': 'MB'
        }
    }

    for metric in metrics.values():
        metric['overhead_pct'] = ((metric['rtlola'] - metric['base']) / metric['base']) * 100

    return metrics

if __name__ == "__main__":
    regular_fmu = "fmus/BouncingBall.fmu"
    rtlola_fmu = "fmus_RTLola_FFI/BouncingBall.fmu"
    rtlola_fmu_ipc = "fmus_RTLola_IPC/BouncingBall.fmu"

    # Run benchmarks
    print("Running baseline (no RTLola)...")
    baseline = benchmark_fmu(regular_fmu, with_rtlola=False)

    print("Running with RTLola...")
    rtlola_results_ffi = benchmark_fmu(rtlola_fmu, with_rtlola=True)

   # print("Running with RTLola IPC...")
    #rtlola_results_ipc = benchmark_fmu(rtlola_fmu_ipc, with_rtlola=False)

    # Analyze results
    overhead = analyze_overhead(baseline, rtlola_results_ffi)

    print("\n=== Performance Overhead Analysis ===")
    print(f"{'Metric':<20} | {'Baseline':<10} | {'RTLola IPC':<10} | {'Overhead %':<10}")
    print("-" * 60)
    for name, data in overhead.items():
        print(f"{name.replace('_', ' ').title():<20} | "
              f"{data['base']:.4f}{data['unit']:<3} | "
              f"{data['rtlola']:.4f}{data['unit']:<3} | "
              f"{data['overhead_pct']:.2f}%")
