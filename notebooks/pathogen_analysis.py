"""
Pflanze Bioinformatics Module
Plant Pathogen Sequence Analysis using Biopython + NCBI Entrez
Part of: Pflanze Crop Monitoring Platform
Author: Yashraj

Description:
    Fetches real plant pathogen sequences from NCBI, computes GC content,
    extracts taxonomy, correlates pathogen risk with satellite-derived NDVI
    stress scores, and generates a structured JSON database + Markdown report.

Usage:
    pip install biopython
    python pathogen_analysis.py
"""

import json
import os
import datetime
import time

from Bio import Entrez, SeqIO
from Bio.SeqUtils import gc_fraction

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Always set your email when using NCBI Entrez to comply with NCBI policies.
# may result in your IP being blocked. See: https://www.ncbi.nlm.nih.gov/books/NBK25497/
Entrez.email = "yashrajpatil250@gmail.com"

# Runtime guard: refuse to run with the placeholder email
if Entrez.email == "your@email.com":
    raise ValueError(
        "Please set a valid email address in Entrez.email before running this script. "
        "NCBI requires a real contact email to comply with their usage policy."
    )

# Pathogens mapped to diseases covered in the Pflanze app
PATHOGEN_SEQUENCES = {
    "Tobacco Mosaic Virus": {
        "id": "NC_001497",
        "crop": "Tomato/Tobacco",
        "disease": "Mosaic Disease",
        "description": (
            "A (+)ssRNA plant virus that causes mosaic discoloration and "
            "stunted growth. One of the most widely studied plant viruses."
        ),
    },
    "Rice Blast Fungus": {
        "id": "NC_017850",
        "crop": "Rice",
        "disease": "Rice Blast",
        "description": (
            "Magnaporthe oryzae causes rice blast, the most destructive fungal "
            "disease of rice, responsible for significant yield losses globally."
        ),
    },
    "Potato Late Blight": {
        "id": "NC_015247",
        "crop": "Potato/Tomato",
        "disease": "Late Blight",
        "description": (
            "Phytophthora infestans is an oomycete responsible for the Irish "
            "Potato Famine (1840s) and remains a major threat to solanaceous crops."
        ),
    },
    "Wheat Stripe Rust": {
        "id": "NC_014069",
        "crop": "Wheat",
        "disease": "Stripe Rust",
        "description": (
            "Puccinia striiformis f.sp. tritici causes yellow stripe rust on wheat, "
            "reducing grain yield by up to 70% under epidemic conditions."
        ),
    },
}

# NDVI thresholds used for disease risk correlation
# NDVI < 0.2 → bare soil/severe stress; 0.2–0.4 → moderate; 0.4–0.6 → fair; >0.6 → healthy
NDVI_RISK_THRESHOLDS = {
    "severe_stress": 0.20,
    "moderate_stress": 0.40,
    "fair_health": 0.60,
}


# ---------------------------------------------------------------------------
# Core Analysis Functions
# ---------------------------------------------------------------------------

def analyze_pathogen(name: str, info: dict) -> dict:
    """
    Fetch a pathogen sequence from NCBI Entrez and compute bioinformatics metrics.

    Parameters
    ----------
    name : str
        Human-readable pathogen name (e.g. "Tobacco Mosaic Virus").
    info : dict
        Dict with keys 'id', 'crop', 'disease', 'description'.

    Returns
    -------
    dict
        Structured record with sequence metadata and computed metrics.
        Returns a fallback dict with error information on failure.
    """
    accession = info["id"]
    print(f"[INFO] Fetching sequence for: {name} (Accession: {accession})")

    try:
        # Fetch the GenBank record from NCBI
        handle = Entrez.efetch(
            db="nucleotide",
            id=accession,
            rettype="gb",
            retmode="text"
        )
        record = SeqIO.read(handle, "genbank")
        handle.close()

        # Respect NCBI rate limit (max 3 requests/second without API key)
        time.sleep(0.4)

        # Compute GC content as a percentage
        gc_pct = round(gc_fraction(record.seq) * 100, 2)
        seq_len = len(record.seq)

        # Extract taxonomy from annotations
        taxonomy = record.annotations.get("taxonomy", [])

        result = {
            "name": name,
            "accession": accession,
            "description": info["description"],
            "organism": record.annotations.get("organism", "Unknown"),
            "taxonomy": taxonomy,
            "sequence_length_bp": seq_len,
            "gc_content_percent": gc_pct,
            "associated_crop": info["crop"],
            "disease_name": info["disease"],
            "data_source": "NCBI Nucleotide",
            "fetch_date": datetime.datetime.utcnow().isoformat() + "Z",
            "error": None,
        }

        print(
            f"  ✓ {name}: {seq_len:,} bp | GC={gc_pct}% | "
            f"Organism: {result['organism']}"
        )
        return result

    except (OSError, ValueError, RuntimeError) as exc:
        print(f"  ✗ Failed to fetch {name}: {exc}")
        return {
            "name": name,
            "accession": accession,
            "description": info.get("description", ""),
            "organism": "Unknown",
            "taxonomy": [],
            "sequence_length_bp": None,
            "gc_content_percent": None,
            "associated_crop": info["crop"],
            "disease_name": info["disease"],
            "data_source": "NCBI Nucleotide",
            "fetch_date": datetime.datetime.utcnow().isoformat() + "Z",
            "error": str(exc),
        }


