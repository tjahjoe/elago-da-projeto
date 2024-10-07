import asyncio
import cv2
from queue import Queue
from threading import Thread
from websockets.asyncio.server import serve
import websockets

frame_queue = Queue(maxsize=1)
stop = False

def cam():
    global stop
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened() and not stop :
        ret, frame = cap.read()
        if not ret :
            break
        frame = cv2.flip(frame, 1)
        _, encoded_frame = cv2.imencode('.jpg', frame)
        data = encoded_frame.tobytes()

        if not frame_queue.full() :
            frame_queue.put(data)
        else :
            frame_queue.get_nowait()
            frame_queue.put(data)

        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) == ord('q') :
            stop = True
            break

    cap.release()
    cv2.destroyAllWindows()

async def headler(websocket) :
    global stop
    while not stop :
        try :
            if not frame_queue.empty():
                data = frame_queue.get_nowait()
                await websocket.send(data)
        except websockets.ConnectionClosedOK :
            # pass
            # stop = True
            break
        except KeyboardInterrupt :
            stop = True
            break
        await asyncio.sleep(0)

async def main() :
    async with serve(headler, "0.0.0.0", 8001) :
        await asyncio.get_running_loop().create_future() 
        # await asyncio.Future() # hampir sama dengan yang atas akan tetapi tidak sepesifik


if __name__ == '__main__' :
    running_cam = Thread(target=cam)
    running_cam.start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    running_cam.join()