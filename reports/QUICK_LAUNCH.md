# 🚀 Quick Launch Guide

**Three Ways to Launch the Bihar Maiden Voyage**

---

## ⚡ FASTEST: Automated 3-Terminal Launcher (RECOMMENDED)

```bash
cd ~/thermal_hexacopter_project
bash scripts/master_launch.sh
```

**What happens:**
1. Prompts for screen recording (y/n)
2. Opens Terminal 1: Gazebo + PX4 (auto-waits 45s for boot)
3. Opens Terminal 2: Thermal AI Monitor (auto-waits 10s for init)
4. Opens Terminal 3: Survey Mission (executes immediately)
5. All terminals have visual progress indicators

**Perfect for:** First-time users, demos, PhD defense recording

---

## 🎯 ALTERNATIVE: Python Automation

```bash
cd ~/thermal_hexacopter_project
python3 scripts/master_fly.py --record --verbose
```

**Perfect for:** Headless execution, CI/CD, batch testing

---

## 🔧 MANUAL: Step-by-Step

See `docs/MISSION_COMMAND_CHEATSHEET.md` for complete manual instructions.

**Perfect for:** Debugging, learning, customization

---

## ✅ After Mission Completes

```bash
cd ~/thermal_hexacopter_project
git add .
git commit -m "feat: complete maiden voyage in Bihar world"
git tag -a v4.0-thesis-validated -m "Thesis validated"
```

---

**Status:** Ready for takeoff! 🚁🌾
