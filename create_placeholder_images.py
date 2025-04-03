"""
为GUI版本创建简单角色图片占位符
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 确保assets目录存在
os.makedirs("assets", exist_ok=True)

def create_placeholder_image(filename, text, bg_color, text_color=(255, 255, 255)):
    """创建占位图像"""
    # 创建400x400的图像
    img = Image.new('RGB', (400, 400), color=bg_color)
    d = ImageDraw.Draw(img)
    
    # 尝试加载字体，使用默认字体大小
    font = ImageFont.load_default()
    
    # 添加文本
    # 兼容不同版本的PIL
    try:
        # 新版本的PIL
        text_width, text_height = d.textbbox((0, 0), text, font=font)[2:4]
    except:
        # 旧版本的PIL
        text_width, text_height = d.textsize(text, font=font)
    
    position = ((400 - text_width) // 2, (400 - text_height) // 2)
    
    # 兼容不同版本的PIL
    try:
        d.text(position, text, font=font, fill=text_color)
    except:
        d.text((position[0], position[1]), text, font=font, fill=text_color)
    
    # 保存图像
    img.save(f"assets/{filename}.png")
    print(f"Created {filename}.png")

# 创建不同情绪的角色图像
create_placeholder_image("sutang_happy", "苏糖 (非常开心)", (150, 220, 150))
create_placeholder_image("sutang_smile", "苏糖 (微笑)", (180, 230, 180))
create_placeholder_image("sutang_normal", "苏糖 (正常)", (200, 240, 200))
create_placeholder_image("sutang_neutral", "苏糖 (平静)", (220, 220, 220))
create_placeholder_image("sutang_unhappy", "苏糖 (不高兴)", (240, 180, 180))

# 创建图标
create_placeholder_image("icon", "绿园中学物语", (100, 180, 100))

print("所有占位图像已创建完成")
print("提示：这些只是示例图像，您应该替换为实际的角色图像") 