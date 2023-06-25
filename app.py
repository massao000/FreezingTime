import tkinter as tk
import cv2
import numpy as np
from PIL import ImageTk, Image
import datetime
import os
import imageio

# カメラ表示
def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=image)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    if is_camera_on:
        video_label.after(10, update_frame)

# カメラ停止
def toggle_camera():
    global is_camera_on
    is_camera_on = not is_camera_on
    if is_camera_on:
        update_frame()

# カウントダウン
def start_countdown():
    # ボタンを無効化
    countdown_button.config(state="disabled")
    
    count_label.config(text="3")
    count_label.update()
    count_label.after(1000, update_count, 2)
    
# カウントダウンアップデート
def update_count(count):
    if count >= 0:
        count_label.config(text=str(count))
        count_label.update()
        count_label.after(1000, update_count, count - 1)
    else:
        count_label.config(text="Go!")
        count_label.update()
        toggle_camera()
        animate_lines()

def animate_lines():
    width, height = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    line_width = 3
    x = 0
    crop_height = 1  # 切り出す領域の高さ
    crop_width = 1  # 切り出す領域の幅
    line_positions = []  # 縦線が通った位置を保存する配列
    speed = speed_scale.get()  # スライドバーの値を取得
    result_image = np.zeros((int(height), int(width), 3), dtype=np.uint8)
    line_direction = get_line_direction()
    dt_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 動画出力用の設定
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    output_video = cv2.VideoWriter(f"output\movie\{dt_now}.mp4", fourcc, 20.0, (int(width), int(height)))

    # GIF出力用のフレームリスト
    frames_gif = []
    
    while x <= width:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_copy = frame.copy()
            
            if line_direction == "Vertical":
                cv2.line(frame, (int(x), 0), (int(x), int(height)), (255, 0, 0), line_width)
                cv2.line(result_image, (int(x), 0), (int(x), int(height)), (255, 0, 0), line_width)
            elif line_direction == "Horizontal":
                cv2.line(frame, (0, int(x)), (int(width), int(x)), (255, 0, 0), line_width)
                cv2.line(result_image, (0, int(x)), (int(width), int(x)), (255, 0, 0), line_width)
            
            if line_positions:
                if line_direction == "Vertical":
                    stop_frame = np.concatenate(line_positions, axis=1)
                elif line_direction == "Horizontal":
                    stop_frame = np.concatenate(line_positions)
                
                stop_frame_h, stop_frame_w = stop_frame.shape[:2]
                frame[0:0+stop_frame_h, 0:0+stop_frame_w] = stop_frame

            image = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=image)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
            video_label.update()
            x += speed
            
            # 動画をフレームごとに書き込み
            frame_video = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output_video.write(frame_video)
            
            # GIF出力用にフレームを追加
            frames_gif.append(frame)
            
            if x % 1 == 0:                
                if line_direction == "Vertical":
                    x1 = int(x) * crop_width
                    y1 = 0
                    x2 = (int(x) + speed) * crop_width
                    y2 = height
                elif line_direction == "Horizontal":
                    x1 = 0
                    y1 = int(x) * crop_height
                    x2 = width
                    y2 = (int(x) + speed) * crop_height
    
                clipping = frame_copy[int(y1):int(y2), int(x1):int(x2)]
                line_positions.append(clipping)
    
    # 動画出力を終了
    output_video.release()
    
    # GIFとして保存
    if save_gif_var.get():
        imageio.mimsave(f"output\gif\{dt_now}.gif", frames_gif, duration=20)
    
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=image)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    
    image = Image.fromarray(stop_frame)
    imgtk = ImageTk.PhotoImage(image=image)
    result_label.imgtk = imgtk
    result_label.configure(image=imgtk)
    result_label.update()
    
    stop_frame = cv2.cvtColor(stop_frame, cv2.COLOR_BGR2RGB)
    
    cv2.imwrite(f"output\img\{dt_now}.png", stop_frame)
    
    # ボタンを有効化
    countdown_button.config(state="normal")
    
    toggle_camera()

def get_line_direction():
    return line_var.get()

def save_dir():
    
    save_dirs = ['output', 'output\gif', 'output\movie', 'output\img']
    
    for i in save_dirs:
        if not os.path.isdir(i):
            os.makedirs(i)

# カメラのキャプチャを開始
cap = cv2.VideoCapture(0)
is_camera_on = True

# Tkinterウィンドウの作成
window = tk.Tk()
window.title("Freezing Time")


# カメラ映像を表示するためのラベルを作成
video_label = tk.Label(window)
video_label.grid(row=0, column=0, padx=10, pady=10)

# 結果を表示するためのラベルを作成
result_label = tk.Label(window)
result_label.grid(row=0, column=1, padx=10, pady=10)

# カウントダウンラベルの作成
count_label = tk.Label(window, text="", font=("Arial", 24))
count_label.grid(row=2, column=0, padx=10, pady=10)

# スピード調整用のスライドバーの作成
speed_scale = tk.Scale(window, from_=1, to=10, orient=tk.HORIZONTAL, label="Speed")
speed_scale.grid(row=3, column=0, padx=10, pady=10)

# ラジオボタンの作成
line_var = tk.StringVar()
line_var.set("Vertical")
vertical_radio = tk.Radiobutton(window, text="Vertical", variable=line_var, value="Vertical")
vertical_radio.grid(row=4, column=0, padx=10, pady=5)
horizontal_radio = tk.Radiobutton(window, text="Horizontal", variable=line_var, value="Horizontal")
horizontal_radio.grid(row=5, column=0, padx=10, pady=5)

# GIFボタンの作成
save_gif_var = tk.BooleanVar()
save_gif_checkbox = tk.Checkbutton(window, text="Save as GIF", variable=save_gif_var)
save_gif_checkbox.grid(row=6, column=0, padx=10, pady=10)
save_gif_label = tk.Label(window, text="Saving GIF takes a long time")
save_gif_label.grid(row=7, column=0, padx=10, pady=10)

# カウントダウンを開始するボタンの作成
countdown_button = tk.Button(window, text="Start Countdown", command=start_countdown)
countdown_button.grid(row=8, column=0, padx=10, pady=10)


# ウィンドウのレイアウトを調整
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

# 保存ディレクトリを実行
save_dir()

# カメラ映像を更新する関数を呼び出す
update_frame()

# Tkinterウィンドウのメインループ
window.mainloop()

# カメラキャプチャを解放
cap.release()