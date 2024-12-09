import tkinter as tk
from PIL import Image, ImageTk
import pygame
import time
import threading
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# 初始化pygame
pygame.mixer.init()

# 获取系统音量控制接口
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# 解除静音状态
volume.SetMute(0, None)

# 设置音量为最大
volume.SetMasterVolumeLevelScalar(1.0, None)

# 创建主窗口，但先隐藏它
window = tk.Tk()
window.withdraw()

# 创建一个全局列表来存储所有的窗口
windows = []

# 创建一个全局变量来控制窗口的创建
create_windows = False

def create_main_window():
    window.title('下北泽奇遇记')

    # 创建标签
    label = tk.Label(window, text="请尽情抚摸先辈(单击/长按)")
    label.pack()

    try:
        # 加载图像
        normal_image = ImageTk.PhotoImage(Image.open("resource/image/normal.jpg"))
        apply_image = ImageTk.PhotoImage(Image.open("resource/image/apply.jpg"))
    except Exception as e:
        tk.messagebox.showerror("错误", f"无法加载图片: {e}")
        window.destroy()
        return

    # 创建按钮
    button = tk.Button(window, image=normal_image)

    # 创建一个标志变量
    is_long_press = False

    # 创建一个定时器
    timer = None

    # 鼠标按下事件处理器
    def on_press(event):
        nonlocal is_long_press, timer
        is_long_press = False
        button.config(image=apply_image)
        timer = window.after(1000, on_long_press)  # 如果在1秒内没有收到鼠标松开事件，就认为是长按事件

    # 鼠标长按事件处理器
    def on_long_press():
        nonlocal is_long_press
        is_long_press = True
        threading.Thread(target=play_sound, args=("resource/audio/yuan.mp3", button)).start()

        # 在新的线程中创建窗口
        global create_windows
        create_windows = True
        threading.Thread(target=create_new_windows).start()

    # 创建新窗口的函数
    def create_new_windows():
        while create_windows:
            # 创建新的窗口并添加到全局列表中
            new_window = tk.Toplevel(window)
            new_window.title("新窗口")
            new_label = tk.Label(new_window, image=apply_image)
            new_label.pack()
            windows.append(new_window)
            time.sleep(0.1)  # 每0.1秒创建一个新的窗口

    # 鼠标松开事件处理器
    def on_release(event):
        nonlocal is_long_press, timer
        if timer is not None:
            window.after_cancel(timer)  # 取消定时器
            timer = None
        if not is_long_press:  # 只有在非长按的情况下才播放音频
            threading.Thread(target=play_sound, args=("resource/audio/heng.mp3", button)).start()

    # 播放音频的函数
    def play_sound(sound_file, button):
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        except Exception as e:
            tk.messagebox.showerror("错误", f"无法加载音频文件: {e}")
            window.destroy()
            return

        # 音频播放期间持续设置系统音量为最大
        while pygame.mixer.music.get_busy():
            # 解除静音状态
            volume.SetMute(0, None)
            volume.SetMasterVolumeLevelScalar(1.0, None)
            time.sleep(0.1)

        if not pygame.mixer.music.get_busy():  # 音频播放完成后恢复默认图像
            button.config(image=normal_image)

            # 停止创建新的窗口
            global create_windows
            create_windows = False

            # 关闭所有的窗口
            for win in windows:
                win.destroy()
            windows.clear()

    # 绑定事件处理器
    button.bind("<Button-1>", on_press)
    button.bind("<ButtonRelease-1>", on_release)

    button.pack()

    # 显示主窗口
    window.deiconify()

# 创建一个新的窗口来显示提示信息
info_window = tk.Toplevel(window)
info_window.title("提示")

# 在新窗口中添加一个Text部件来显示信息
info_text = tk.Text(info_window, height=10, width=50)
info_text.pack()

# 插入信息
info_text.insert(tk.END, "本程序为作者在下北泽偶遇雷普高人，经高人指点后开发。\n")
info_text.insert(tk.END, "使用程序前请确保身边没人，以防社死！！", "highlight")

# 使用tag_configure方法来改变"highlight"标签的颜色和样式
info_text.tag_configure("highlight", foreground="red", font=("TkDefaultFont", 20, "bold"))

# 创建一个新的函数来处理窗口关闭事件
def close_info_and_open_main():
    info_window.destroy()
    create_main_window()

# 设置窗口关闭时的回调函数
info_window.protocol("WM_DELETE_WINDOW", close_info_and_open_main)

# 运行窗口
window.mainloop()