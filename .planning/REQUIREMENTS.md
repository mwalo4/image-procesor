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
| AIRM-01 | TBD | Pending |
| AIRM-02 | TBD | Pending |
| AIRM-03 | TBD | Pending |
| PROC-01 | TBD | Pending |
| PROC-02 | TBD | Pending |
| COMP-01 | TBD | Pending |

**Coverage:**
- v1 requirements: 6 total
- Mapped to phases: 0
- Unmapped: 6 ⚠️

---
*Requirements defined: 2026-02-25*
*Last updated: 2026-02-25 after initial definition*
