# Roadmap: Image Processor - White Product Detection Fix

## Overview

Two focused code fixes to `universal_processor.py` followed by regression validation. Phase 1 stops the flood-fill algorithm from bleeding into white product areas in non-AI mode. Phase 2 fixes rembg post-processing so white products are fully opaque and multi-product compositions are preserved. Phase 3 validates that all existing images still process correctly.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Flood-Fill Fix** - Stop background detection from bleeding into white product areas (non-AI mode)
- [ ] **Phase 2: AI Post-Processing Fix** - Correct rembg output so products are fully opaque and fully preserved
- [ ] **Phase 3: Regression Validation** - Confirm all previously-working images still process correctly

## Phase Details

### Phase 1: Flood-Fill Fix
**Goal**: White products in non-AI mode are cleanly separated from the #F3F3F3 background without bleed
**Depends on**: Nothing (first phase)
**Requirements**: PROC-01, PROC-02
**Success Criteria** (what must be TRUE):
  1. Processing the Natura Siberica test image in non-AI mode produces an output where white product surfaces are not eaten away by the flood-fill mask
  2. The output image shows all three products with their white areas intact and visually distinct from the #F3F3F3 background
  3. A product with white areas touching the image edge does not disappear or become partially transparent in the output
**Plans:** 1 plan

Plans:
- [ ] 01-01-PLAN.md — Strengthen flood-fill edge barrier with multi-signal detection + visual verification

### Phase 2: AI Post-Processing Fix
**Goal**: Rembg output is corrected so partially-alpha product pixels become fully opaque and no product in a multi-product composition is removed
**Depends on**: Phase 1
**Requirements**: AIRM-01, AIRM-02, AIRM-03
**Success Criteria** (what must be TRUE):
  1. Processing the Natura Siberica test image in AI mode produces an output where the tube and both boxes are visible with no ghosting (no semi-transparent product pixels)
  2. All three products in the multi-product composition appear in the output — none are removed by rembg post-processing
  3. The output contains no rembg artifacts (halos, partial cutouts, or missing product regions)
**Plans**: TBD

### Phase 3: Regression Validation
**Goal**: Every previously-working product photo continues to process identically after the Phase 1 and Phase 2 fixes
**Depends on**: Phase 2
**Requirements**: COMP-01
**Success Criteria** (what must be TRUE):
  1. A set of representative non-white-product images (dark products, colorful products) processed before and after the fix produce visually identical outputs
  2. No new artifacts appear in any test image after the fixes are applied
  3. Processing time per image remains within acceptable range (a few seconds)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Flood-Fill Fix | 0/1 | Planned | - |
| 2. AI Post-Processing Fix | 0/? | Not started | - |
| 3. Regression Validation | 0/? | Not started | - |
