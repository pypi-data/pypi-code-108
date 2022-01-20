from MyQR import myqr

words = "http://kw618.xyz" # 黑点密集多比较合适
words = "http://kw618.xyz/price/detail?house_id=HZZRGY0818218414_02"  # 黑点密集度有点偏高了

def make_qrcode(words, save_name="t1.jpg", save_dir=FILE_PATH_FOR_DESKTOP):
    "生成二维码; (如果http开头, 扫描后会自动跳转到该页面)"
    myqr.run(
    	words, # words 的字符数越多, 二维码越复杂, 黑点越多
        version=1, # version 的数值越大, 二维码越复杂, 黑点越多
        level='L', # 从L/M/Q/H顺序, 字母越靠右, 二维码越复杂, 黑点越多 (L是最简单的)
        picture=None,
        colorized=False,
        contrast=1.0,
        brightness=1.0,
        # save_name="kw_v1.jpg",
        save_name=save_name,
        save_dir=save_dir,
    )




# # 网上的案例
# # =================
# myqr.run(
#     words='http://www.baidu.com',
#     # 扫描二维码后，显示的内容，或是跳转的链接
#     version=5,  # 设置容错率
#     level='H',  # 控制纠错水平，范围是L、M、Q、H，从左到右依次升高
#     picture='test.gif',  # 图片所在目录，可以是动图
#     colorized=False,  # 黑白(False)还是彩色(True)
#     contrast=1.0,  # 用以调节图片的对比度，1.0 表示原始图片。默认为1.0。
#     brightness=1.0,  # 用来调节图片的亮度，用法同上。
#     save_name='test_qrcode2.gif',  # 控制输出文件名，格式可以是 .jpg， .png ，.bmp ，.gif
# )
# # 如果不设置这个save_name参数，并且也不想生成图片、动态二维码时，默认生成的图片名称为qrcode.png
# # 如果不设置这个save_name参数，并且加了picture参数，如test.gif，生成的即为test_qrcode.gif，如test.jpg，生成的即为test_qrcode.jpg
# # 报错：Wrong picture! Input a filename that exists and be tailed with one of {'.jpg', '.png', '.bmp', '.gif'}!
# # 解决方案：picture与save_name 设置一致




#
