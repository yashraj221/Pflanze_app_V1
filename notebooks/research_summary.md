# Pflanze — Pathogen Bioinformatics Analysis Report

**Generated:** 2026-02-24 10:34 UTC
**Script:** `notebooks/pathogen_analysis.py`
**Data source:** NCBI Nucleotide (via Biopython Entrez API)

---

## Summary Table

| Pathogen | Accession | Length (bp) | GC% | Crop | Disease | NDVI Score | Risk Zone |
|---|---|---|---|---|---|---|---|
| Tobacco Mosaic Virus | NC_001497 | 8,024 | 39.97 | Tomato/Tobacco | Mosaic Disease | 0.58 | Fair Health |
| Rice Blast Fungus | NC_017850 | N/A | N/A | Rice | Rice Blast | 0.69 | Moderate Stress |
| Potato Late Blight | NC_015247 | 16,477 | 36.9 | Potato/Tomato | Late Blight | 0.75 | Moderate Stress |
| Wheat Stripe Rust | NC_014069 | 3,690 | 53.55 | Wheat | Stripe Rust | 0.62 | Moderate Stress |

---

## NDVI Formula

```
NDVI = (NIR - Red) / (NIR + Red)
```

| NDVI Range | Interpretation |
|---|---|
| < 0.2 | Bare soil / severe stress |
| 0.2 – 0.4 | Sparse / stressed vegetation |
| 0.4 – 0.6 | Moderate, fair-health vegetation |
| > 0.6 | Dense, healthy vegetation |

---

## Pathogen Details

### Tobacco Mosaic Virus

- **Accession:** NC_001497
- **Organism:** Cauliflower mosaic virus
- **Taxonomy:** Viruses > Riboviria > Pararnavirae > Artverviricota
- **Sequence Length:** 8,024 bp
- **GC Content:** 39.97%
- **Associated Crop:** Tomato/Tobacco
- **Disease:** Mosaic Disease
- **NDVI Correlation Score:** 0.58
- **Risk Zone:** Fair Health
- **Description:** A (+)ssRNA plant virus that causes mosaic discoloration and stunted growth. One of the most widely studied plant viruses.

### Rice Blast Fungus

- **Accession:** NC_017850
- **Organism:** Unknown
- **Taxonomy:** N/A
- **Sequence Length:** N/A
- **GC Content:** N/A
- **Associated Crop:** Rice
- **Disease:** Rice Blast
- **NDVI Correlation Score:** 0.69
- **Risk Zone:** Moderate Stress
- **Description:** Magnaporthe oryzae causes rice blast, the most destructive fungal disease of rice, responsible for significant yield losses globally.

### Potato Late Blight

- **Accession:** NC_015247
- **Organism:** Odocoileus virginianus
- **Taxonomy:** Eukaryota > Metazoa > Chordata > Craniata
- **Sequence Length:** 16,477 bp
- **GC Content:** 36.9%
- **Associated Crop:** Potato/Tomato
- **Disease:** Late Blight
- **NDVI Correlation Score:** 0.75
- **Risk Zone:** Moderate Stress
- **Description:** Phytophthora infestans is an oomycete responsible for the Irish Potato Famine (1840s) and remains a major threat to solanaceous crops.

### Wheat Stripe Rust

- **Accession:** NC_014069
- **Organism:** Torque teno virus 4
- **Taxonomy:** Viruses > Monodnaviria > Shotokuvirae > Commensaviricota
- **Sequence Length:** 3,690 bp
- **GC Content:** 53.55%
- **Associated Crop:** Wheat
- **Disease:** Stripe Rust
- **NDVI Correlation Score:** 0.62
- **Risk Zone:** Moderate Stress
- **Description:** Puccinia striiformis f.sp. tritici causes yellow stripe rust on wheat, reducing grain yield by up to 70% under epidemic conditions.

---

## References

- Rouse, J.W. et al. (1974). Monitoring vegetation systems in the Great Plains with ERTS.
- Hughes, D.P. & Salathé, M. (2015). An open access repository of images on plant health.
- Mohanty, S.P. et al. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419.
- NCBI Nucleotide Database: https://www.ncbi.nlm.nih.gov/nucleotide/
