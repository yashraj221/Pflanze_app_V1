# Pflanze Bioinformatics Pipeline

**Document:** Technical Architecture of the Bioinformatics Integration Layer
**Part of:** Pflanze Crop Monitoring Platform
**Author:** Yashraj

---

## Overview

The Pflanze bioinformatics pipeline bridges three distinct data domains:

1. **Phenotypic** — Visual disease symptoms captured by mobile camera
2. **Spectral** — Satellite-derived NDVI vegetation stress indices
3. **Genomic** — Pathogen nucleotide sequences from NCBI

By integrating these domains, the system provides multi-scale crop health intelligence ranging from field-level stress mapping down to molecular characterization of disease-causing organisms.

---

## Architecture: How the Bioinformatics Layer Integrates with the App

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PFLANZE INTEGRATED ARCHITECTURE                      │
├──────────────────────┬──────────────────────────┬───────────────────────────┤
│  FRONTEND (index.html│  BIOINFORMATICS MODULE   │  EXTERNAL DATA SOURCES    │
│  Browser / Mobile)   │  (Python / Biopython)    │                           │
├──────────────────────┼──────────────────────────┼───────────────────────────┤
│                      │                          │                           │
│  ┌────────────────┐  │  ┌────────────────────┐  │  ┌─────────────────────┐  │
│  │ NDVI Map Layer │◀─┼──│ compute_ndvi()     │  │  │ Sentinel-2 L2A      │  │
│  │ (Leaflet.js)   │  │  │ NDVI = (NIR-Red)/  │  │  │ (ESA Copernicus)    │  │
│  └────────────────┘  │  │       (NIR+Red)    │  │  │ NASA GIBS Tiles     │  │
│                      │  └────────────────────┘  │  └─────────────────────┘  │
│  ┌────────────────┐  │                          │                           │
│  │ Disease        │  │  ┌────────────────────┐  │  ┌─────────────────────┐  │
│  │ Detection UI   │──┼─▶│ analyze_pathogen() │──┼─▶│ NCBI Nucleotide     │  │
│  │ (Plant.ID +    │  │  │ NCBI Entrez fetch  │  │  │ (Biopython Entrez)  │  │
│  │  Crop.Health)  │  │  └────────────────────┘  │  └─────────────────────┘  │
│  └────────────────┘  │                          │                           │
│                      │  ┌────────────────────┐  │  ┌─────────────────────┐  │
│  ┌────────────────┐  │  │ correlate_disease  │  │  │ PlantVillage        │  │
│  │ Weather Module │  │  │ _ndvi()            │  │  │ (Reference classes) │  │
│  │ (OpenWeather)  │  │  └────────────────────┘  │  └─────────────────────┘  │
│  └────────────────┘  │                          │                           │
│                      │  ┌────────────────────┐  │  ┌─────────────────────┐  │
│                      │  │ generate_summary   │  │  │ OpenWeatherMap API  │  │
│                      │  │ _report()          │──┼─▶│ iNaturalist         │  │
│                      │  └────────────────────┘  │  └─────────────────────┘  │
└──────────────────────┴──────────────────────────┴───────────────────────────┘
```

---

## Step-by-Step Pipeline Description

### Step 1: Image Capture

**Component:** `index.html` — Disease Detection Tab

The user photographs plant symptoms using their mobile device or uploads an existing image. The image is encoded as Base64 and submitted to the Kindwise Plant.ID API.

```
[User Camera / File Upload]
          │
          ▼
[Base64 encode image]
          │
          ▼
[POST → Plant.ID API]  →  Species identification + confidence score
[POST → Crop.Health API] →  Disease predictions ranked by probability
```

---

### Step 2: Disease API Analysis

**APIs:** Plant.ID (Kindwise), Crop.Health (Kindwise), Groq AI (Llama-3)

The disease detection pipeline returns a ranked list of probable diseases. Groq AI synthesizes the top predictions into a natural-language explanation with treatment recommendations:

```
[Plant.ID API Response]
  → plant_name, probability[]

[Crop.Health API Response]
  → disease_name[], confidence[]

[Groq AI Prompt]
  → "Analyze these disease predictions for <plant>: <diseases>"
  → Severity assessment + Treatment plan + Prevention advice
