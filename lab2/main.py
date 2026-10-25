from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_image(file: UploadFile = File(...), method: str = Form(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    res = img.copy()

    if method == 'linear':
        res = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            
    elif method == 'eq_rgb':
        for i in range(3):
            res[:, :, i] = cv2.equalizeHist(img[:, :, i])
            
    elif method == 'eq_hsv':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
        res = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
    elif method == 'points':
        kernel = np.array([[-1, -1, -1],
                           [-1,  8, -1],
                           [-1, -1, -1]])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered = cv2.filter2D(gray, -1, kernel)
        res = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        
    elif method == 'lines':
        kernel = np.array([[-1, -1, -1],
                           [ 2,  2,  2],
                           [-1, -1, -1]])
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered = cv2.filter2D(gray, -1, kernel)
        res = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        
    elif method == 'sobel':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        magnitude = np.uint8(np.clip(magnitude, 0, 255))
        res = cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

    _, buffer = cv2.imencode('.jpg', res)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)