# Literature Audit: Resilient Autonomous UAV Systems in Precision Agriculture

## 1. Introduction and Context
Precision Agriculture (PA) has increasingly relied on Unmanned Aerial Vehicles (UAVs) equipped with multispectral and thermal sensors for crop health monitoring. However, contemporary PA systems are overwhelmingly GNSS-dependent. In environments such as the riverine "Diara" lands of Munger, Bihar, operations frequently encounter GPS-shadows due to dense riparian vegetation, tall crop canopies, and distinct topographical features.

## 2. Review of Existing Tracking and Estimation Techniques
Existing literature extensively covers Visual-Inertial Odometry (VIO) and traditional Extended Kalman Filters (EKF) for state estimation in GPS-denied environments (e.g., S. Weiss et al., 2012; Leutenegger et al., 2015). 
While these systems perform well in structured, rigid environments, they face significant degradation in agricultural settings. 
- **The Visual Noise Problem:** High-humidity environments, such as Bihar's maize fields during the monsoon, induce camera lens fogging and severe glare. Furthermore, the non-rigid, swaying nature of tall maize plants introduces massive outliers in visual feature tracking, overwhelming standard VIO pipelines.

## 3. The Gap in Autonomous Thermal Monitoring
Thermal stress detection methodologies are often "dumb" in their autonomy—existing research predominantly treats the UAV as a passive data-collection platform that follows pre-programmed GNSS waypoints. When the "stars" (satellites) go dark, these platforms either initiate an emergency landing or drift unpredictably.
There is a critical literature gap regarding **active, real-time path planning coupled with robust state estimation** specifically designed for high-heat, high-humidity, GPS-degraded agricultural canopies.

## 4. Path Planning in Dynamic Agricultural Environments
Standard heuristic searches like Dijkstra or basic $A^*$ are well-documented for static obstacle avoidance (Hart et al., 1968). However, applying $A^*$ in a dynamic agricultural field requires an context-aware cost function $f(n) = g(n) + h(n)$ that respects crop rows and dynamic farm machinery (e.g., tractors). Most current literature fails to integrate real-time spatial heuristics with non-GNSS state estimators in a resource-constrained UAV compute environment.

## 5. Conclusion: Filling the Gap with Fortress v4.0
This dissertation directly addresses these gaps by introducing the **Indra-Eye** system. By operating an Error-State Kalman Filter (ES-EKF) on the $SO(3)$ manifold, the system guarantees attitude stability without gimbal lock during aggressive wind-correction maneuvers common in the Diara region. Coupled with a dynamically optimized $A^*$ path planner and a decoupled V5 Mission Commander, this research presents a paradigm shift from passive observation to resilient, autonomous, and active precision agriculture.
