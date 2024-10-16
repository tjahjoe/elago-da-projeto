import asyncio
import websockets
import numpy as np
import cv2
from queue import Queue, Empty
from detection import detection
from threading import Thread,Event


frame_queue = Queue(maxsize=1)
stop_event = Event()

def display() :
    while not stop_event.is_set() :
        try :
            frame = frame_queue.get_nowait()
            frame = np.frombuffer(frame, dtype='uint8')
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            detection(frame)
            cv2.imshow('rcv', frame)
            if cv2.waitKey(1) == ord('q') :
                stop_event.set()
        except Empty:
            continue

    cv2.destroyAllWindows()


async def client():
    uri = 'ws://localhost:8001/'
    try:
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                if stop_event.is_set():
                    break 

                if not frame_queue.full():
                    frame_queue.put(message)
                await asyncio.sleep(0) 

        stop_event.set()  
    except (websockets.ConnectionClosed, OSError):
        stop_event.set()


if __name__ == '__main__' :
    dtc = Thread(target=display)
    dtc.start()
    try:
        asyncio.run(client())
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        dtc.join()