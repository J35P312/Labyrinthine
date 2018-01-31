from PIL import Image, ImageDraw, ImageFont
import sys
import math
#arg 1 input file
#arg 2 = label
#arg 3 output prefix

#Jesper EIsfeldt
#make bezier and pascal row was copied from user unutbu:http://stackoverflow.com/questions/246525/how-can-i-draw-a-bezier-curve-using-pythons-pil

def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n-1)
    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t**i for i in range(n))
            upowers = reversed([(1-t)**i for i in range(n)])
            coefs = [c*a*b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef*p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result
    return bezier

def pascal_row(n):
    # This returns the nth row of Pascal's Triangle
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n//2+1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n&1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result)) 
    return result

ref={}
ref_pos=[]
rea = {}
rea_pos=[]
links=[]

header_string=sys.argv[2]

table=0
segment_number=0
ref_number=0
for line in open(sys.argv[1]):
    content=line.strip().split("\t")
    if len(content) == 1:
            content=line.strip().split(",")
    if line[0] == "#":
        table += 1
        continue
    #get rid of empty rows in the table
    if line.strip().replace("\t","") == "":
        continue
    #get rid of empty rows in the table
    if line.strip().replace(",","") == "":
        continue
    print content
    print table
    if table == 1:
        ref_pos.append(content[0])
        ref[content[0]]={ "chrA":content[1],"posA":content[2],"posB":content[4],"chrB":content[3],"variant_type":content[-1],"length":content[5],"segment_number":segment_number }
        segment_number += 1
    elif table ==2:
        
        links.append( {"link_start_id":content[-2],"link_end_id":content[-1],"link_id":content[0],"link_orientation_1":content[4],"link_orientation_2":content[8]} )
    elif table == 3:
        rea_pos.append(ref_number)
        rea[ref_number]={"id":content[0],"chrA":content[1],"posA":content[2],"posB":content[4],"chrB":content[3],"variant_type":content[-1]}
        ref_number +=1


segments_to_draw=max([segment_number,ref_number])
x_margin=200
y_margin=300
x=3000
y=1600
tick_len=50
link_heigth =10*tick_len
scale=1000000

start_pos=x_margin
x_range=x-x_margin*2
image = Image.new('RGB', (x, y),(256,256,256))

font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 80)
draw = ImageDraw.Draw(image)
w, h = draw.textsize(header_string)
draw.text( ( int((x)/2-4*w) , int(y_margin/4)), "{}".format(header_string),font=font, fill=(0,0,0))

#draw.line( (x_margin, y_margin+link_heigth, x-x_margin, y_margin+link_heigth), fill = (0,0,0),width=4 )
#draw.line( (x_margin, y-y_margin, x-x_margin, y-y_margin), fill = (0,0,0),width=4 )
pos_vector=[]
font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 80)
line_width=10
for variant in ref_pos:
    colour = (0,0,0)
    if "del" in ref[variant]["variant_type"] or "Del" in ref[variant]["variant_type"]:
            colour = (255,0,0)
    elif "inv" in ref[variant]["variant_type"] or "Inv" in ref[variant]["variant_type"]:
        colour = (0,0,255)
    elif "dup" in ref[variant]["variant_type"] or "Dup" in ref[variant]["variant_type"]:
        colour = (0,255,0)
    elif "None" in ref[variant]["variant_type"] or "none" in ref[variant]["variant_type"]:
        end_pos=start_pos+int( x_range/segments_to_draw)
        pos_vector.append([start_pos,end_pos])
        start_pos=end_pos
        continue

    end_pos=start_pos+int( x_range/segments_to_draw)
    draw.line( (start_pos, y_margin+link_heigth, end_pos, y_margin+link_heigth), fill = colour,width=line_width )
    if variant != ref_pos[0] and variant!= ref_pos[-1]:
        draw.line( (start_pos, y_margin-tick_len+link_heigth, start_pos, y_margin+tick_len+link_heigth), fill = (0,0,0),width=line_width )
        draw.line( (end_pos, y_margin-tick_len+link_heigth, end_pos, y_margin+tick_len+link_heigth), fill = (0,0,0),width=line_width )
    draw.text( ( start_pos+int((end_pos - start_pos)/2) , y_margin+2*tick_len+link_heigth), "{}".format(variant),font=font, fill=(0,0,0))

    if variant != ref_pos[-1]:
        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 50)
        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 80)
    else:
        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 50)


    if "inv" in ref[variant]["variant_type"] or "Inv" in ref[variant]["variant_type"]:
        draw.line( (start_pos+int((end_pos-start_pos)/4), y_margin+link_heigth-int(tick_len/2), end_pos-int((end_pos-start_pos)/4) , y_margin+link_heigth-int(tick_len/2)), fill = (0,0,0),width=6 )    
        x_start_pos=start_pos+int((end_pos-start_pos)/4)
        x_end_pos=start_pos+int((end_pos-start_pos)/2)
        increment=abs((tick_len/2.0-tick_len/3.0)/len(range(x_start_pos,x_end_pos)))

        j=0
        m=y_margin+link_heigth-int(tick_len/2)
        print x_start_pos
        for i in range(x_start_pos,x_end_pos):
            y_start_pos=int(round(m-j*increment))
            y_end_pos=int(round(m+j*increment))
            #print y_end_pos
            draw.line( (i, y_start_pos, i, y_end_pos), fill = (0,0,0),width=8)
            j +=1



    pos_vector.append([start_pos,end_pos])
    start_pos=end_pos