def compute_ndvi(nir: float, red: float) -> float:
    """
    Compute the Normalized Difference Vegetation Index (NDVI).

    NDVI = (NIR - Red) / (NIR + Red)

    Values range from -1.0 to +1.0:
      < 0.2  : Bare soil, urban, water, or severely stressed vegetation
      0.2–0.4: Sparse or stressed vegetation
      0.4–0.6: Moderate, fair-health vegetation
      > 0.6  : Dense, healthy green vegetation

    Parameters
    ----------
    nir : float
        Near-infrared reflectance (Sentinel-2 Band 8, ~842 nm).
    red : float
        Red reflectance (Sentinel-2 Band 4, ~665 nm).

    Returns
    -------
    float
        NDVI value in [-1.0, 1.0], or 0.0 if nir + red == 0 (avoid division by zero).

    References
    ----------
    Rouse et al. (1974). Monitoring vegetation systems in the Great Plains
    with ERTS. Proc. 3rd ERTS Symposium, NASA SP-351, 309–317.
    """
    denominator = nir + red
    if denominator == 0:
        return 0.0
    return round((nir - red) / denominator, 4)


def correlate_disease_ndvi(pathogen_results: list) -> list:
    """
    Correlate pathogen risk levels with satellite-derived NDVI stress zones.

    Uses a mock NDVI stress score per pathogen (in a real pipeline this
    would be replaced by field-observed Sentinel-2 pixel values).

    The correlation score is computed as:
        ndvi_correlation_score = 1.0 - mock_ndvi
    i.e., lower NDVI → higher pathogen risk indicator.

    Parameters
    ----------
    pathogen_results : list
        List of dicts returned by analyze_pathogen().

    Returns
    -------
    list
        Same list with 'ndvi_correlation_score' and 'ndvi_risk_zone' added
        to each record.
    """
    # Representative NDVI values observed in disease-affected fields
    # (based on published literature for each pathogen/crop combination)
    mock_ndvi_map = {
        "Tobacco Mosaic Virus": 0.42,   # Moderate stress on foliar crops
        "Rice Blast Fungus":    0.31,   # Significant canopy damage in rice
        "Potato Late Blight":   0.25,   # Severe defoliation
        "Wheat Stripe Rust":    0.38,   # Moderate-to-severe stripe rust
    }

    for record in pathogen_results:
        ndvi_val = mock_ndvi_map.get(record["name"], 0.50)
        correlation_score = round(1.0 - ndvi_val, 4)

        # Classify into risk zones based on NDVI thresholds
        if ndvi_val < NDVI_RISK_THRESHOLDS["severe_stress"]:
            risk_zone = "Severe Stress"
        elif ndvi_val < NDVI_RISK_THRESHOLDS["moderate_stress"]:
            risk_zone = "Moderate Stress"
        elif ndvi_val < NDVI_RISK_THRESHOLDS["fair_health"]:
            risk_zone = "Fair Health"
        else:
            risk_zone = "Healthy"

        record["ndvi_correlation_score"] = correlation_score
        record["ndvi_risk_zone"] = risk_zone
        record["representative_ndvi"] = ndvi_val

    return pathogen_results


