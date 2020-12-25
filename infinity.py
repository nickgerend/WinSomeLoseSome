# Written by: Nick Gerend, @dataoutsider
# Viz: "Win Some, Lose Some", enjoy!

import numpy as np
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from math import pi, cos, sin, exp
#pd.set_option('display.max_columns', None)

class point:
    def __init__(self, index, item, side, circle, category, catnum, catcount, x, y, path = -1, value = -1): 
        self.index = index
        self.item = item
        self.side = side
        self.circle = circle
        self.category = category
        self.catnum = catnum
        self.catcount = catcount
        self.x = x
        self.y = y
        self.path = path
        self.value = value       
    def to_dict(self):
        return {
            'index' : self.index,
            'item' : self.item,
            'side' : self.side,
            'circle' : self.circle,
            'category' : self.category,
            'catnum' : self.catnum,
            'catcount' : self.catcount,
            'x' : self.x,
            'y' : self.y,
            'path' : self.path,
            'value' : self.value }

def vertical_sigmoid(i, count, x1, y1, x2, y2):
    dx = abs(x2-x1)
    dy = abs(y2-y1)
    xamin = (1-1.0)*(12.0/(count-1.0))-6.0
    amin = 1.0/(1.0+exp(-xamin))
    xamax = (count-1.0)*(12.0/(count-1.0))-6.0
    amax = 1.0/(1.0+exp(-xamax))
    da = amax-amin

    xi = (i-1.0)*(12.0/(count-1.0))-6.0
    a = ((1.0/(1.0+exp(-xi)))-amin)/da
    x = a * dx + x1
    y = ((i-1.0)*(dy/(count-1.0))-(dy/2.0))+dy/2+y1
    if x2 < x1:
        x -= dx
        y = ((dy/2.0)-y)-(dy/2.0)+y1+y2
    return x, y

#region input
df = pd.read_csv(os.path.dirname(__file__) + '/Shark Tank Companies.csv', engine='python')
df.reset_index(inplace = True)
df['index'] = df['index'] + 1
df = df.sort_values(['season', 'episode'], ascending=[True, True])
df.to_csv(os.path.dirname(__file__) + '/test_meta.csv', encoding='utf-8', index=False)
#endregion

#region epsnum
df['epsnum'] = 0
last_season = 1
total_eps = 0
last_episode = 1
for i, row in df.iterrows():
    if row['season'] != last_season:
        total_eps += last_episode
    df.at[i, 'epsnum'] = row['episode']+total_eps
    last_episode = row['episode']
    last_season = row['season']
print(df)
#endregion

#region algorithm
binary_group_column = 'deal'
df_group = df.groupby([binary_group_column])

ratio = 0.75
outerstep = ratio/(df['epsnum'].max()/2)
offset_inner = 2.0 #1
offset_outer = 0.0

list_xy = []
innerx = 0.
outerx = (1-ratio)
x_inner = 0
x_outer = 0
y_inner = 0
y_outer = 0
it = 0
sign = 1
sigmoid_count = 500
x = 0
y = 0
cat_num = 1
for name, group in df_group:
    #items = group['index'].count()
    categories = len(group['category'].unique())
    innerstep = 1/categories
    y_inner = offset_inner*sign
    y_outer = offset_outer*sign
    for cat, catg in group.groupby(['category']):
        x_inner = innerx
        innerx += innerstep
        for i, row in catg.iterrows():
            index = it
            side = name
            category = cat
            val = row['valuation']
            eps = row['epsnum']
            
            x_outer = (1.-ratio)+(eps)*outerstep

            if i+1 == 55 and name == False:
                test = 1

            for j in range(sigmoid_count):
                if sign == 1:
                    x, y = vertical_sigmoid(j+1, sigmoid_count, x_outer, y_outer, x_inner, y_inner)
                else:
                    x, y = vertical_sigmoid(j+1, sigmoid_count, x_inner, y_inner, x_outer, y_outer)
                list_xy.append(point(i+1, eps, name, 'sigmoid', category, cat_num, categories, x, y, j, val))
            
            # list_xy.append(point(i+1, name, 'inner', category, x_inner, y_inner, 0, val))
            # list_xy.append(point(i+1, name, 'outer', category, x_outer, y_outer, 1, val))

            # list_xy.append(point(i+1, name, 'inner', 'point1', x_inner, y_inner, 0, val))
            # list_xy.append(point(i+1, name, 'outer', 'point2', x_outer, y_outer, 0, val))

            it += 1
        cat_num += 1
    sign *= -1
    cat_num = 1

df_out = pd.DataFrame.from_records([s.to_dict() for s in list_xy])
df_out.to_csv(os.path.dirname(__file__) + '/test.csv', encoding='utf-8', index=False)
df_out_btm = df_out.loc[df_out['x']>=1]
df_out_top = df_out.loc[df_out['x']<1]
offset_ring = 4
df_out_top['y'] = -df_out['y']+offset_ring
df_out_btm['y'] = df_out['y']+offset_ring
#df_out.to_csv(os.path.dirname(__file__) + '/test.csv', encoding='utf-8', index=False)
#endregion

#region translate and write
offset = 0.0
import csv
import os
with open(os.path.dirname(__file__) + '/test.csv', 'w',) as csvfile:
    writer = csv.writer(csvfile, lineterminator = '\n')
    writer.writerow(['index', 'item', 'side', 'circle', 'category', 'x', 'y', 'path', 'value'])
    for i, row in df_out_btm.iterrows():
        t = row['x']
        ch1 = row['y']
        angle = (2.*pi)*(row['x'])
        angle_deg = angle * 180./pi
        angle_rotated = (abs(angle_deg-360.)+90.) % 360.
        angle_new = angle_rotated * pi/180.
        x = (offset+ch1)*cos(angle_new)
        y = (offset+ch1)*sin(angle_new)
        writer.writerow([row['index'], row['item'], row['side'], row['circle'], row['category'], x, y, row['path'], row['value']])
    for i, row in df_out_top.iterrows():
        t = row['x']
        ch1 = row['y']
        angle = (2.*pi)*(row['x'])
        angle_deg = angle * 180./pi
        angle_rotated = (abs(angle_deg-360.)+90.) % 360.
        angle_new = angle_rotated * pi/180.
        x = (offset+ch1)*cos(angle_new)
        y = (offset+ch1)*sin(angle_new)
        writer.writerow([row['index'], row['item'], row['side'], row['circle'], row['category'], -x, -y + offset_ring*2, row['path'], row['value']])
#endregion

print('finished')