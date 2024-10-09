import subprocess
import json
import re
from itertools import product
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Regex pattern to extract the performance data from the output
stream_output_pattern = r"(Copy|Scale|Add|Triad):\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"

# Run a command and return its output
def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Detect available NUMA nodes using numactl --hardware
def detect_numa_nodes():
    numa_nodes = []
    try:
        # Run numactl --hardware to get NUMA node information
        numactl_output = run_command("numactl --hardware")

        # Extract NUMA node numbers from the output
        node_pattern = re.compile(r"available:\s(\d+)\snodes\s\((\d+-\d+)\)")
        node_match = node_pattern.search(numactl_output)
        if node_match:
            start_node, end_node = map(int, node_match.group(2).split('-'))
            numa_nodes = list(range(start_node, end_node + 1))
    except Exception as e:
        print(f"Error using numactl to detect NUMA nodes: {e}")
        return [0]  # Default to NUMA node 0 if detection fails
    return numa_nodes

# Run the STREAM benchmark with numactl and collect output
def run_stream(cpu_node, mem_node):
    command = f"numactl --cpunodebind={cpu_node} --membind={mem_node} stream"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Parse the output from STREAM benchmark
def parse_stream_output(output):
    results = {}
    matches = re.findall(stream_output_pattern, output)
    for match in matches:
        function, best_rate, avg_time, min_time, max_time = match
        results[function] = {
            "Best Rate MB/s": float(best_rate),
            "Avg Time (s)": float(avg_time),
            "Min Time (s)": float(min_time),
            "Max Time (s)": float(max_time)
        }
    return results

# Create a table for each function (Copy, Scale, Add, Triad)
def generate_performance_table(all_results, function):
    # Initialize table (rows for CPU nodes, columns for memory nodes)
    numa_nodes = sorted(list(set([result["CPU Node"] for result in all_results])))
    table = pd.DataFrame(index=numa_nodes, columns=numa_nodes)

    # Populate the table with the best MB/s results
    for result in all_results:
        cpu_node = result["CPU Node"]
        mem_node = result["Memory Node"]
        if function in result["Results"]:
            best_rate = result["Results"][function]["Best Rate MB/s"]
            table.loc[cpu_node, mem_node] = best_rate

    # Infer object types to proper numeric types and replace NaN values
    table = table.infer_objects(copy=False).fillna(0)

    return table

# Generate and save heatmap with seaborn
def save_heatmap(table, function_name):
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        table,
        annot=True, fmt=".2f", cmap="RdYlGn_r",  # 'RdYlGn_r' goes from red to green
        linewidths=.5, square=True
    )
    plt.title(f"{function_name} Memory Performance Heatmap (MB/s)")
    plt.ylabel('CPU Node')
    plt.xlabel('Memory Node')
    plt.savefig(f"{function_name}_performance_heatmap.png")  # Save the figure to a file
    plt.close()  # Close the figure to free memory

# Colorize value with ANSI colors based on range
def colorize_value(value, min_val, max_val):
    normalized = (value - min_val) / (max_val - min_val)
    if normalized < 0.33:
        return f"\033[92m{value:.2f}\033[0m"  # Green for low values
    elif normalized < 0.66:
        return f"\033[93m{value:.2f}\033[0m"  # Yellow for medium values
    else:
        return f"\033[91m{value:.2f}\033[0m"  # Red for high values

# Print table with colored values for console
def print_colored_table(table):
    min_val = table.min().min()
    max_val = table.max().max()

    print("\nMemory Performance Table (MB/s):\n")
    for row in table.index:
        row_data = []
        for col in table.columns:
            val = table.loc[row, col]
            if pd.isna(val):
                row_data.append(f"  -  ")
            else:
                row_data.append(colorize_value(val, min_val, max_val))
        print(f"{row}: {' | '.join(row_data)}")

# Main function to run tests for all CPU and memory node combinations
def main():
    # Detect available NUMA nodes
    numa_nodes = detect_numa_nodes()
    print(f"Detected NUMA nodes: {numa_nodes}")

    all_results = []
    baseline_result = None

    # Iterate over all combinations of CPU and memory nodes
    for cpu_node, mem_node in product(numa_nodes, repeat=2):
        print(f"Running STREAM with CPU node {cpu_node} and Memory node {mem_node}")
        output = run_stream(cpu_node, mem_node)
        results = parse_stream_output(output)

        # Store results along with the configuration
        test_result = {
            "CPU Node": cpu_node,
            "Memory Node": mem_node,
            "Results": results
        }
        all_results.append(test_result)

        # If it's the baseline (same CPU and memory node), store it for ratio calculation
        if cpu_node == 0 and mem_node == 0:
            baseline_result = results

    # Generate tables for each function
    functions = ["Copy", "Scale", "Add", "Triad"]
    tables = {}
    for function in functions:
        table = generate_performance_table(all_results, function)
        tables[function] = table

        # Save the heatmap to a file
        save_heatmap(table, function)

        # Print the table with ANSI color output in console
        print_colored_table(table)

    # Output results to JSON format
    with open("stream_performance_results.json", "w") as f:
        json.dump(all_results, f, indent=4)

    print("Performance results saved to 'stream_performance_results.json'.")

if __name__ == "__main__":
    main()
