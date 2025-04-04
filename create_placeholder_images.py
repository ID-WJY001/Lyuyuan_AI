"""
创建placeholder图像用于开发和测试
"""

import os
from PIL import Image, ImageDraw, ImageFont

# 确保目标目录存在
target_dir = "web_app/static/images"
os.makedirs(target_dir, exist_ok=True)

def create_placeholder_image(text, size=(128, 128), color=(100, 100, 100), filename="placeholder"):
    """创建带有文字的占位图像"""
    img = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(img)
    
    # 尝试加载默认字体，如果失败则使用默认配置
    try:
        try:
            # 尝试加载中文字体
            if os.name == 'nt':  # Windows
                font = ImageFont.truetype("simhei.ttf", 16)
            else:  # macOS, Linux
                font = ImageFont.truetype("NotoSansSC-Regular.otf", 16)
        except:
            # 回退到系统默认
            font = ImageFont.load_default()
            
        # 计算文本位置以居中
        text_width, text_height = draw.textsize(text, font=font)
        position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
        draw.text(position, text, fill="white", font=font)
    except:
        # 如果字体处理有问题，使用最简单的文本绘制
        draw.text((10, 10), text, fill="white")
    
    # 保存图像
    img.save(f"{target_dir}/{filename}.png")
    print(f"创建图像: {filename}.png")

# 创建各种状态的占位图像
create_placeholder_image("笑", color=(50, 150, 50), filename="sutang_happy")
create_placeholder_image("微笑", color=(100, 150, 100), filename="sutang_smile")
create_placeholder_image("普通", color=(100, 100, 100), filename="sutang_normal")
create_placeholder_image("中性", color=(150, 150, 150), filename="sutang_neutral")
create_placeholder_image("不高兴", color=(150, 50, 50), filename="sutang_unhappy")
create_placeholder_image("图标", color=(0, 100, 200), filename="icon")

print("所有占位图像创建完成") 