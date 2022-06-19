from model.common import *

def train_face_reg(faces):
    global fe, embeddings
    left, front, right = faces
    left = torch.cat([trans(img).unsqueeze(0).to('cuda:0') for img in left[10:-10]])
    front = torch.cat([trans(img).unsqueeze(0).to('cuda:0') for img in front[10:-10]])
    right = torch.cat([trans(img).unsqueeze(0).to('cuda:0') for img in right[10:-10]])
    with torch.no_grad():
        embed_left = fe(left).mean(0, keepdim=True)
        embed_front = fe(front).mean(0, keepdim=True)
        embed_right = fe(right).mean(0, keepdim=True)
    
    # embeds = torch.load(DATA_PATH+'/facelist.pth')
    embeddings = torch.cat([embeddings, embed_left.to('cpu'), embed_front.to('cpu'), embed_right.to('cpu')])
    torch.save(embeddings, 'data/facelist.pth')


def add_member(id):
    global model, fe
    cap = cv2.VideoCapture(id)
    cap.set(cv2.CAP_PROP_FPS, 30)
    faces = [[], [], []]    # Chua anh mat trai, truoc, phai
    i, leap = 0, 5
    while True:
        success, frame = cap.read()  # read the camera frame
        if not success:
            continue

        i += 1

        if len(faces[0]) < 50:
            direction, warning = 0, 'Please turn your face to the left'
        elif len(faces[1]) < 50:
            direction, warning = 1, 'Please turn your face foward'
        elif len(faces[2]) < 50:
            direction, warning = 2, 'Please turn your face to the right'
        else:
            direction, warning = -1, 'Model is processing ....'
        
        if i % leap != 0 and direction != -1:
            frame0 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = model(frame0)
            if len(res.xyxy[0]):
                x1, y1, x2, y2, _, cls = map(int, res.xyxy[0][0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), [255, 0, 0], thickness=2)
                face = extract_face(frame0, [x1, y1, x2, y2])
                faces[direction].append(face)

        if direction == -1: # Du anh de train
            cap.release()
            train_face_reg(faces)
            break

        if i % 10 < 5:
            frame = cv2.putText(frame, warning, org=(0, frame.shape[0]-10), color=[0, 0, 255], thickness=2, fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  


def add_info(info):
    global names

    names.append(info)
    with open('data/member.json', 'w') as f:
        json.dump(names, f, indent=2)