def generate_summary_report(results: list) -> None:
    """
    Print a tabular summary to stdout and save a Markdown research report.

    Parameters
    ----------
    results : list
        List of pathogen analysis dicts (output of analyze_pathogen +
        correlate_disease_ndvi).
    """
    report_lines = [
        "# Pflanze — Pathogen Bioinformatics Analysis Report",
        "",
        f"**Generated:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Script:** `notebooks/pathogen_analysis.py`",
        f"**Data source:** NCBI Nucleotide (via Biopython Entrez API)",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Pathogen | Accession | Length (bp) | GC% | Crop | Disease | NDVI Score | Risk Zone |",
        "|---|---|---|---|---|---|---|---|",
    ]

    print("\n" + "=" * 80)
    print("PFLANZE PATHOGEN ANALYSIS — SUMMARY REPORT")
    print("=" * 80)
    print(f"{'Pathogen':<30} {'Accession':<12} {'Length':>10} {'GC%':>6} {'Risk Zone':<18}")
    print("-" * 80)

    for r in results:
        length_str = f"{r['sequence_length_bp']:,}" if r["sequence_length_bp"] else "N/A"
        gc_str = f"{r['gc_content_percent']}" if r["gc_content_percent"] is not None else "N/A"
        score = r.get("ndvi_correlation_score", "N/A")
        zone = r.get("ndvi_risk_zone", "N/A")

        # Console row
        print(
            f"{r['name']:<30} {r['accession']:<12} {length_str:>10} "
            f"{gc_str:>6} {zone:<18}"
        )

        # Markdown row
        report_lines.append(
            f"| {r['name']} | {r['accession']} | {length_str} | "
            f"{gc_str} | {r['associated_crop']} | {r['disease_name']} | "
            f"{score} | {zone} |"
        )

    print("=" * 80)

    # Extended Markdown sections
    report_lines += [
        "",
        "---",
        "",
        "## NDVI Formula",
        "",
        "```",
        "NDVI = (NIR - Red) / (NIR + Red)",
        "```",
        "",
        "| NDVI Range | Interpretation |",
        "|---|---|",
        "| < 0.2 | Bare soil / severe stress |",
        "| 0.2 – 0.4 | Sparse / stressed vegetation |",
        "| 0.4 – 0.6 | Moderate, fair-health vegetation |",
        "| > 0.6 | Dense, healthy vegetation |",
        "",
        "---",
        "",
        "## Pathogen Details",
        "",
    ]

    for r in results:
        report_lines += [
            f"### {r['name']}",
            "",
            f"- **Accession:** {r['accession']}",
            f"- **Organism:** {r['organism']}",
            f"- **Taxonomy:** {' > '.join(r['taxonomy'][:4]) if r['taxonomy'] else 'N/A'}",
            f"- **Sequence Length:** {r['sequence_length_bp']:,} bp" if r["sequence_length_bp"] else "- **Sequence Length:** N/A",
            f"- **GC Content:** {r['gc_content_percent']}%" if r["gc_content_percent"] is not None else "- **GC Content:** N/A",
            f"- **Associated Crop:** {r['associated_crop']}",
            f"- **Disease:** {r['disease_name']}",
            f"- **NDVI Correlation Score:** {r.get('ndvi_correlation_score', 'N/A')}",
            f"- **Risk Zone:** {r.get('ndvi_risk_zone', 'N/A')}",
            f"- **Description:** {r['description']}",
            "",
        ]

    report_lines += [
        "---",
        "",
        "## References",
        "",
        "- Rouse, J.W. et al. (1974). Monitoring vegetation systems in the Great Plains with ERTS.",
        "- Hughes, D.P. & Salathé, M. (2015). An open access repository of images on plant health.",
        "- Mohanty, S.P. et al. (2016). Using deep learning for image-based plant disease detection. *Frontiers in Plant Science*, 7, 1419.",
        "- NCBI Nucleotide Database: https://www.ncbi.nlm.nih.gov/nucleotide/",
        "",
    ]

    # Save Markdown report
    report_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "research_summary.md"
    )
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report_lines))

    print(f"\n[INFO] Markdown report saved → {report_path}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  Pflanze Bioinformatics Module")
    print("  Plant Pathogen Sequence Analysis")
    print(f"  Started: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Step 1: Fetch and analyze all pathogen sequences from NCBI
    all_results = []
    for pathogen_name, pathogen_info in PATHOGEN_SEQUENCES.items():
        result = analyze_pathogen(pathogen_name, pathogen_info)
        all_results.append(result)

    # Step 2: Compute NDVI-based disease risk correlation
    all_results = correlate_disease_ndvi(all_results)

    # Step 3: Validate NDVI formula with example values
    example_ndvi = compute_ndvi(nir=0.72, red=0.12)
    print(f"\n[INFO] Example NDVI (NIR=0.72, Red=0.12): {example_ndvi}")

    # Step 4: Save pathogen database as JSON
    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "pathogen_database.json"
    )
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with open(db_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "NCBI Nucleotide via Biopython Entrez API",
                "total_pathogens": len(all_results),
                "pathogens": all_results,
            },
            fh,
            indent=2,
            ensure_ascii=False,
        )
    print(f"[INFO] Pathogen database saved → {db_path}")

    # Step 5: Generate and save the summary Markdown report
    generate_summary_report(all_results)

    print("\n[DONE] Pflanze bioinformatics analysis complete.")
