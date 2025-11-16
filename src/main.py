"""
Genomic Variant Interpretation Service

This module provides a FastAPI-based REST API for genomic variant annotation and interpretation.
It accepts variant data in standard genomic format (chromosome, position, reference, alternate alleles)
and returns annotated results including gene information, clinical consequences, and population frequencies.

Author: VarScanner Team
Version: 0.0.1
"""

from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json


class VariantIn(BaseModel):
  """
  Input model for a single genomic variant.
  
  Represents a variant in standard VCF-like format with chromosome, position,
  reference allele, and alternate allele information.
  """
  chrom: str  # Chromosome identifier (e.g., "1", "22", "X")
  pos: int    # Genomic position (1-based coordinate)
  ref: str    # Reference allele sequence
  alt: str    # Alternate (variant) allele sequence
  
class PredictRequest(BaseModel):
  """
  Request model for variant prediction/annotation.
  
  Contains a list of variants to be annotated along with the reference genome
  build used for interpretation (e.g., "GRCh37", "GRCh38").
  """
  genome_build: str              # Reference genome build identifier
  variants: List[VariantIn]      # List of variants to annotate

class VariantResult(BaseModel):
  """
  Output model for an annotated variant.
  
  Contains the original variant information (echo) along with functional annotation
  including gene association, predicted consequence, population allele frequency,
  and clinical significance from public databases.
  """
  variant: str                        # Variant identifier string (chrom:pos:ref>alt)
  echo: VariantIn                     # Echo of the input variant
  gene: Optional[str] = None          # Gene symbol (if variant is in a gene)
  consequence: Optional[str] = None   # Predicted functional consequence
  gnomad_af: Optional[float] = None   # Allele frequency in gnomAD population database
  rsid: Optional[str] = None          # dbSNP reference SNP identifier
  clinvar: Optional[str] = None       # Clinical significance from ClinVar

class PredictResponse(BaseModel):
  """
  Response model for batch variant annotation.
  
  Contains the genome build used for annotation and a list of annotated results,
  maintaining one-to-one correspondence with the input variants.
  """
  genome_build: str           # Reference genome build used for interpretation
  results: List[VariantResult]  # Annotated results for each input variant

# ============================================================================
# Module-level data initialization
# ============================================================================

STUB_PATH = Path("../data/stubs/annot.json")  # Path to stub annotation data file
# Load stub annotation data from JSON file (used for demonstration/testing)
STUB_ANNOT = json.loads(STUB_PATH.read_text())

def variant_key(v: VariantIn) -> str:
  """
  Generate a standardized variant identifier string.
  
  Converts a variant object into a standardized key format used for lookups
  and reporting. Format: chrom:pos:ref>alt
  
  Args:
      v (VariantIn): The variant object to convert to key format
  
  Returns:
      str: Standardized variant key string (e.g., "1:12345:A>T")
  """
  return f"{v.chrom}:{str(v.pos)}:{v.ref}>{v.alt}"

# ============================================================================
# FastAPI application setup
# ============================================================================

app = FastAPI(
  title = "Genomic Variant Interpretation Assistant",
  version = "0.0.1"
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
def health() -> dict:
  """
  Health check endpoint.
  
  Returns:
      dict: Status indicator with 'ok' field set to True if service is operational
  """
  return {"ok" : True}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
  """
  Annotate and interpret genomic variants.
  
  Processes a batch of genomic variants by looking up their annotations from
  the stub database. Each variant is assigned a standardized key and its
  corresponding annotation is retrieved or a default empty annotation is used.
  
  Args:
      req (PredictRequest): Request containing genome build and list of variants
  
  Returns:
      PredictResponse: Annotated results for each input variant with the same
                       genome build reference
  """
  # Initialize results list to accumulate annotated variants
  results: List[VariantResult] = []
  
  # Process each variant in the request
  for v in req.variants:
    # Generate standardized variant key for annotation lookup
    key = variant_key(v)
    
    # Retrieve annotation for this variant from stub data, or use default empty annotation
    annot = STUB_ANNOT.get(
      key,
      {
        # Default annotation structure when variant is not found in stub
        "gene": None,
        "consequence": None,
        "gnomad_af": None,
        "rsid": None,
        "clinvar": None
      }
    )
    
    # Create annotated result object with original variant echo and annotation data
    result = VariantResult(
      variant=key, 
      echo=v, 
      gene=annot["gene"],
      consequence=annot["consequence"],
      gnomad_af=annot["gnomad_af"],
      rsid=annot["rsid"],
      clinvar=annot["clinvar"]
    )
    # Add result to results list
    results.append(result)
  
  # Return response with genome build reference and annotated results
  return PredictResponse(
    genome_build = req.genome_build,
    results = results
  )
