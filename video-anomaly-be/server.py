from flask import Flask, request, send_file, Response, render_template,send_from_directory, jsonify
from flask_mime import Mime
import os,io
from c3d import *
from classifier import *
from utils.visualization_util import *
import keras.backend.tensorflow_backend as tb
from threading import Thread
import pickle
# import tensorflow as tf

# build models
feature_extractor = c3d_feature_extractor()
classifier_model = build_classifier_model()

print('Models created')

# graph = tf.get_default_graph()

def generateVideo():
    global feature_extractor
    global classifier_model
    video_name = 'video.mp4'
    save_path = os.path.join(cfg.output_folder, video_name)
    annotations_save_path = os.path.join(cfg.output_folder, 'annotations.pkl')
    #delete existing file in output 
    if(os.path.isfile(save_path)):
        os.remove(save_path)
    if(os.path.isfile(annotations_save_path)):
        os.remove(annotations_save_path)

    # read video
    video_clips, num_frames, fps = get_video_clips(cfg.sample_video_path)

    print("Number of clips in the video : ", len(video_clips))
    print("FPS of video : ", fps)

    print("Models initialized")

    # extract features
    rgb_features = []
    for i, clip in enumerate(video_clips):
        clip = np.array(clip)
        if len(clip) < params.frame_count:
            continue

        clip = preprocess_input(clip)
        rgb_feature = feature_extractor.predict(clip)[0]
        rgb_features.append(rgb_feature)

        print("Processed clip : ", i)

    rgb_features = np.array(rgb_features)

    # bag features
    rgb_feature_bag = interpolate(rgb_features, params.features_per_bag)

    # classify using the trained classifier model
    tb._SYMBOLIC_SCOPE.value = True
    predictions = classifier_model.predict(rgb_feature_bag)

    predictions = np.array(predictions).squeeze()

    predictions = extrapolate(predictions, num_frames)

    temporalAnnotations = getTemporalAnnotation(predictions, fps, 0.5)
    #save the temporalAnnotations
    pickle.dump(temporalAnnotations, open(annotations_save_path, 'wb'))

    # print('temporal annotations:', temporalAnnotations)

    # visualize predictions
    visualize_predictions(cfg.sample_video_path, predictions, save_path)

distFolder = os.path.join('..','video-anomaly-fe','dist','video-anomaly-fe')

app = Flask(__name__, static_folder=distFolder, template_folder=distFolder)
mimetype = Mime(app)

@app.route("/api/upload", methods=['POST'])
def upload_file():
    file = request.files['file']
    print('Files in request:',file,file.filename)
    filename = 'video.mp4'
    file.save(os.path.join('uploads',filename))
    thread = Thread(target=generateVideo)
    thread.start()
    return ""

@app.route("/api/processed_video")
def send_processed_video():
    # with graph.as_default():
    filePath = os.path.join('processed', 'video.mp4')
    if(not os.path.isfile(filePath) or os.path.getsize(filePath) == 0):
        return Response(status=404)

    print('sending processed video',filePath)
    #generateVideo()
    return send_file(filePath, attachment_filename='video.mp4', as_attachment=True)

@app.route("/api/annotations")
def send_annotations():
    filePath = os.path.join('processed', 'annotations.pkl')
    if(not os.path.isfile(filePath) or os.path.getsize(filePath) == 0):
        return Response(status=404)
    annotations = pickle.load(open(filePath, 'rb'))
    print('annotations from route:', annotations)
    return jsonify(annotations)




# @app.route('/', methods=['GET'])
# def root(path=None):
#     print('got path', path)
#     return render_template("index.html", mimetype="application/javascript")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    print('in static proxy', path)
    ext = path.split('.')[-1]
    print('\nin static proxy the extension', ext)
    if (ext == 'js'):
        return send_from_directory(distFolder, path,mimetype="application/javascript")
    elif (ext == 'css'):
        return send_from_directory(distFolder, path,mimetype="text/css")
    elif (ext == 'ico'):
        return send_from_directory(distFolder, path,mimetype="image/x-icon")
    else:
        return render_template("index.html", mimetype="text/html")

    
if __name__ == "__main__":
    app.run(port='8080', debug=True)