from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class LineReq(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class CircleReq(BaseModel):
    xc: int
    yc: int
    r: int

def algo_step(x1, y1, x2, y2):
    points = []
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) >= abs(dy):
        if dx == 0: return [[x1, y1]]
        k = dy / dx
        b = y1 - k * x1
        step = 1 if dx > 0 else -1
        x = x1
        while True:
            points.append([x, round(k * x + b)])
            if x == x2: break
            x += step
    else:
        if dy == 0: return [[x1, y1]]
        k = dx / dy
        b = x1 - k * y1
        step = 1 if dy > 0 else -1
        y = y1
        while True:
            points.append([round(k * y + b), y])
            if y == y2: break
            y += step
    return points

def algo_dda(x1, y1, x2, y2):
    points = []
    dx, dy = x2 - x1, y2 - y1
    length = max(abs(dx), abs(dy))
    if length == 0: return [[x1, y1]]
    sx, sy = dx / length, dy / length
    x, y = x1, y1
    for _ in range(int(length) + 1):
        points.append([round(x), round(y)])
        x += sx
        y += sy
    return points

def algo_bresenham_line(x1, y1, x2, y2):
    points = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    while True:
        points.append([x1, y1])
        if x1 == x2 and y1 == y2: break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return points

def algo_bresenham_circle(xc, yc, r):
    points = []
    x, y = 0, r
    err = 3 - 2 * r

    def add_sym(x, y):
        points.extend([
            [xc + x, yc + y], [xc + x, yc - y],
            [xc - x, yc + y], [xc - x, yc - y],
            [xc + y, yc + x], [xc + y, yc - x],
            [xc - y, yc + x], [xc - y, yc - x]
        ])

    while x <= y:
        add_sym(x, y)
        if err >= 0:
            err += 4 * (x - y) + 10
            y -= 1
        else:
            err += 4 * x + 6
        x += 1
    
    unique_points = []
    for p in points:
        if p not in unique_points:
            unique_points.append(p)
    return unique_points

@app.post("/api/step")
def api_step(req: LineReq):
    t0 = time.perf_counter()
    pts = algo_step(req.x1, req.y1, req.x2, req.y2)
    dt = (time.perf_counter() - t0) * 1000
    return {"points": pts, "time_ms": round(dt, 4)}

@app.post("/api/dda")
def api_dda(req: LineReq):
    t0 = time.perf_counter()
    pts = algo_dda(req.x1, req.y1, req.x2, req.y2)
    dt = (time.perf_counter() - t0) * 1000
    return {"points": pts, "time_ms": round(dt, 4)}

@app.post("/api/bresenham")
def api_bresenham(req: LineReq):
    t0 = time.perf_counter()
    pts = algo_bresenham_line(req.x1, req.y1, req.x2, req.y2)
    dt = (time.perf_counter() - t0) * 1000
    return {"points": pts, "time_ms": round(dt, 4)}

@app.post("/api/bresenham_circle")
def api_bresenham_circle(req: CircleReq):
    t0 = time.perf_counter()
    pts = algo_bresenham_circle(req.xc, req.yc, req.r)
    dt = (time.perf_counter() - t0) * 1000
    return {"points": pts, "time_ms": round(dt, 4)}

if __name__ == "__main__":
  uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)