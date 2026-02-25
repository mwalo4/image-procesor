# Requirements: Image Processor - White Product Detection Fix

**Defined:** 2026-02-25
**Core Value:** Produktové fotky musí mít všechny produkty kompletně zachované a čistě zobrazené na cílovém pozadí

## v1 Requirements

### AI Background Removal

- [ ] **AIRM-01**: When rembg gives partial alpha (<128) to product pixels, those pixels must be treated as fully opaque product (no ghosting)
- [ ] **AIRM-02**: When rembg removes product areas that flood-fill considers product, the system must fall back cleanly (no artifacts, no duchové)
- [ ] **AIRM-03**: AI removal must not crop off products from multi-product compositions

### Non-AI Processing

- [ ] **PROC-01**: Flood-fill background detection must not bleed into white product areas that touch the image edge
- [ ] **PROC-02**: White products must be visually distinct from #F3F3F3 background (not blend/disappear)

### Compatibility

- [ ] **COMP-01**: Existing product photos that process correctly (99%+ of images) must continue to work without degradation

## v2 Requirements

(None — this is a focused bug fix)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Changing rembg model | Black-box AI, we control post-processing only |
| Changing target background color | #F3F3F3 is a business requirement |
| New processing features | Bug fix only, no feature additions |
| Training custom AI model | Out of scope for this fix |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROC-01 | Phase 1 | Pending |
| PROC-02 | Phase 1 | Pending |
| AIRM-01 | Phase 2 | Pending |
| AIRM-02 | Phase 2 | Pending |
| AIRM-03 | Phase 2 | Pending |
| COMP-01 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 6
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-25*
*Last updated: 2026-02-25 after roadmap creation*
