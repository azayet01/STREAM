The STREAM benchmark measures memory transfer rates in megabytes per second (MB/s) for four simple computational kernels. These kernels are designed to evaluate the performance of the memory subsystem by using large arrays and stressing memory bandwidth. The types of measurements performed by the program are based on the following four computational operations, each of which corresponds to a specific kernel:

1. **Copy**:
   - **Operation**: `c[j] = a[j]`
   - **Description**: This measures the rate at which data can be copied from one array to another. It involves moving data between two memory locations, stressing the memory bandwidth in a straightforward way by duplicating data from array `a` to array `c`.
   - **Memory Access Pattern**: Two memory accesses per element (one read from `a`, one write to `c`).
   - **Data Transfer**: 2 * sizeof(STREAM_TYPE) * STREAM_ARRAY_SIZE bytes.

2. **Scale**:
   - **Operation**: `b[j] = scalar * c[j]`
   - **Description**: This measures the rate of scaling the contents of an array by a constant value (`scalar`). The `Scale` operation involves a read, a multiplication, and a write, testing both memory and CPU arithmetic performance.
   - **Memory Access Pattern**: Two memory accesses per element (one read from `c`, one write to `b`), with one arithmetic operation.
   - **Data Transfer**: 2 * sizeof(STREAM_TYPE) * STREAM_ARRAY_SIZE bytes.

3. **Add**:
   - **Operation**: `c[j] = a[j] + b[j]`
   - **Description**: This kernel measures the rate of adding two arrays element by element and storing the result in a third array. It evaluates how fast data can be read from two locations and written to a third location, placing a heavier load on the memory subsystem due to the increased number of memory accesses.
   - **Memory Access Pattern**: Three memory accesses per element (two reads from `a` and `b`, one write to `c`).
   - **Data Transfer**: 3 * sizeof(STREAM_TYPE) * STREAM_ARRAY_SIZE bytes.

4. **Triad**:
   - **Operation**: `a[j] = b[j] + scalar * c[j]`
   - **Description**: This is a combination of the `Scale` and `Add` operations, where the contents of an array are scaled and added to another array. The `Triad` kernel is considered the most complex and stresses the memory subsystem with both arithmetic operations and multiple memory accesses.
   - **Memory Access Pattern**: Three memory accesses per element (one read from `b`, one read from `c`, one write to `a`), with two arithmetic operations (multiplication and addition).
   - **Data Transfer**: 3 * sizeof(STREAM_TYPE) * STREAM_ARRAY_SIZE bytes.

### Summary of Measurements:
- **Best Rate (MB/s)**: The highest observed bandwidth for each kernel, computed as the size of the data transferred divided by the minimum time taken for the operation.
- **Average Time**: The average time over all iterations (excluding the first iteration) for each kernel.
- **Minimum Time**: The shortest time observed for a particular kernel.
- **Maximum Time**: The longest time observed for a particular kernel.

These kernels are repeated `NTIMES` times, and the program reports the best result (i.e., the minimum time) for each kernel after discarding the first run. This approach helps to avoid performance fluctuations due to system startup or cache warming effects. The program uses arrays of size `STREAM_ARRAY_SIZE` (default: 10 million elements), which can be adjusted based on system cache size and memory capabilities.

In essence, the STREAM benchmark primarily measures **memory bandwidth** through these four kernels and reports how efficiently data can be transferred between different memory locations during common operations like copying, scaling, adding, and combining arrays.