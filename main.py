from fastapi import FastAPI, Request, UploadFile, status

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

# system files
from shutil import os, rmtree
# OCR Google Engine
import pytesseract as tess
from PIL import Image

# Global variables
DOT = '.'
DIR_FILES_PATH = './files/'

templates = Jinja2Templates(directory='templates')

app = FastAPI()

def create_file(full_path, filename, content): # content: byte encoded
    with open(full_path + '/' + filename, 'wb') as f:
        f.write(content)

def transcript_photo(source_file: str):
    my_image = Image.open(source_file)
    text = tess.image_to_string(my_image)
    byte_encoded_content = bytes(text, 'utf-8')

    return byte_encoded_content

def delete_saved_files():
    files = os.listdir(DIR_FILES_PATH)
    if files != list():
        for file in files:
            rmtree(DIR_FILES_PATH + file)

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('home.html', context={'request': request})

@app.get('/filelist', response_class=HTMLResponse)
async def fileslist(request: Request):
    filenames_and_formats = list()

    dir_files = os.listdir('./files')
    for dir_file in dir_files:
        files = os.listdir('./files/' + dir_file)

        lista = list()
        for file in files:
            if file.find(DOT) != -1:
                lista += file.split(DOT)
        filenames_and_formats.append(lista)

    return templates.TemplateResponse('filelist.html', context={'request': request, 'dir_source_files_path': DIR_FILES_PATH, 'filenames_and_formats': filenames_and_formats})

@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile):
    if file.filename != "":
        content = await file.read() # byte encoding
        filename = file.filename

        name, file_format = filename.split(DOT)

        full_path = DIR_FILES_PATH + name
        os.mkdir(full_path)
        create_file(full_path, filename, content)

        if file_format == 'jpg' or file_format == 'png':
            source_file = full_path + '/' + filename
            transcription_content = transcript_photo(source_file)
            transcription_filename = name + '.txt'
            create_file(full_path, transcription_filename, transcription_content)

    return RedirectResponse(url='/filelist', status_code=status.HTTP_301_MOVED_PERMANENTLY)

@app.get('/files/{filename}')
async def get_file(filename: str):
    dir_filename = filename.split(DOT)[0]
    return FileResponse(DIR_FILES_PATH + dir_filename + '/' + filename)

@app.get('/delete_files', response_class=HTMLResponse)
async def delete_files(request: Request):
    delete_saved_files()

    return RedirectResponse(url='/filelist', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
