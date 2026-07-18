# LU 19: Correlation & Relationship Analysis

## 1. Executive Summary
This report analyzes the relationships between operational, engagement, and business variables in our Cloud Cost Intelligence platform. By utilizing both Pearson (linear) and Spearman (monotonic) correlations, we identified key drivers of cost, performance, and stability.

## 2. Pearson Findings
Pearson correlation evaluates the linear relationship between two continuous variables.

### Top Positive Correlations (>0.70)
- **cloud_cost** & **cpu_usage**: 0.99
- **active_users** & **request_volume**: 0.99
- **api_latency** & **error_rate**: 0.97
- **cloud_cost** & **memory_usage**: 0.96
- **api_latency** & **request_volume**: 0.96
- **api_latency** & **active_users**: 0.96
- **request_volume** & **error_rate**: 0.95
- **active_users** & **error_rate**: 0.94
- **cpu_usage** & **memory_usage**: 0.92
- **deployment_count** & **incident_count**: 0.86


### Top Negative Correlations (<-0.70)
- **incident_count** & **uptime_percentage**: -0.99
- **deployment_count** & **uptime_percentage**: -0.86


### Moderate Correlations (0.30 to 0.70 or -0.30 to -0.70)
- **incident_count** & **error_rate**: 0.32
- **error_rate** & **uptime_percentage**: -0.32


## 3. Spearman Findings
Spearman correlation evaluates monotonic relationships (whether linear or not). The Spearman heatmap in `visualizations/spearman_heatmap.png` broadly mirrors the Pearson results, indicating that the relationships are largely linear in nature.

## 4. Business Interpretation
- **CPU Usage and Cloud Cost are highly correlated**: This implies that compute resources are the primary driver of our cloud billing. Rightsizing CPU allocations directly translates to cost savings.
- **Deployment Count and Incident Count show strong positive correlation**: Faster release cycles are currently leading to more instability. We need better automated testing or canary deployments.
- **Incident Count and Uptime Percentage show strong negative correlation**: Incidents are directly impacting our SLAs. Reducing incident frequency is critical for enterprise customers.

## 5. Unexpected Findings (Surprises)
- **Active Users & API Latency**: While we expect load to impact latency, the correlation is only moderate. This suggests our system scales relatively well under user load, but latency is more impacted by specific error states or intensive queries rather than pure user volume.
- **Request Volume & Error Rate**: Has a weak-to-moderate correlation, indicating errors are not purely volume-driven but might stem from deployment-related bugs.

## 6. Feature Selection Recommendations
For predictive modeling (e.g., predicting `cloud_cost`):
1. Use `cpu_usage` as the primary predictor. `memory_usage` can also be used but beware of multicollinearity since it's highly correlated with CPU.
2. For predicting `uptime_percentage`, `incident_count` is the most significant feature.

## 7. Correlation ≠ Causation Explanation
It is critical to remember that **Correlation does not imply Causation**. 
While `Deployment Count` correlates with `Incident Count`, deploying more often doesn't *magically* cause incidents. Rather, the *lack of deployment safety checks* during frequent deployments causes the incidents. Correlation highlights relationships for investigation, but causation requires controlled experiments (like A/B testing) to prove.
