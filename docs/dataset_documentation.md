# Dataset documentation template

Complete this document with actual sources before training or presenting.

## Required provenance CSV

Each incoming source folder may contain `provenance.csv`:

```csv
relative_path,group_id,source,license,generator,original_url,notes
real/example.jpg,real-family-001,Example Photo Source,LICENSE,none,https://...,original photograph
ai_generated/example.png,ai-family-001,Example Generator Set,LICENSE,Generator Name,https://...,prompt retained separately
```

`group_id` must be shared by every related version of one underlying image. It is the key leakage-control field.

## Source register

| Stage | Source | Class | Count | License | URL | Access date | In train? | In OOD? |
|---|---|---:|---:|---|---|---|---|---|
| Original | To be completed | - | - | - | - | - | - | - |
| Expanded | To be completed | - | - | - | - | - | - | - |
| OOD | To be completed | - | - | - | - | - | No | Yes |

## Improvement checklist

- Multiple independent AI generator families.
- Multiple photographic source families.
- Balanced classes and documented source mix.
- Diverse subjects, styles, resolutions, lighting, and compression.
- Invalid and tiny images removed.
- Exact duplicates removed; near-duplicate review recorded.
- Train-only variants retain family group IDs.
- Licenses allow the intended academic use.
- People and sensitive content handled ethically.

The preparation script writes an immutable manifest and a preparation report. The reporting script calculates counts, dimensions, source distribution, duplicate count, and missing provenance from actual files.

