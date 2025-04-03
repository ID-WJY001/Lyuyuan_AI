"""
创建网页版背景图像
"""
from PIL import Image, ImageDraw
import os

def create_school_background():
    """创建学校背景图像"""
    # 创建一个1920x1080的图像，淡蓝色背景
    width, height = 1920, 1080
    background_color = (235, 245, 255)
    
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # 绘制建筑轮廓（简化的学校建筑）
    building_color = (180, 200, 220)
    
    # 主楼
    draw.rectangle([(400, 300), (1520, 800)], fill=building_color, outline=(150, 170, 190), width=2)
    
    # 窗户
    window_color = (220, 230, 255)
    window_outline = (150, 170, 190)
    
    # 绘制窗户行
    for y in range(350, 751, 100):
        for x in range(450, 1471, 120):
            draw.rectangle([(x, y), (x+80, y+70)], fill=window_color, outline=window_outline, width=1)
    
    # 屋顶
    draw.polygon([(400, 300), (960, 150), (1520, 300)], fill=(160, 180, 200), outline=(150, 170, 190), width=2)
    
    # 门
    door_color = (140, 160, 180)
    draw.rectangle([(910, 650), (1010, 800)], fill=door_color, outline=(120, 140, 160), width=2)
    
    # 草地
    grass_color = (150, 200, 150)
    draw.rectangle([(0, 800), (width, height)], fill=grass_color)
    
    # 天空渐变
    for y in range(300):
        # 从顶部到y=300的蓝色渐变
        color = (235 - y//3, 245 - y//3, 255)
        draw.line([(0, y), (width, y)], fill=color, width=1)
    
    # 存储图像
    img.save("school_bg.jpg", quality=95)
    print("背景图像已创建: school_bg.jpg")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_school_background() 