```

---

### Step 3: Pathogen Mapping

**Script:** `notebooks/pathogen_analysis.py` — `PATHOGEN_SEQUENCES` dict

The detected disease name is mapped to a corresponding pathogen NCBI accession ID using the `PATHOGEN_SEQUENCES` dictionary:

```python
PATHOGEN_SEQUENCES = {
    "Tobacco Mosaic Virus":  {"id": "NC_001497", "crop": "Tomato/Tobacco", "disease": "Mosaic Disease"},
    "Rice Blast Fungus":     {"id": "NC_017850", "crop": "Rice",           "disease": "Rice Blast"},
    "Potato Late Blight":    {"id": "NC_015247", "crop": "Potato/Tomato",  "disease": "Late Blight"},
    "Wheat Stripe Rust":     {"id": "NC_014069", "crop": "Wheat",          "disease": "Stripe Rust"},
}
```

---

### Step 4: NCBI Sequence Fetch

**Library:** Biopython — `Bio.Entrez.efetch()`

For each mapped pathogen, the script fetches the GenBank record from NCBI:

```python
handle = Entrez.efetch(db="nucleotide", id=accession, rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
```

The GenBank record contains:
- Full nucleotide sequence
- Organism name and complete taxonomic lineage
- Feature annotations (genes, CDS, regulatory elements)
- Literature cross-references

---

### Step 5: GC Content & Taxonomy Analysis

**Functions:** `gc_fraction()` from `Bio.SeqUtils`

```python
gc_pct  = gc_fraction(record.seq) * 100      # → e.g., 44.13%
taxonomy = record.annotations["taxonomy"]     # → ["Viruses", "Riboviria", ...]
seq_len  = len(record.seq)                    # → e.g., 6395 bp
```

**Why GC content matters:**
- High GC% (>55%) often indicates organisms adapted to higher temperatures or with more stable secondary structures
- GC% differences between host and pathogen DNA are used in horizontal gene transfer studies
- Fungal pathogens (*M. oryzae*, ~52% GC) differ markedly from RNA viruses (TMV, ~44% GC)

---

### Step 6: NDVI Correlation

**Function:** `correlate_disease_ndvi()` in `notebooks/pathogen_analysis.py`

NDVI values observed in disease-affected fields are associated with each pathogen:

```
ndvi_correlation_score = 1.0 − observed_ndvi

Disease severity         Low NDVI    High correlation score
─────────────────────────────────────────────────────────────
Late Blight (severe)      0.25           0.75  ← High risk
Rice Blast (significant)  0.31           0.69
Stripe Rust (moderate)    0.38           0.62
Mosaic Disease (mild)     0.42           0.58
```

This creates a quantitative link: *lower NDVI in a field → higher pathogen risk indicator*.

---

### Step 7: Output Generation

Two output files are written:

**`data/pathogen_database.json`**
```json
{
  "generated_at": "2026-02-22T...",
  "source": "NCBI Nucleotide via Biopython Entrez API",
  "total_pathogens": 4,
  "pathogens": [...]
}
```

**`notebooks/research_summary.md`**
A formatted Markdown report with a summary table, NDVI interpretation table, per-pathogen details, and references — suitable for inclusion in research documentation.

---

## ASCII Pipeline Diagram (Compact)

```
Camera/Upload
    │
    ▼
Plant.ID + Crop.Health API
    │  disease_name
    ▼
PATHOGEN_SEQUENCES mapping
    │  accession_id
    ▼
NCBI Entrez efetch()  ──▶  GenBank Record
    │                           │
    │                    gc_fraction()
    │                    taxonomy[]
    │                    seq_length
    ▼
correlate_disease_ndvi()
    │  NDVI stress score
    │  Risk zone classification
    ▼
pathogen_database.json + research_summary.md
    │
    ▼
Pflanze UI (future: display genomic context alongside disease alert)
```

---

## How to Run the Pipeline Locally

### Prerequisites

```bash
# Python 3.9 or higher required
python --version

# Install dependencies
pip install biopython>=1.81 requests>=2.31.0 numpy>=1.24.0
# or
pip install -r notebooks/requirements.txt
```

### Run the Analysis

```bash
# From the repository root
python notebooks/pathogen_analysis.py
```

### Expected Output

```
============================================================
  Pflanze Bioinformatics Module
  Plant Pathogen Sequence Analysis
  Started: 2026-02-22 00:00 UTC
============================================================
[INFO] Fetching sequence for: Tobacco Mosaic Virus (Accession: NC_001497)
  ✓ Tobacco Mosaic Virus: 6,395 bp | GC=44.13% | Organism: Tobacco mosaic virus
[INFO] Fetching sequence for: Rice Blast Fungus (Accession: NC_017850)
  ✓ Rice Blast Fungus: 3,947,040 bp | GC=51.86% | Organism: Magnaporthe oryzae 70-15
...

[INFO] Example NDVI (NIR=0.72, Red=0.12): 0.7143
[INFO] Pathogen database saved → data/pathogen_database.json
[INFO] Markdown report saved → notebooks/research_summary.md

[DONE] Pflanze bioinformatics analysis complete.
```

### Using the Pre-filled Sample Data

If you do not wish to make live NCBI API calls, use the pre-filled sample database:

```python
import json

with open("data/sample_pathogen_database.json") as f:
    db = json.load(f)

for pathogen in db["pathogens"]:
    print(f"{pathogen['name']}: {pathogen['gc_content_percent']}% GC, "
          f"NDVI Risk Zone: {pathogen['ndvi_risk_zone']}")
```

---

## Notes on NCBI API Usage

- Always set `Entrez.email` to your own email address (required by NCBI policy)
- Without an NCBI API key, requests are limited to 3/second (the script includes a 0.4s delay)
- For high-throughput analyses, register for an NCBI API key at https://www.ncbi.nlm.nih.gov/account/
- Set your key with: `Entrez.api_key = "YOUR_KEY"`

---

## Integration Roadmap

| Phase | Feature | Status |
|---|---|---|
| v1.0 | Static pathogen mapping (4 species) | ✅ Complete |
| v1.0 | NCBI sequence fetch + GC analysis | ✅ Complete |
| v1.0 | Mock NDVI correlation | ✅ Complete |
| v2.0 | Live NDVI pixel extraction from Sentinel-2 tiles | 🔜 Planned |
| v2.0 | Automatic disease→pathogen mapping from API response | 🔜 Planned |
| v3.0 | RNA-seq differential expression analysis | 🔜 Future |
| v3.0 | Phylogenetic tree visualization in the web UI | 🔜 Future |
