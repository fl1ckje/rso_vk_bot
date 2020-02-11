# # import asyncio
# #
# #
# # async def hello():
# #     print('Hello ...')
# #     await asyncio.sleep(5)
# #     print('... World!')
# #
# #
# # async def main():
# #     await asyncio.gather(hello(), hello())
# #
# #
# # asyncio.run(main())
#
# from PIL import Image
#
# try:
#     original = Image.open('downloads/185255580.png', 'r')
#     frame = Image.open('frames/Общая 1.png', 'r')
#     if original.size[1] < original.size[0]:
#         print('Фото не вертикальное!')
#     original = original.convert('RGBA')
#     frame = frame.convert('RGBA')
#     # изменение размеров фото и рамки
#     new_original_size, new_frame_size = (), ()
#     if original.size[0] > frame.size[0]:
#         new_original_size = (frame.size[0], int(frame.size[0] * original.size[1] / original.size[0]))
#         new_frame_size = frame.size
#         original = original.resize(new_original_size, Image.BICUBIC)
#     elif original.size[0] == frame.size[0]:
#         new_original_size = original.size
#         new_frame_size = frame.size
#     elif original.size[0] < frame.size[0]:
#         new_original_size = original.size
#         new_frame_size = (original.size[0], int(original.size[0] * frame.size[1] / frame.size[0]))
#         frame = frame.resize(new_frame_size, Image.BICUBIC)
#     # изменение размеров фото и рамки
#
#     # смещение фото и рамки
#     original_offset = (0, 0)
#     v_offset = 94
#     frame_offset = (0, new_original_size[1] - v_offset)
#     # смещение фото и рамки
#
#     # общее изображение для фото и рамки
#     new_image_size = (new_original_size[0], new_original_size[1] + new_frame_size[1] - v_offset)
#     new_image = Image.new('RGBA', new_image_size, (255, 255, 255, 0))
#     new_image.paste(original, original_offset)
#     new_image.paste(frame, frame_offset, mask=frame)
#     new_image.save('edited/185255580.png')
#     print('Размер оригинала после (w*h): ' + str(new_original_size))
#     print('Размер рамки после (w*h): ' + str(new_frame_size))
#     print('Размер оригинала с рамкой (w*h): ' + str(new_image_size))
# except FileNotFoundError:
#     print('Файл не найден')
