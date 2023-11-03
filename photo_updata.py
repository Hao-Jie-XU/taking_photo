from PIL import Image, ImageDraw, ImageFont
import os

def copy_photo(value,photo_name,photo_str):
    #水印文字
    text = value

    folder_name = photo_name
    time_str = photo_str
    original_name = folder_name + '/' +time_str + '.bmp'
    new_name = folder_name + '/' +time_str + '_' + text + '.bmp'


    # 原照片路径
    original_image_path = original_name
    # 重命名后的照片路径
    new_image_path = new_name
    # 打开原照片
    image = Image.open(original_image_path)
    # 创建一个可编辑的图像副本
    image_copy = image.copy()
    # 为图像副本创建一个绘制对象
    draw = ImageDraw.Draw(image_copy)

    font_name = r'C:\Windows\Fonts\msyh.ttc'
    # 设置水印文字的字体和大小
    font = ImageFont.truetype(font_name, size=100)# 替换为你自己的字体路径和大小

    # 计算水印文字的位置（居中位置）
    x = image_copy.width - 200
    y = 50
    # 在图像副本上添加水印文字
    if text == 'OK':
        draw.text((x, y), text, font=font, fill=(255, 0, 0, 0))
    else :
        draw.text((x, y), text, font=font, fill=(0, 255, 0, 0))
    # 保存新图像副本
    image_copy.save(new_image_path)
    # 删除原照片
    os.remove(original_image_path)