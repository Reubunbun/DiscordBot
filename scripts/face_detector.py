from imutils import face_utils
from keras.models import Model, load_model
import keras, cv2, dlib, sys
import numpy as np

def detect_human_face(img_path):
    img = cv2.imread(img_path)
    predictor_path = "scripts/data/shape_predictor_68_face_landmarks.dat"
    predictor = dlib.shape_predictor( predictor_path )
    detector  = dlib.get_frontal_face_detector()
    if len(img.shape) > 2 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    rects = detector(img, 1)
    detections = []
    if len(rects) > 0:
        for rect in rects:
            shape = predictor(img, rect)
            shape = face_utils.shape_to_np(shape)
            lStart, lEnd = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            rStart, rEnd = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
            new_face = {  "type" : "human", "landmarks" : {
                    "left_eye"   : shape[lStart:lEnd].tolist(),
                    "right_eye"  : shape[rStart:rEnd].tolist(),
                    "nose"       : shape[33].tolist(),
                    "chin"       : shape[8].tolist(),
                    "left_cheek" : shape[0].tolist(),
                    "right_cheek": shape[16].tolist(),
                    "left_brow"  : shape[17:22].tolist(),
                    "right_brow" : shape[22:27].tolist()
                }
            }
            detections.append(new_face)
    else:
        detections = []

    return detections

def predict_bounding_box(img, img_size):
    old_size = img.shape[:2] # old_size is in (height, width) format
    ratio = float(img_size) / max(old_size)
    new_size = tuple( [int(x*ratio) for x in old_size] )
    # new_size should be in (width, height) format
    img = cv2.resize(img, (new_size[1], new_size[0]))
    delta_w = img_size - new_size[1]
    delta_h = img_size - new_size[0]
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)
    new_img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
        value=[0, 0, 0])
    return new_img, ratio, top, left

def detect_cat_face(img_path):
    bbs_model  = load_model("scripts/data/bbs_1.h5" )
    lmks_model = load_model("scripts/data/lmks_1.h5")
    img_size = 224

    img = cv2.imread(img_path)
    if len(img.shape) > 2 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    ori_img = img.copy()
    result_img = img.copy()
    img, ratio, top, left = predict_bounding_box(img, img_size)

    inputs = (img.astype('float32') / 255).reshape((1, img_size, img_size, 3))
    pred_bb = bbs_model.predict(inputs)[0].reshape((-1, 2))

    ori_bb = ((pred_bb - np.array([left, top])) / ratio).astype(np.int)
    center = np.mean(ori_bb, axis=0)
    face_size = max(np.abs(ori_bb[1] - ori_bb[0]))
    new_bb = np.array([
      center - face_size * 0.6,
      center + face_size * 0.6
    ]).astype(np.int)
    new_bb = np.clip(new_bb, 0, 99999)

    # predict landmarks
    face_img = ori_img[new_bb[0][1]:new_bb[1][1], new_bb[0][0]:new_bb[1][0]]
    face_img, face_ratio, face_top, face_left = predict_bounding_box(face_img, img_size)
    face_inputs = (face_img.astype('float32') / 255).reshape((1, img_size, img_size, 3))
    pred_lmks = lmks_model.predict(face_inputs)[0].reshape((-1, 2))

    # compute landmark of original image
    new_lmks = ((pred_lmks - np.array([face_left, face_top])) / face_ratio).astype(np.int)
    ori_lmks = new_lmks + new_bb[0]

    new_detection = { "type" : "cat", "landmarks" : {
            "left_eye"  : ori_lmks[0].tolist(),
            "right_eye" : ori_lmks[1].tolist(),
            "nose"      : ori_lmks[2].tolist(),
            "left_left_ear"   : ori_lmks[3].tolist(),
            "right_left_ear"  : ori_lmks[5].tolist(),
            "left_right_ear"  : ori_lmks[6].tolist(),
            "right_right_ear" : ori_lmks[8].tolist()
        }
    }
    eye_w = abs(new_detection["landmarks"]["right_right_ear"][0] - new_detection["landmarks"]["left_left_ear"][0])*0.3
    eye_h = 0.75*eye_w
    leye, reye = new_detection["landmarks"]["left_eye"], new_detection["landmarks"]["right_eye"]
    leye_center = find_eye_center(leye, eye_w, eye_h, ori_img)
    if leye_center is not None and leye_center[1] > leye[1]:
        new_detection["landmarks"]["left_eye"]  = leye_center
    reye_center = find_eye_center(reye, eye_w, eye_h, ori_img)
    if reye_center is not None and reye_center[1] > reye[1]:
        new_detection["landmarks"]["right_eye"] = reye_center

    return new_detection

def find_eye_center(point, eye_w, eye_h, img):
    x1 = int( point[0] - (0.5*eye_w) )
    x2 = int( point[0] + (0.5*eye_w) )
    y1 = int( point[1] - (0.5*eye_h) )
    y2 = int( point[1] + (0.5*eye_h) )
    cropped = img[y1:y2,x1:x2]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.blur(gray, (3,3))
    param2 = 50
    while True:
        detected_circles = cv2.HoughCircles(gray_blurred,
                       cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
                       param2 = param2, minRadius = 1, maxRadius = 40)
        if detected_circles is not None:
            detected_circles = np.uint16(np.around(detected_circles))
            if len(detected_circles[0,:]) == 1:
                for pt in detected_circles[0, :]:
                    return [x1+pt[0], y1+pt[1]]
                break
        param2 -= 5
        if param2 < 20:
            break
    return None

if __name__ == "__main__":
    if len(sys.argv) == 3:
        _, img_file, type = sys.argv
        if type == "cat":
            landmarks = detect_cat_face(img_file)
            print([landmarks])
        elif type == "human":
            landmarks = detect_human_face(img_file)
            print(landmarks)
        elif type == "both":
            human_landmarks = detect_human_face(img_file)
            cat_landmarks   = detect_cat_face(img_file)
            human_landmarks.append(cat_landmarks)
            print(human_landmarks)
        else:
            print("Don't recognise type")
    else:
        print("Invalid arguments")
