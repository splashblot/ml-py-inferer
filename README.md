# ml-py-inferer

Rest server written in Python3 compatible with [Web OpenDronMaps](https://github.com/OpenDroneMap/WebODM) 
as ProcessinNode that makes inference over images using models trained with 
[Faster R-CNN networks](https://github.com/rbgirshick/py-faster-rcnn)

## Weaknesses/TODOS
* Parallel execution has not be tested. Could Caffe work well in multithreaded execution,
 making several inferences in parallel?
* Current implementation uses Multithreading. Python is not pretty good at multithreading.
 Does it really paralleling well? Or there is many contention so that we cannot saturate 
 CPU?
* REST server implemented with Flask-restful. After implementation I have noticed that
it wasn't the best decision. It would be better to reimplement the REST server
with DJango. It shouldn't take that much. 
* Security assurance. Current implementation doesn't care much on parameter checking
so it cannot be considered "secure"
* Only happy path has been properly tested. Failure paths should also be properly tested.
* After migration to Python3 and CPU Caffe, non minimal suppression stop working properly
 (NMS). Currently native python implementation is being used, but sure it won't be
 the fastest. 
* Output should also include xml annotation files with predicted bounding boxes and the
status file with the metadata.
