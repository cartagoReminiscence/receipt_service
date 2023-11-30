from fastapi import FastAPI, Request, UploadFile, status

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse

# system files
import os

DIR_FILES_PATH = './files/'

templates = Jinja2Templates(directory='templates')

app = FastAPI()

def delete_saved_files():
    filenames = os.listdir(DIR_FILES_PATH)
    for filename in filenames:
        os.remove(DIR_FILES_PATH + filename)
    print('all files were removed')

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse('home.html', context={'request': request})

@app.get('/filelist', response_class=HTMLResponse)
async def fileslist(request: Request):
    files = os.listdir('./files')
    return templates.TemplateResponse('filelist.html', context={'request': request, 'files': files, 'dir_files_path': DIR_FILES_PATH})

@app.get('/todos/')
async def todo():
    return {'nombre': 'Abraham', 'edad': 27}

@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile):
    title = file.filename
    content = await file.read() # byte encoding

    with open(DIR_FILES_PATH + title, 'wb') as f:
        f.write(content)

    # return RedirectResponse(url='/filelist', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    return RedirectResponse(url='/filelist', status_code=status.HTTP_301_MOVED_PERMANENTLY)

@app.get('/files/{filename}')
async def get_file(filename: str):
    return FileResponse(DIR_FILES_PATH + filename)

@app.get('/delete_files', response_class=HTMLResponse)
async def delete_files(request: Request):
    delete_saved_files()

    return RedirectResponse(url='/filelist', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
