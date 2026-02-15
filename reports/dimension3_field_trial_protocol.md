# DIMENSION 3: Field Trial Protocol & Methodology

**Author**: Abhishek Raj, IIT Patna  
**Date**: February 15, 2026

---

## Executive Summary

**Objective**: Validate UAV disease detection system in real Bihar farm conditions  
**Phases**: 3-phase protocol (controlled → pilot → scaled)  
**Timeline**: 12 months (kharif 2026 + rabi 2026-27)

---

## 1. Study Design

### 1.1 Research Questions

**RQ1**: Can thermal UAV detect maize disease 7-10 days earlier than visual symptoms?  
**RQ2**: Does early detection reduce economic loss for Bihar farmers?  
**RQ3**: Is the system usable by farmers with limited digital literacy?

### 1.2 Hypothesis

**H0**: UAV thermal detection has equal timing to visual scouting  
**H1**: UAV detects disease 7+ days earlier (p < 0.05, two-tailed t-test)

---

## 2. Phase 1: Controlled Trials (IIT Patna)

### 2.1 Location & Duration

- **Site**: IIT Patna experimental farm (1 ha)
- **Duration**: 1 season (90 days, kharif 2026)
- **Plots**: 20 plots × 50 m² (10 control, 10 infected)

### 2.2 Experimental Design

**Controlled Infection**:
- Inoculate 10 plots with *Exserohilum turcicum* spores (fungal blight)
- Density: 10⁵ spores/mL spray
- Timing: V6 growth stage (6 leaves)

**Data Collection**:
- Daily: Thermal images (7 AM, 2 PM)
- Every 3 days: Visual inspection by agronomist
- Weekly: Lab PCR confirmation (disease presence)

### 2.3 Metrics

- **Detection Lag**: Days (thermal alert) - Days (visual symptoms)
- **AI Accuracy**: True positive rate vs lab PCR
- **False Positive Rate**:Target <10%

**Expected Outcome**: Validate 7-10 day early detection claim

---

## 3. Phase 2: Pilot Trials (5 Farmers, Bihar)

### 3.1 Site Selection

**Districts**: Patna, Nalanda, Vaishali (high maize cultivation)

**Farm Criteria**:
- Size: 1-3 hectares
- Crop: Maize (hybrid varieties)
- History: Disease incidence in past 2 years
- Access: Road connectivity for equipment transport
-Farmer: Willing participant, literate (Hindi)

### 3.2 Farmer Recruitment

**Strategy**:
1. Partner with Bihar Agricultural University (BAU)
2. Krishi Vigyan Kendra (KVK) extension officers
3. Select 5 farmers (gender: 3 male, 2 female)

**Incentive**: ₹500/farmer + free disease diagnosis

### 3.3 Trial Protocol

**Pre-Season** (Week 0):
- Farmer training (4 hours): UAV operation, safety, data interpretation
- Install reference markers (GPS coordinates)
- Baseline soil + seed testing

**In-Season** (Weeks 1-12):
- **UAV flights**: 2× per week (Monday, Thursday)
- **Visual scouting**: 2× per week (same days, by farmer)
- **Lab testing**: Weekly PCR samples (suspicious areas)

**Post-Season** (Week 13):
- Yield measurement (tons/ha)
- Economic analysis (input costs vs revenue)
- Farmer feedback survey (25 questions, Hindi)

### 3.4 Data Collection Forms

**Field Data Sheet** (Hindi + English):

```
खेत निगरानी फॉर्म / Field Monitoring Form

किसान: _________ | Farmer: _________
तारीख: _________ | Date: _________

1. मौसम / Weather:
   [ ] धूप / Sunny  [ ] बादल / Cloudy  [ ] बारिश / Rain

2. फसल अवस्था / Crop Stage: V___ (पत्तियों की संख्या / Leaf count)

3. बीमारी के लक्षण (दिखाई देने वाले)?
   Disease Symptoms (Visible)?
   [ ] हाँ / Yes → विवरण: ___________
   [ ] नहीं / No

4. ड्रोन अलर्ट?
   Drone Alert?
   [ ] हाँ / Yes → स्थान: __________
   [ ] नहीं / No

5. दवा छिड़काव?
   Fungicide Application?
   [ ] हाँ / Yes → प्रकार: __________, मात्रा: __________
   [ ] नहीं / No
```

### 3.5 Annotation Interface

**For Building Training Dataset**:

**Web-Based Tool** (Tablet-compatible):
```
Image: [Thermal Image Display]

Annotation:
[ ] Healthy
[ ] Bacterial Wilt (तना गलन)
[ ] Fungal Blight (पत्ती झुलसा)
[ ] Rust (रतुआ)
[ ] Leaf Spot (पत्ती धब्बा)
[ ] Virus (वायरस)

Confidence:
( ) High (90-100%)
( ) Medium (70-89%)
( ) Low (<70%)

GPS: [Auto-filled]
Notes: [Text box]

[Save] [Next Image]
```

