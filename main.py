from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from parser import parse_quiz_file, extract_text
from validator import validate_output_with_gpt, attempt_fix_with_gpt
import tempfile
import uuid
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_post(request: Request):
    return templates.TemplateResponse("upload_form.html", {"request": request})

@app.post("/upload/auto-correct", response_class=HTMLResponse)
async def upload_and_autocorrect(request: Request, file: UploadFile = File(...)):
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    raw_text = extract_text(tmp_path, file.filename)
    parsed_output = parse_quiz_file(tmp_path, file.filename)

    validation_result = validate_output_with_gpt(parsed_output)

    if "✅ VALID FILE" in validation_result:
        final_output = parsed_output
    else:
        final_output = attempt_fix_with_gpt(raw_text)

    output_filename = f"parsed_output_{uuid.uuid4().hex}.txt"
    output_path = os.path.join("generated", output_filename)
    os.makedirs("generated", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_output)

    return templates.TemplateResponse("upload_form.html", {
        "request": request,
        "download_link": f"/download/{output_filename}"
    })

@app.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    file_path = os.path.join("generated", filename)
    return FileResponse(path=file_path, filename=filename, media_type='text/plain')
