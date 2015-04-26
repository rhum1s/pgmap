# -*- coding:utf-8 -*-
# R. Souweine, 2015

import os

os.chdir("../")
os.system("python config.py")
os.system("python pg.py")
os.system("python geo_df_utils.py")
os.system("python draw_map.py")