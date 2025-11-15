from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

class VariantIn(BaseModel):
  chrom: str
  pos: int
  ref: str
  alt: str
  
class PredictRequest(BaseModel):
  genome_build: str
  variants: List[VariantIn]

class VariantResult(BaseModel):
  variant: str
  echo: VariantIn

class PredictResponse(BaseModel):
  genome_build: str
  results: List[VariantResult]

def variant_key(v: VariantIn) -> str:
  return f"{v.chrom}:{str(v.pos)}:{v.ref}>{v.alt}"

app = FastAPI(
  title = "Genomic Variant Interpretation Assistant",
  version = "0.0.1"
)

@app.get("/health")
def health():
  return {"ok" : True}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
  results: List[VariantResult] = []
  for v in req.variants:
    key = variant_key(v)
    result = VariantResult(variant=key, echo=v)
    results.append(result)
  
  return PredictResponse(
    genome_build = req.genome_build,
    results = results
  )
