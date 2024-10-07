import asyncio
import websockets
import numpy as np
import cv2
from queue import Queue
from detection import detection
from threading import Thread

frame_queue = Queue(maxsize=1)
stop = False

def display() :
    global stop
    while not stop :
        frame = frame_queue.get()
        frame = np.frombuffer(frame, dtype='uint8')
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        detection(frame)
        cv2.imshow('rcv', frame)
        if cv2.waitKey(1) == ord('q') :
            stop = True
            break

    cv2.destroyAllWindows()


async def client() :
    uri = 'ws://localhost:8001/'
    global stop
    try :
        async with websockets.connect(uri) as websocket :
            async for message in websocket:  
                encode_frame = message

                if not frame_queue.full() :
                    frame_queue.put(encode_frame)
                await asyncio.sleep(0)

                if stop :
                    break

            if not stop :
                stop = True
    except :
        stop = True

if __name__ == '__main__' :
    dtc = Thread(target=display)
    dtc.start()
    asyncio.run(client())
    dtc.join()