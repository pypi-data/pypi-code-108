# coding=<encoding name> ： # coding=utf-8
# 参数
# --------------------------------------------------------------------------------------------------------
# 屏幕宽度，高度
# 中间区域Rect((200, 6), (900, 650))， 宽900px， 高650px。中心坐标(650, 331)
# 代表现实场景中的长3000mm， 宽2167mm
WIDTH, HEIGHT = 1300, 700
# TITLE
TITLE = '华光仿真器'
# ICON
ICON = 'hg.png'
# --------------------------------------------------------------------------------------------------------
# 主角运动速度比例(现实速度设置1，代表1mm每秒)
speed_setting = 0.0075  # 每秒40帧，则有0.0075*40 = 0.3px每秒 = 1mm每秒
mm_convert_px = 0.3
px_convert_mm = 3.33
# --------------------------------------------------------------------------------------------------------
# 场景矩形————用于检测碰撞(也就是用于框住所有场景中存在的物体)
scene0 = []
scene1 = [((193, 52), (550-193, 584-52)), ((755, 10), (1104-755, 587-10))]  # 红外场景
scene2 = [((193, 9), (574-193, 123-9)), ((479, 106), (552-479, 178-106)),
          ((720, 11), (1099-720, 106-11)), ((794, 145), (1101-794, 174-145)),
          ((889, 272), (960-889, 340-272)), ((236, 199), (360-236, 380-199)),
          ((361, 192), (415-361, 277-192)), ((194, 399), (570-194, 653-399)),
          ((732, 407), (1101-732, 652-407))]  # 超声波场景
scene3 = [((195, 11), (575-195, 655-11)), ((198, 12), (876-198, 49-12)),
          ((1044, 8), (1100-1044, 120-8)), ((1020, 140), (1099-1020, 256-140)),
          ((722, 254), (1104-722, 652-254)), ((694, 66), (765-694, 135-66)),
          ((587, 62), (695-587, 135-62))]  # 简单运动
scene4 = []
scene5 = []
scene6 = []
scene7 = []
scene8 = []
scene9 = []
scene10 = []
# 角色，背景，赛道、障碍、物品或其他图像的名称与坐标或RGB(传感器不存放在这)
elements = {'actors': {'默认': ['actors/car', (360, 370)],
                       0: ['actors/car', (650, 331)],
                       1: ['actors/car', (660, 610)],
                       2: ['actors/car', (650, 331)],
                       3: ['actors/car', (650, 610)],
                       },
            'interfaces': {0: ['interfaces/interface_none', (0, 0)],
                           1: ['interfaces/interface1', (0, 0)],
                           2: ['interfaces/interface2', (0, 0)]
                           },
            'levels': {'默认': ['levels/level', (190, 6), scene0],
                       0: ['levels/level_none', (190, 6), scene0],
                       1: ['levels/level1', (200, 6), scene1],  # 红外场景
                       2: ['levels/level2', (190, 6), scene2],  # 超声波场景
                       3: ['levels/level3', (190, 6), scene3],  # 简单运动
                       4: ['levels/level4', (190, 6), scene4],  #
                       5: ['levels/level5', (190, 6), scene5],  #
                       6: ['levels/level6', (190, 6), scene6],  #
                       7: ['levels/level7', (190, 6), scene7],  #
                       8: ['levels/level8', (190, 6), scene8],  #
                       9: ['levels/level9', (190, 6), scene9],  #
                       10: ['levels/level10', (190, 6), scene10],  #

                       },
            'racetracks': {0: ['racetracks/none', (0, 0)],
                           1: ['racetracks/racetrack1', (300, 80)],
                           2: ['racetracks/racetrack2', (320, 150)]
                           },
            'others': {0: ['others/none', (0, 0)],
                       1: ['others/obstacle1', (500, 500)],
                       2: ['others/obstacle2', (600, 400)]
                       }
            }
# --------------------------------------------------------------------------------------------------------
# 仿真界面所有固定及关联坐标点
hardware_pos_pic_right = {1: (1235, 70), 2: (1235, 200), 3: (1235, 330), 4: (1235, 460), 5: (1235, 590)}
hardware_pos_name_right = {key: (1225, hardware_pos_pic_right[key][1] + 56)
                           for key, a in hardware_pos_pic_right.items()}
io_pwm_pos_right = {key: [(hardware_pos_pic_right[key][0] - 102, hardware_pos_pic_right[key][1] - 45),
                          (hardware_pos_pic_right[key][0] - 102, hardware_pos_pic_right[key][1] - 20)]
                    for key, b in hardware_pos_pic_right.items()}
return_data_pos_right = {key: [(hardware_pos_pic_right[key][0] - 102, hardware_pos_pic_right[key][1] + 24),
                               (hardware_pos_pic_right[key][0] - 102, hardware_pos_pic_right[key][1] + 48)]
                         for key, c in hardware_pos_pic_right.items()}
return_data_pos_right_other = {key: [(hardware_pos_pic_right[key][0] - 5, hardware_pos_pic_right[key][1] - 24),
                                     (hardware_pos_pic_right[key][0] - 5, hardware_pos_pic_right[key][1] + 24)]
                               for key, e in hardware_pos_pic_right.items()}
# 以下待开发使用
hardware_pos_pic_left = {1: (71, 55), 2: (71, 225), 3: (71, 380)}
hardware_pos_name_left = {'csb': (71, 55 + 65), 'motor': (71, 225 + 70), 'wheel': (71, 380 + 78)}
return_data_pos_left = {key: [(hardware_pos_pic_left[key][0] + 96, hardware_pos_pic_left[key][1] - 20),
                              (hardware_pos_pic_left[key][0] + 96, hardware_pos_pic_left[key][1] + 20)]
                        for key, d in hardware_pos_pic_left.items()}
# 文本框位置
texts_pos = {0: (96, 485), 1: (96, 510), 2: (96, 533),
             3: (96, 559), 4: (96, 582), 5: (96, 605)
             }
# (1: [(60, 510), (140, 510)],
# 2: [(60, 533), (140, 533)],
# 3: [(75, 559), (150, 559)],
# 4: [(75, 582), (150, 582)],
# 5: [(75, 605), (150, 605)])
texts_pos_sitting = {'文本框': texts_pos[0],
                     '场景长宽约: 3m*2m': texts_pos[1],
                     '前进速度(mm/s): ': texts_pos[2],
                     '当前温度(℃): ': texts_pos[3],
                     '当前湿度(%): ': texts_pos[4]
                     }
# 输入框位置
input_pos = {'设置温度': [(203, 666), (170, 20)],
             '设置湿度': [(203+170, 666), (170, 20)]
             }
# --------------------------------------------------------------------------------------------------------
