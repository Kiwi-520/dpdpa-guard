# dpdpa-guard

A developer-focused **DPDPA compliance engine** that scans data for personal information and generates actionable compliance reports.

## Pipeline

Input
↓
1. Source
↓
2. Detection
↓
3. Normalisation
↓
4. Purpose Inference
↓
5. DPDPA Knowledge Engine
↓
6. Linkage Risk
↓
7. Cross-Module Integration
↓
8. Reporter
↓
Compliance Report

## What it does

- Detects Indian PII using Presidio and custom recognizers.
- Normalises detected entities into a common taxonomy.
- Maps detected data to DPDPA requirements.
- Identifies purpose mismatches and linkage risks.
- Checks consent and retention requirements.
- Generates compliance reports.

## Goal

Turn raw data into an actionable **DPDPA compliance report**.