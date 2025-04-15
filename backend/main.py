from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os

app = FastAPI()

# Aktifkan CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dalam pengembangan bisa menggunakan "*", tapi untuk produksi sebaiknya lebih spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path : dummyData.json
possible_paths = [
    "../dummyData.json", 
]

DUMMY_DATA = {}
for path in possible_paths:
    try:
        with open(path, "r") as f:
            DUMMY_DATA = json.load(f)
            print(f"Data berhasil dimuat dari: {path}")
            break
    except FileNotFoundError:
        continue

if not DUMMY_DATA:
    print("Haalo: dummyData.json tidak ditemukan!")
    DUMMY_DATA = {"error": "Data tidak tersedia"}

sales_reps = DUMMY_DATA.get("salesReps", [])

# 1. GET /api/data - return all sales reps
@app.get("/api/sales-reps")
def get_all_sales_reps():
    return {"users": sales_reps}

# 2. GET /api/sales/{id} - get sales rep by ID
@app.get("/api/sales/{rep_id}")
def get_sales_rep(rep_id: int):
    for rep in sales_reps:
        if rep["id"] == rep_id:
            return rep
    raise HTTPException(status_code=404, detail="Sales rep not found")

# 3. GET /api/regions - list of unique regions
@app.get("/api/regions")
def get_regions():
    regions = sorted(set(rep["region"] for rep in sales_reps))
    return {"regions": regions}

# 4. GET /api/region/{region} - reps by region
@app.get("/api/region/{region}")
def get_reps_by_region(region: str):
    reps = [rep for rep in sales_reps if rep["region"].lower() == region.lower()]
    return {"region": region, "users": reps}

# 5. GET /api/skills - all unique skills
@app.get("/api/skills")
def get_all_skills():
    skill_set = set()
    for rep in sales_reps:
        skill_set.update(rep.get("skills", []))
    return {"skills": sorted(skill_set)}

# 6. GET /api/skill/{skill} - reps by skill
@app.get("/api/skill/{skill}")
def get_reps_by_skill(skill: str):
    reps = [rep for rep in sales_reps if skill.lower() in map(str.lower, rep.get("skills", []))]
    return {"skill": skill, "users": reps}

# 7. GET /api/deals/summary - total by status and total value
@app.get("/api/deals/summary")
def get_deals_summary():
    summary = {"Closed Won": 0, "Closed Lost": 0, "In Progress": 0, "Total Value": 0}
    for rep in sales_reps:
        for deal in rep.get("deals", []):
            status = deal["status"]
            value = deal["value"]
            if status in summary:
                summary[status] += 1
            summary["Total Value"] += value
    return summary

# 8. GET /api/deals/by-status - grouped deals by status
@app.get("/api/deals/by-status")
def get_deals_by_status():
    status_map = {"Closed Won": [], "Closed Lost": [], "In Progress": []}
    for rep in sales_reps:
        for deal in rep.get("deals", []):
            status = deal["status"]
            status_map[status].append({"salesRep": rep["name"], **deal})
    return status_map

# 9. GET /api/clients - all unique clients
@app.get("/api/clients")
def get_all_clients():
    seen = set()
    clients = []
    for rep in sales_reps:
        for client in rep.get("clients", []):
            name = client["name"]
            if name not in seen:
                seen.add(name)
                clients.append(client)
    return {"clients": clients}

# Optional: AI Mock Endpoint
@app.post("/api/ai")
async def ai_endpoint(request: Request):
    body = await request.json()
    user_question = body.get("question", "")
    return {"answer": f"Ini adalah jawaban placeholder untuk: {user_question}"}

# Optional: Health Check
@app.get("/")
def read_root():
    return {"status": "OK", "message": "Backend API berjalan"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)