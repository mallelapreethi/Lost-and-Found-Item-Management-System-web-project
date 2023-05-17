import cv2
import torch
def search_video_for_object(link_to_video, item, confid):
# function for detecting object in video
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True) # loading yolov5 model
    object_class = item
    videofile_search = link_to_video
    cap = cv2.VideoCapture(videofile_search)
    last_frame = cv2.imread("notfound.jpg", cv2.IMREAD_ANYCOLOR)
# maintain boolean variable to know whether object is detected or not, keep track of most recent image frame in which object is detected 
    found=False
    box = None
# Looping through all the frames of input video
    while True:
        present, frame_to_read = cap.read() #reading nextframe information
        if not present: # checking if frame is present or not for reading/searching
            break
        frame_to_read = cv2.cvtColor(frame_to_read, cv2.COLOR_BGR2RGB) #converting frame from BGR format to RGB format
    # Run yolov5 detection on frame
        resultant = model(frame_to_read, size=640) # stoiring result in resultant array
    # Filtering the results to store only required object with required confidence thresold
        resultant = resultant.pandas().xyxy[0]
        resultant = resultant[resultant['name'] == object_class]
        resultant = resultant[resultant['confidence'] >= confid]
    # If the required item is detected in the image frame taken, updating the last frame seen and box
        if len(resultant) > 0:
            last_frame = frame_to_read
            found=True
            box = resultant.iloc[0][['xmin', 'ymin', 'xmax', 'ymax']]
            last_result=resultant
    if found :
        # Drawing a box around the object/item detected
        x1, y1, x2, y2 = box
        cv2.rectangle(last_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        label = f"{object_class}: {last_result.iloc[0]['confidence']:.2f}"
        cv2.putText(last_frame, label, (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        last_frame = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
        return last_frame
    else:
        return last_frame
    cap.release()   #releasing the videocapture object

