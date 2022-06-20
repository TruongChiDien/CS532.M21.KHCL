import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from model import home, history, add_member, member
from pydantic import BaseModel

app = FastAPI()
app.mount('/static', StaticFiles(directory='src/model'), name = 'static')
app.mount('/templates', StaticFiles(directory='src/view'), name='templates')
app.mount('/data', StaticFiles(directory='data'), name='data')

templates = Jinja2Templates(directory='src/view')


class Member(BaseModel):
    name: str
    birth: str
    gender: str

    def data(self):
        return {'name': self.name, 'birth': self.birth, 'gender': self.gender}


@app.get('/', response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})


@app.get('/home_feed', response_class=HTMLResponse)
async def home_feed():
    return StreamingResponse(home.gen_frames(0),
                    media_type='multipart/x-mixed-replace; boundary=frame')


@app.get('/members', response_class=HTMLResponse)
async def members_template(request: Request):
    return templates.TemplateResponse('members.html', {"request": request})


@app.get('/get_members', response_class=HTMLResponse)
async def members_table():
    return HTMLResponse(member.members())


@app.get('/add_member', response_class=HTMLResponse)
async def add_member_template(request: Request):
    return templates.TemplateResponse('add_member.html', {"request": request})


@app.get('/add_member_feed', response_class=HTMLResponse)
def add_member_feed():
    return StreamingResponse(add_member.add_member(0),
                    media_type='multipart/x-mixed-replace; boundary=frame')


@app.post('/upload_member_info', response_class=HTMLResponse)
async def member_info(info: Member):
    add_member.add_info(info.data())



@app.get('/history', response_class=HTMLResponse)
async def history_template(request: Request):
    return templates.TemplateResponse('history.html', {"request": request})


@app.get('/get_history', response_class=HTMLResponse)
async def history_table():
    return HTMLResponse(history.history())


if __name__ == '__main__':
    uvicorn.run(app, port=8000)