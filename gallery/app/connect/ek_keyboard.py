import pyautogui

class Keyboard:
    def __init__(self):
        pass
    
    def write(self, text):
        pyautogui.typewrite(text)

    def press(self, key):
        pyautogui.press(key)

    def press_hot_key(self, *args, **kwargs):
        pyautogui.hotkey(*args, **kwargs)

    def volume_up(self):
        pyautogui.press('volumeup')

    def volume_down(self):
        pyautogui.press('volumedown')
    
    def volume_mute(self):
        pyautogui.press('volumemute')
    
    def volume_no_mute(self):
        pyautogui.press('volumemute')

    def next_music(self):
        pyautogui.press('nexttrack')

    def prev_music(self):
        pyautogui.press('prevtrack')
    
    def music_play(self):
        pyautogui.press('playpause')

    def music_pause(self):
        pyautogui.press('playpause')
    
    def finger_up(self, text):
        pyautogui.typewrite(text)
        pyautogui.press('enter')

if __name__ == '__main__':
    keyboard = Keyboard()
    # 模拟按下 L 键
    pyautogui.keyDown('win')
    pyautogui.keyDown('l')
    pyautogui.keyUp('l')
    pyautogui.keyUp('win')
