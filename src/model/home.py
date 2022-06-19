from model.common import *
from datetime import datetime
import numpy as np


def check_exist(his):
    global history_file
    check_range = min(20, len(history_file))
    return his in history_file[-check_range:]


def check_and_write(name, face):
    global names, history_file

    time = datetime.now()
    time = time.strftime(r'%Y/%m/%d %H:%M')
    date, hour, minute  = time[:10], int(time[11:13]), int(time[14:16])

    
    cur_time = -1
    check_range = min(50, len(history_file))
    for i in range(1, check_range+1):
        if history_file[-i]['name'] == name:
            cur_time = history_file[-i]['date']
            break

    # print(cur_time)
    if cur_time != -1:
        cur_date, cur_hour, cur_minute = cur_time[:10], int(cur_time[11:13]), int(cur_time[14:16])
        if cur_date == date and ((hour*60+minute) - (cur_hour*60+cur_minute)) < 10:  # Vi pham trong 10p gan day
            return

    evidence_path = 'data/evidence/{}_{:02d}{:02d}_{}.jpg'.format(date.replace("/", ""), hour, minute, name)
    his = {'name': name, 'date':time, 'evidence':evidence_path}
    if check_exist(his):
        return

    face = np.array(face)
    cv2.imwrite(evidence_path, face)
    history_file.append(his)
    with open('data/history.json', 'w') as f:
        json.dump(history_file, f, indent=2)


def face_reg(face):
    global fe, embeddings, names
    embed = fe(trans(face).unsqueeze(0).to('cuda:0'))
    norm_score = torch.nn.functional.cosine_similarity(embed.to('cpu'), embeddings)
    score, embed_idx = torch.max(norm_score, dim=0)
    name = names[int(embed_idx/3)]['name']
    if score > 0.7: 
        check_and_write(name, face)


def yolo2img(img, boxes):
    global names
    for box in boxes:
        x1, y1, x2, y2, _, cls = map(int, box)
        if not cls and len(names):
            face_reg(extract_face(img, [x1, y1, x2, y2]))
        img = cv2.rectangle(img, (x1, y1), (x2, y2), [255, 0, 0] if cls else [0, 255, 0], thickness=2)
        img = cv2.putText(img, 'mask' if cls else 'no mask', (x1, y1), color=[255, 0, 0] if cls else [0, 255, 0], thickness=2, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1)
    return img


def gen_frames(id):
    global model
    cap = cv2.VideoCapture(id)
    # cap.set(cv2.CAP_PROP_FPS, 30)
    while True:
        success, frame = cap.read()  # read the camera frame
        if not success:
            continue
        frame0 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = model(frame0)
        frame = yolo2img(frame, res.xyxy[0])
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    