**Quality Control**:
- 3-person consensus (2 agronomists + 1 farmer)
- Inter-rater reliability: κ > 0.8

---

## 4. Phase 3: Scaled Validation (50 Farmers)

### 4.1 Expansion Strategy

**Timeline**: Rabi 2026-27 (after Phase 2 analysis)

**Clusters**:
- 5 clusters × 10 farmers
- Each cluster: 1 UAV operator (trained farmer)
- Service model: UAV-as-a-Service (₹500/ha)

### 4.2 Randomized Controlled Trial (RCT)

**Design**: 2-arm RCT

**Treatment Arm** (25 farmers):
- UAV disease monitoring
- Precision fungicide prescription

**Control Arm** (25 farmers):
- Traditional visual scouting
- Standard fungicide schedule

**Randomization**: Stratified by district (block randomization)

### 4.3 Primary Outcome

**Metric**: Yield (tons/ha)

**Hypothesis**: Treatment yield > Control yield by ≥10% (t-test, α=0.05)

### 4.4 Secondary Outcomes

- Fungicide cost (₹/ha)
- Disease incidence (% plots infected)
- Farmer satisfaction (Likert scale, 1-5)
- Adoption intention (Yes/No)

---

## 5. Data Management Plan

### 5.1 Data Types

1. **Aerial Imagery**: Thermal (.jpg), GPS metadata
2. **Ground Truth**: Visual scoring (0-5 severity scale)
3. **Lab Data**: PCR results (positive/negative)
4. **Yield Data**: Harvest weight (kg), moisture %
5. **Economic Data**: Input costs, market price

### 5.2 Storage & Security

**Local**: Encrypted Jetson Nano (AES-256)  
**Backup**: AWS S3 (India region, encrypted)  
**Access**: Password-protected, role-based

**Retention**: 10 years (research reproducibility)

### 5.3 Data Sharing

**Open Data** (upon PhD submission):
- Anonymized thermal images (3,000+)
- Disease annotations (CSV format)
- Metadata (weather, GPS, crop stage)

**Repository**: Zenodo (DOI minting) + GitHub

**License**: CC BY 4.0 (attribution required)

---

## 6. Quality Assurance

### 6.1 Calibration

**Thermal Camera**:
- Monthly: Blackbody calibration (±0.1°C accuracy)
- Pre-flight: Lens cleaning, dead pixel check

**GPS**:
- RTK base station for cm-level accuracy
- Multi-band GNSS (L1 + L5 frequencies)

### 6.2 Standard Operating Procedures (SOPs)

**SOP-001**: UAV Pre-Flight Checklist (15 items)  
**SOP-002**: Image Acquisition Protocol (altitude, overlap, lighting)  
**SOP-003**: Ground Truth Sampling (leaf collection, labeling)  
**SOP-004**: Data Upload & Backup (daily routine)

---

## 7. Statistical Analysis Plan

### 7.1 Sample Size Calculation

**Phase 2** (Pilot):
- n = 5 farmers (exploratory, not powered for significance)

**Phase 3** (RCT):
- Effect size: 10% yield improvement
- Power: 80% (β = 0.2)
- Significance: α = 0.05 (two-tailed)
- **Required**: n = 23 per arm → **25 per arm** (accounting for 10% dropout)

### 7.2 Analysis Methods

**Detection Lag**:
- Paired t-test (thermal vs visual detection days)
- Wilcoxon signed-rank test (non-parametric backup)

**Yield Comparison**:
- Independent t-test (treatment vs control)
- ANOVA (if >2 groups needed)

**Correlation**:
- Pearson's r (thermal signature vs disease severity)

**Software**: R 4.3, Python (SciPy, statsmodels)

---

## 8. Ethical Considerations

**IRB Approval**: IIT Patna Human Ethics Committee  
**Informed Consent**: Signed bilingual form  
**Farmer Compensation**: ₹500 + knowledge transfer  
**No Harm**: Control farmers receive post-study UAV service (1 season free)

---

## 9. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| UAV crash | Medium | High | Insurance, backup unit |
| Farmer dropout | Low | Medium | Regular engagement, incentives |
| Weather delays | High | Low | Extended timeline buffer |
| Disease non-occurrence | Low | High | Controlled Phase 1 validates system |

---

## 10. Dissemination Plan

**During Trials**:
- Monthly blog posts (IIT Patna website, Hindi)
- Farmer field days (demonstration flights)

**Post-Trials**:
- Conference: IEEE International Conference on Robotics and Automation (ICRA)
- Journal: Computers and Electronics in Agriculture (CAIE)
- Policy brief: Bihar Agricultural Department

---

## Conclusion

**Rigor**: 3-phase validation (controlled → pilot → RCT)  
**Scale**: 50 farmers, 2 seasons, multi-district  
**Data**: Open dataset (3,000+ images) for reproducibility

**Status**: ✅ COMPLETE (Protocol designed, awaiting execution)

**Word Count**: 890 words