rea_len=0
for i in range(0,len(pos_vector)):
    variant=ref_pos[i]
    if variant in rea_pos:
        rea_len += pos_vector[i][1]-pos_vector[i][0]

start_pos=int(x-(ref_number*(x_range/segments_to_draw) ))/2

for k in range(0,len(rea_pos)):
    variant=rea[k]["id"]
    colour = (0,0,0)
    #if "del" in ref[variant]["variant_type"] or "Del" in ref[variant]["variant_type"]:
    if "del" in rea[k]["variant_type"].lower():
        colour = (255,0,0)
    elif "inv" in ref[variant]["variant_type"] or "Inv" in ref[variant]["variant_type"]:
        colour = (0,0,255)
    elif "dup" in ref[variant]["variant_type"] or "Dup" in ref[variant]["variant_type"]:
        colour = (0,255,0)
    elif "None" in ref[variant]["variant_type"] or "none" in ref[variant]["variant_type"]:
        end_pos=start_pos+int( x_range/segments_to_draw)
        start_pos=end_pos
        continue
    end_pos=start_pos+int( x_range/segments_to_draw)
    spacer=False
    if k < ref_number-1:
        if rea[k+1]["variant_type"] == "None":
            spacer=True
    
    draw.line( (start_pos,  y-y_margin, end_pos, y-y_margin), fill = colour,width=line_width )
    if k != 0 and variant!= rea_pos[-1]:

        draw.line( (start_pos, y-y_margin-tick_len, start_pos, y-y_margin+tick_len), fill = (0,0,0),width=line_width )

        
    if k < ref_number-1 and not spacer:

        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 50)
        w, h = draw.textsize(str("{} {}".format(int(int(ref[variant]["posB"])/scale),int(int(rea[rea_pos[k+1]]["posA"])/scale))),font = font)

        draw.line( (end_pos, y-y_margin-tick_len, end_pos, y-y_margin+tick_len), fill = (0,0,0),width=line_width )
    else:
        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 50)

    if "inv" in rea[k]["variant_type"] or "Inv" in rea[k]["variant_type"]:
        draw.line( (start_pos+int((end_pos-start_pos)/4),  y-y_margin-int(tick_len/2), end_pos-int((end_pos-start_pos)/4) ,  y-y_margin-int(tick_len/2)), fill = (0,0,0),width=6 )    
        x_start_pos=start_pos+int((end_pos-start_pos)/4)
        x_end_pos=start_pos+int((end_pos-start_pos)/2)
        increment=abs((tick_len/2.0-tick_len/3.0)/len(range(x_start_pos,x_end_pos)))

        j=0
        m= y-y_margin-int(tick_len/2)
        for i in range(x_start_pos,x_end_pos):
            y_start_pos=int(round(m-j*increment))
            y_end_pos=int(round(m+j*increment))
            #print y_end_pos
            draw.line( (i, y_start_pos, i, y_end_pos), fill = (0,0,0),width=8)
            j +=1


    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMonoBold.ttf", 80)
    draw.text( ( start_pos+int((end_pos - start_pos)/2) , y-y_margin+2*tick_len), "{}".format(variant),font=font, fill=(0,0,0))
    start_pos=end_pos

