from fastapi import FastAPI


app = FastAPI(
  title = "Genomic Variant Interpretation Assistant",
  version = "0.0.1"
)

@app.get("/health")
def health():
  return {"ok" : True}
