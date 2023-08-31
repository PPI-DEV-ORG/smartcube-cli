import cv2
import numpy as np
import multiprocessing

# Fungsi untuk mendeteksi objek dalam satu frame
def detect_objects(frame, model):
    # Lakukan deteksi objek di sini menggunakan model CNN Anda
    # Hasil deteksi diberikan dalam bentuk bounding boxes dan label

    # Contoh sederhana untuk menunjukkan proses
    # Ini hanya menggambar kotak di tengah frame
    height, width, _ = frame.shape
    center_x, center_y = width // 2, height // 2
    cv2.rectangle(frame, (center_x - 50, center_y - 50), (center_x + 50, center_y + 50), (0, 255, 0), 2)

    return frame

# Fungsi untuk memproses satu video stream
def process_camera(camera_id):
    cap = cv2.VideoCapture(camera_id)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Panggil fungsi deteksi objek untuk setiap frame
        processed_frame = detect_objects(frame, model)

        # Tampilkan frame yang telah diproses
        cv2.imshow(f'Camera {camera_id}', processed_frame)
        
        # Tekan 'q' untuk keluar dari loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Inisialisasi model CNN Anda di sini
    model = None  # Gantilah dengan model CNN yang sesuai
    
    # Daftar kamera yang akan digunakan (gantilah sesuai kebutuhan)
    camera_ids = [
    'rtsp://192.168.215.211:8080/h264.sdp', 
    'rtsp://192.168.215.214:8081/h264.sdp', 
    'rtsp://192.168.215.219:8080/h264.sdp']

    # Mulai proses pemrosesan untuk setiap kamera
    processes = []
    for camera_id in camera_ids:
        p = multiprocessing.Process(target=process_camera, args=(camera_id,))
        p.start()
        processes.append(p)

    # Tunggu semua proses selesai
    for p in processes:
        p.join()