for link in links:

    index= 0
    if "end" in link["link_start_id"].split(":")[-1]:
        index = 1

    segment= ref[ link["link_start_id"].split(":")[0] ]["segment_number"]
    start=pos_vector[ segment  ][ index ]

    index= 0
    if "end" in link["link_end_id"].split(":")[-1]:
        index = 1
    print link["link_end_id"].split(":")[0]
    segment= ref[ link["link_end_id"].split(":")[0] ]["segment_number"]
    end=pos_vector[ segment  ][ index ]
    sample_link_heigth=link_heigth
    if link_heigth > (end-start):
        sample_link_heigth= link_heigth/2


    ts = [t/10300.0 for t in range(10301)]

    xys = [(start,y_margin-tick_len+link_heigth),(start, y_margin-tick_len-sample_link_heigth+link_heigth),(end, y_margin-tick_len-sample_link_heigth+link_heigth),(end, y_margin-tick_len+link_heigth)]
    bezier = make_bezier(xys)
    points = bezier(ts)
    j=0
    draw_line = True
    px_lim=20
    dist=0
    for i in range(0,len(points)-1):
        if draw_line:
            draw.line( (points[i][0], points[i][1], points[i+1][0], points[i+1][1]), fill = (0,0,0),width=line_width )

        dist += math.sqrt( math.pow((points[i][0]-points[i+1][0]),2) + math.pow((points[i][1]-points[i+1][1]),2)  )
        if dist > px_lim:
            if draw_line:
                draw_line = False
            else:
                draw_line = True
            dist = 0

    #draw.text( ( start+int( (end-start)/2), y_margin-tick_len-int(0.95*sample_link_heigth)+link_heigth), "{}".format(link["link_id"]),font=font, fill=(0,0,0))
    #draw.text( ( start-10, y_margin+2*tick_len+link_heigth), "{}".format(link["link_orientation_1"]),font=font, fill=(0,0,0))
    #draw.text( ( end-10 ,  y_margin+2*tick_len+link_heigth), "{}".format(link["link_orientation_2"]),font=font, fill=(0,0,0))

x_start=x-x_margin-200
x_end=x-x_margin-100
draw.line( (x_start, int(y_margin/4), x_end , int(y_margin/4) ), fill = (0,255,0),width=line_width )
draw.text( (x_end+10 , int(y_margin/4)-40 ),"Dup", font=font, fill=(0,0,0))
draw.line( ( x_start, 2*int(y_margin/4), x_end, 2*int(y_margin/4)), fill = (255,0,0),width=line_width )
draw.text( ( x_end+10 , 2*int(y_margin/4)-40 ), "Del",font=font, fill=(0,0,0))
draw.line( (x_start, 3*int(y_margin/4),x_end, 3*int(y_margin/4)), fill = (0,0,255),width=line_width )
draw.text( ( x_end+10 , 3*int(y_margin/4)-40 ), "Inv" ,font=font, fill=(0,0,0))
draw.line( (x_start, 4*int(y_margin/4),x_end, 4*int(y_margin/4)), fill = (0,0,0),width=line_width )
draw.text( ( x_end+10 , 4*int(y_margin/4)-40 ), "Normal" ,font=font, fill=(0,0,0))
draw.line( (x_start, 5*int(y_margin/4),x_start+int((x_end-x_start)/7), 5*int(y_margin/4)), fill = (0,0,0),width=line_width )
draw.line( (x_start+2*int((x_end-x_start)/7), 5*int(y_margin/4),x_start+3*int((x_end-x_start)/7), 5*int(y_margin/4)), fill = (0,0,0),width=line_width )
draw.line( (x_start+4*int((x_end-x_start)/7), 5*int(y_margin/4),x_start+5*int((x_end-x_start)/7), 5*int(y_margin/4)), fill = (0,0,0),width=line_width )
draw.line( (x_start+6*int((x_end-x_start)/7), 5*int(y_margin/4),x_start+7*int((x_end-x_start)/7), 5*int(y_margin/4)), fill = (0,0,0),width=line_width )
draw.text( ( x_end+10 , 5*int(y_margin/4)-40 ), "Links" ,font=font, fill=(0,0,0))
image.save("{}.png".format(sys.argv[3]), "PNG")



