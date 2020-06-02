from utils.array_util import *
import parameters as params
import cv2


def get_video_clips(video_path):
    frames, fps = get_video_frames(video_path)
    clips = sliding_window(frames, params.frame_count, params.frame_count)
    return clips, len(frames), fps


def get_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # frames.append(frame)
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            break
    return frames, fps

def getTemporalAnnotation(predictions, fps, threshold = 0.5):
    temporalAnnotations = []
    start = None
    end = None
    i = 0
    frames = len(predictions)
    while i < frames:
        if predictions[i] >= threshold:
            start = round(i/fps, 2)
            while i < frames and predictions[i] >= threshold:
                i = i + 1
            i = i - 1
            end = round(i/fps, 2)
            ann = {"start": start,
                    "end": end}
            temporalAnnotations.append(ann)
        i = i + 1
    
    return temporalAnnotations
