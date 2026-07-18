# LU-17: NumPy Vectorised Computation Workflow

## 1. Vectorisation Explanation
In data analysis, **vectorisation** refers to the process of executing operations on entire arrays (or "vectors") at once, rather than iterating through elements one-by-one. Under the hood, libraries like NumPy implement these operations in highly optimised C code. This eliminates the overhead of Python's `for` loops and type-checking on each element. It allows modern CPUs to leverage SIMD (Single Instruction, Multiple Data) instructions, processing multiple data points simultaneously.

## 2. Loop vs NumPy Comparison
In our cloud cost metrics dataset, calculating the Infrastructure Risk Score involved computing a weighted sum based on CPU utilization, memory utilization, incident counts, and deployment counts.

**Traditional Loop Approach (Pandas `iterrows`):**
In this method, we iterate row-by-row using Python's `for` loop. This is exceptionally slow because Python is an interpreted language and processes each iteration individually.

**NumPy Vectorised Approach:**
By extracting the columns into NumPy arrays (`.to_numpy()`), we apply the mathematical formula on the entire arrays in a single line. The underlying C implementation executes the operation across the entire dataset almost instantly.

## 3. Performance Benchmark
We ran a benchmark on a simulated dataset of 100,000 projects to compare both methods for calculating the Infrastructure Risk Score.

| Method | Execution Time (s) | Speed Improvement |
|---|---|---|
| Loop (`iterrows`) | ~1.27s | 1x |
| NumPy Vectorisation | ~0.0016s | **~773.81x** |

**Conclusion**: NumPy is over 770 times faster than a traditional Python for-loop when processing 100k records, demonstrating the critical importance of vectorization for scaling data engineering workflows.

## 4. Normalization Explanation
Normalization is a technique used to scale numeric data into a standard range. For the Risk Score, we used **Min-Max Normalization** to compress the scores into a range between `0` and `1`.
Formula: `(value - min) / (max - min)`
This makes it much easier to compare risk levels across different projects and creates a bounded output which is commonly required for machine learning models or standardized dashboard metrics.

## 5. Ranking Explanation
Using NumPy's array sorting capabilities, we ranked the projects based on their Infrastructure Risk Score, with Rank 1 assigned to the highest risk project. Instead of an expensive Python sort, we used `argsort()` on the negative scores (to sort in descending order) to swiftly establish a ranked index for the entire array.

## 6. Business Insights
* **Scalability**: As the Cloud Cost Intelligence platform scales to millions of projects, loop-based calculations would become a bottleneck. Vectorization ensures that risk scoring remains instantaneous regardless of dataset size.
* **Proactive Risk Mitigation**: By ranking projects and bounding scores between 0 and 1, stakeholders can quickly identify the top tier of risky projects (e.g., those ranked 1-10 or with a normalized score > 0.8) and prioritize infrastructure optimization or incident mitigation.
* **Resource Efficiency**: Faster computations reduce the runtime of our data pipelines. This directly translates to lower compute costs for running our data workflows, perfectly aligning with the overarching goal of a Cloud Cost Intelligence platform.
