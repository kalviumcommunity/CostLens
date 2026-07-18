# LU-20 GroupBy Aggregation & Segment Insights

## 1. Executive Summary
This report analyzes cloud operational data using categorical groupings, pivot tables, and cross-tabulations to extract actionable business segments. By breaking down costs, incidents, and deployments by Team, Environment, and Service, we expose the underlying drivers of our cloud metrics.

### Key Business Insights
- The Backend team contributes 48.3% of total cloud spending.
- The Production environment accounts for 43.0% of incidents.
- The Payments service has the highest average deployment frequency.

---

## 2. Team Analysis
The `Backend` team is historically our largest consumer of cloud resources.
The top 3 highest cost teams are:
- **Backend**: $544,354.78 (1445 incidents)
- **Data**: $176,627.23 (540 incidents)
- **Frontend**: $150,285.38 (460 incidents)

## 3. Environment Analysis
- **Dev**: Total Cost = $294,673.79 | Avg Incidents = 1.27
- **Production**: Total Cost = $624,224.15 | Avg Incidents = 2.32
- **Staging**: Total Cost = $208,901.75 | Avg Incidents = 1.32

## 4. Service Analysis
- **Top Incident Generating Service**: Notification (496 incidents)
- **Best Performing Service (Lowest Incidents)**: Payments (412 incidents)

## 5. Top & Bottom Performers (Teams by Cost)
### Top 5 Highest Cost Teams
| team     |   Total_Cloud_Cost |
|:---------|-------------------:|
| Backend  |           544355   |
| Data     |           176627   |
| Frontend |           150285   |
| Mobile   |            92924.6 |
| DevOps   |            85937.3 |

### Top 5 Lowest Cost Teams
| team     |   Total_Cloud_Cost |
|:---------|-------------------:|
| Security |            77670.4 |
| DevOps   |            85937.3 |
| Mobile   |            92924.6 |
| Frontend |           150285   |
| Data     |           176627   |

## 6. Recommendations
1. Investigate Backend team resource allocation to identify optimization opportunities.
2. Review deployment practices and QA processes in the production environment.
3. Optimize high-cost services associated with the Backend team.
