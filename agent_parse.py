from pydantic import BaseModel, Field
from google import genai
from google.genai import types


# 1. Define your exact schema
class ContractExtraction(BaseModel):
    vendor_name: str
    budget_amount: float
    is_anomalous: bool = Field(description="True if budget > $1M")

# 2. Pass the schema to the LLM
client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='Raw messy text about a $2.5M contract with Acme Corp...',
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ContractExtraction,
    ),
)

# 3. The output is guaranteed to match your schema
print(response.text)
# Output: {"vendor_name": "Acme Corp", "budget_amount": 2500000.0, "is_anomalous": true}