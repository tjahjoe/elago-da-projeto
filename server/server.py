import asyncio
import cv2
from queue import Queue
from threading import Thread, Event
from websockets.asyncio.server import serve
import websockets
import signal

frame_queue = Queue(maxsize=1)
stop_event = Event()

def cam():
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        _, encoded_frame = cv2.imencode('.jpg', frame)
        data = encoded_frame.tobytes()

        if not frame_queue.full():
            frame_queue.put(data)
        else:
            frame_queue.get_nowait()
            frame_queue.put(data)

        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) == ord('q'):
            stop_event.set()

    cap.release()
    cv2.destroyAllWindows()

async def handler(websocket):
    while not stop_event.is_set():
        try:
            if not frame_queue.empty():
                data = frame_queue.get_nowait()
                await websocket.send(data)
        except websockets.ConnectionClosedOK:
            break
        await asyncio.sleep(0)

async def main():
    async with serve(handler, "0.0.0.0", 8001):
        await asyncio.get_running_loop().run_in_executor(None, stop_event.wait)

def handle_sigint(signum, frame):
    stop_event.set()

if __name__ == '__main__':
    running_cam = Thread(target=cam)
    running_cam.start()

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        running_cam.join()
