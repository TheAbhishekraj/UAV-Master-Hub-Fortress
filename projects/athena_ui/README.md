# 🎛️ Athena UI: Unified Flight Readiness Dashboard

The **Athena UI** is a world-class, React-based (Next.js/Vite) graphical command center designed specifically for the UAV Master Hub Fortress Architecture. It serves as the single "pane-of-glass" replacement for fragmented terminal diagnostics and standard QGroundControl telemetry, tailored for autonomous Phase 2 (GPS-Denied) operations.

## Features

The dashboard is structured into a 4-Quadrant tactical layout featuring premium glassmorphism, neon vector accents, and CSS-driven micro-animations:

- **Quad 1 (Inner Ear Diagnostic):** Live visual telemetry tracking absolute system stability. Features a dynamic Z-Variance confidence gauge, active state arrays for GNSS/VIO sensor fusion locks, and an animated ES-EKF IMU bias sparkline tracking system health at 400Hz.
- **Quad 2 (Auth Matrix):** A Go/No-Go array simulating real-world physical checklists. It visually polls power levels, multi-node synchronization, spoofing variance detection, and Geofence bounds before allowing the user to explicitly "Authorize Liftoff".
- **Quad 3 (Tactical Radar Map):** A deep, high-tech map representation of the A* sweep grid. Replaces simple lines with glowing vectors, a translucent Geofence bounds box, pulsing hit-markers for thermal anomalies, and a visualization of the 0.92% Positional Drift shell during simulated Electronic Warfare.
- **Quad 4 (Execution Pipeline):** Tracks total mission yield via tiered, animated gradient progress bars. Displays real-time tactical anomaly counts and features the glowing, high-contrast "Zeus Override" button for forcing an immediate Return-To-Launch via LiDAR retracing.

## Quick Start (Localhost Server)

Athena UI runs on Vite as a standalone React module:

```bash
cd projects/athena_ui
npm install
npm run dev -- --host
```

Once running, navigate to `http://localhost:5174/` or the provided local IP in your browser to view the Command Center!
