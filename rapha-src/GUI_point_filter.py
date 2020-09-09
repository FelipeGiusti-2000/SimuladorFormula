from tkinter import *
from tkinter import filedialog
from math import *
import copy

in_file = ""
out_dir = ""

root = Tk();

FORMATS = [
        ("CSV exportado do GPS do carro?", 0),
        ("GPS Logger (.kml)", 1)
]

unfiltered_coords = []

def get_csv_filename():
    #get input csv file path
    global in_file, csv_label
    in_file = filedialog.askopenfilename(initialdir="/", title="Select CSV", filetypes=(("kml files","*.kml"),
                                                                                        ("csv files","*.csv"),
                                                                                        ("All files","*.*")))
    csv_label['text'] = in_file

def get_out_dir():
    global out_dir, out_dir_label
    out_dir = filedialog.askdirectory(initialdir="/", title="Select Output directory")
    out_dir_label['text'] = out_dir

def app_run():
    try:
        global in_file,out_dir, unfiltered_coords
        EARTH_RADIUS = 6371000

        # raw list of strings for each line
        raw_csv_strings = []
        # list of (lat, lon, alt) dictonaries converted to float 
        parsed_csv_coords = []
        print(in_file)
        print(out_dir)

        start = False

        print("Reading input file...")
        f = open(in_file, "r")


        #gps deles bom
        if (csv_format.get() == 0):
            pass
            for line in f:
                raw_csv_strings.append(line)

            if (len(raw_csv_strings) > 1):
                raw_csv_strings = raw_csv_strings[2:]
                for line in raw_csv_strings:
                    do_work = True
                    line = line[:-1]
                    data = line.split(";")
                    for d in data:
                        try:
                            float(d)
                        except ValueError:
                            #print("Not a float")
                            do_work = False
                            break
                        if (d == ""):
                            do_work = False
                            break
                    if (len(data) == 3 and do_work):
                        #add x,y,z hopefully
                        parsed_csv_coords.append(
                            {"lat" : radians(float(data[1])),
                             "lon" : radians(float(data[2])),
                             "alt" : float(data[0])})
                    else:
                        #print("Parsed more than 3 values inside coordinates\nskipping set...")
                        do_work = True
            else:
                   popupmsg("failed to read file properly")

        #gps logger (app) output .kml
        elif (csv_format.get() == 1):
            for line in f:
                if ("</coordinates>" in line):
                    start = False
                    break
                elif ("<coordinates>" in line):
                    start = True
                elif (start):
                    raw_csv_strings.append(line)

            if (len(raw_csv_strings) > 1):
                for line in raw_csv_strings:
                    do_work = True
                    line = line[:-1]
                    data = line.split(",")
                    for d in data:
                        try:
                            float(d)
                        except ValueError:
                            #print("Not a float")
                            do_work = False
                            break
                        if (d == ""):
                            do_work = False
                            break
                    if (len(data) == 3):
                        #add x,y,z hopefully
                        parsed_csv_coords.append(
                            {"lat" : radians(float(data[1])),
                             "lon" : radians(float(data[0])),
                             "alt" : float(data[2])})
                    else:
                        #print("Parsed more than 3 values inside coordinates\nskipping set...")
                        do_work = True
            else:
                popupmsg("failed to read file properly")

        f.close()

        print("Determining mean latitude...")
        min_lat = max_lat = mean_lat = 0.
        for data in parsed_csv_coords:
            if (data['lat'] < min_lat):
                min_lat = data['lat']
            elif (data['lat'] > max_lat):
                max_lat = data['lat']

        mean_lat = (max_lat + min_lat) / 2.

        print("Getting equirectangular projection of points...")

        origin = copy.deepcopy(parsed_csv_coords[0])
        #equirectangular projection
        origin['x'] = EARTH_RADIUS * origin['lon'] * cos(mean_lat)
        origin['y'] = origin['alt']
        origin['z'] = EARTH_RADIUS * origin['lat']

        unfiltered_output = open(out_dir+"/output_unfiltered.csv", "w+")
        unfiltered_output.write("x,y,z\n");


        for data in parsed_csv_coords:
            #equirectangular projection
            data['x'] = (EARTH_RADIUS * data['lon'] * cos(mean_lat))
            data['y'] = (data['alt'])
            data['z'] = (EARTH_RADIUS * data['lat'])

            #set all points in releation to the origin
            data['x'] -= origin['x']
            data['y'] -= origin['y']
            data['z'] -= origin['z']

            unfiltered_output.write(str(data['x']) +',' + str(data['y'])+',' + str(data['z']) + "\n")

        unfiltered_output.close()

        filtered_coords = []
        filtered_coords.append(parsed_csv_coords[0])

        #max_length = 20.
        #max_angle = radians(40.)
        min_dist = 5.

        #filters input coords based on difference between 
        i = 0
        h = 1
        length = len(parsed_csv_coords)
        #print(str(float(max_length_entry.get())))
        #print(str(float(max_angle_entry.get())))
        while (i+h+1 < length):
            raw_base_dv = { 'x': (parsed_csv_coords[i+h+1]['x'] - parsed_csv_coords[i]['x']),
                        'y': (parsed_csv_coords[i+h+1]['y'] - parsed_csv_coords[i]['y']),
                        'z': (parsed_csv_coords[i+h+1]['z'] - parsed_csv_coords[i]['z'])}
                    
            base_dv = { 'x': (parsed_csv_coords[i+h+1]['x'] - parsed_csv_coords[i]['x'])/ float(h),
                        'y': (parsed_csv_coords[i+h+1]['y'] - parsed_csv_coords[i]['y'])/ float(h),
                        'z': (parsed_csv_coords[i+h+1]['z'] - parsed_csv_coords[i]['z'])/ float(h)}

            dv =    {   'x': parsed_csv_coords[i+h+1]['x'] - parsed_csv_coords[i+h]['x'],
                        'y': parsed_csv_coords[i+h+1]['y'] - parsed_csv_coords[i+h]['y'],
                        'z': parsed_csv_coords[i+h+1]['z'] - parsed_csv_coords[i+h]['z']}
        
            #if (v_length(base_dv) > 0 and v_length(dv) > 0):
                #float(max_length_entry.get()
                #float(max_angle_entry.get()
            if (
                v_length(raw_base_dv) > float(min_dist_entry.get()) and 
                (v_length(raw_base_dv) > float(max_length_entry.get()) or 
                angle_between(base_dv,dv) > radians(float(max_angle_entry.get())))
            ):

                i = i+h
                h = 1
                filtered_coords.append({'x' : parsed_csv_coords[i+h]['x'],
                                        'y' : parsed_csv_coords[i+h]['y'],
                                        'z' : parsed_csv_coords[i+h]['z']})
            else:
                h = h+1   


        print("Filtered Size:\t" + str(len(filtered_coords)))
        print("Unfiltered Size:" + str(len(parsed_csv_coords)))
        print(str(float(len(filtered_coords))/float(len(parsed_csv_coords))) + "% de filtro")
        #write to csv
        filtered_out = open(out_dir+"/output_filtered.csv", "w+")
        filtered_out.write("x,y,z\n0.0,0.0,0.0\n")
        for data in filtered_coords:
            filtered_out.write(str(data['x']) + ',' + str(data['y'])+ ',' + str(data['z']) + "\n")
        filtered_out.close()

    except Exception as e:
        popupmsg("Ocorreu um Erro. Não foi possível ler e gerar os arquivos", str(e.with_traceback))



def angle_between(v1,v2):
    #print("acos( " + str(dot_product(v1,v2) / (v_length(v1) * v_length(v2))) + ")")
    return acos(clamp(dot_product(v1,v2) / (v_length(v1) * v_length(v2)), -1., 1.))
    
def dot_product(v1,v2):
    #print("dot product: " + str(float(v1['x']*v2['x'] + v1['y']*v2['y'] + v1['z']*v2['z'])))
    return float(v1['x']*v2['x'] + v1['y']*v2['y'] + v1['z']*v2['z'])

def v_length(v):
    #print("vector length:\tsqrt( " + str(v['x']**2 + v['y']**2 + v['z']**2) + ")")
    temp = sqrt(v['x']**2 + v['y']**2 + v['z']**2)
    if (temp == 0):
        temp = 1.
    return temp

def clamp(value, min,max):
    if (value > max):
        return max
    elif (value < min):
        return min
    else:
        return value

def clicked(value):
    debug_label['text'] = value
    #debug_label.pack(side=LEFT)

def popupmsg(msg, details=""):
    popup = Tk()
    popup.wm_title("!")
    label = Label(popup, text=msg, font=("Comic Sans", 20))
    label.pack(side="top", fill="x", pady=10)
    label2 = Label(popup, text=details, font=("Comic Sans", 10))
    label2.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()



csv_format = IntVar()
csv_format.set(0)
#max_length_var = DoubleVar()
#max_length_var.set(20.)
#max_angle_var = DoubleVar()
#max_angle_var.set(40.)

introLabel =    Label(root, text="Formats")

csv_btn =       Button(root, text="Escolha o csv", command=get_csv_filename)
out_dir_btn =   Button(root, text="Escolha o diretorio de output", command=get_out_dir)
app_btn =       Button(root, text="Executar", command=app_run)

csv_label =     Label(root, text="          ", bg="#ffffff")
out_dir_label = Label(root, text="          ", bg="#ffffff")

max_length_label = Label(root, text="Max Length")
max_angle_label = Label(root, text="Max Angle")
min_dist_label = Label(root, text="Min Length")

max_length_entry = Entry(root)
max_angle_entry = Entry(root)
min_dist_entry = Entry(root)


introLabel.grid     (row=0,  column=0)
for _text, _value in FORMATS:
    temp = Radiobutton(root, text=_text, variable=csv_format, value=_value)
    temp.grid(column=0)

csv_label.grid      (row=21, column=0, columnspan=1, sticky="ew")
csv_btn.grid        (row=21, column=1, columnspan=1, sticky="w")

out_dir_label.grid  (row=22, column=0, columnspan=1, sticky="ew")
out_dir_btn.grid    (row=22, column=1, columnspan=1, sticky="w")

max_length_label.grid(row=23, column=0, columnspan=1, sticky="ew")
max_angle_label.grid(row=23, column=1, columnspan=1, sticky="ew")
min_dist_label.grid(row=23, column=2, columnspan=1, sticky="ew")

max_length_entry.grid(row=24, column=0, columnspan=1, sticky="ew")
max_angle_entry.grid(row=24, column=1, columnspan=1, sticky="ew")    
min_dist_entry.grid(row=24, column=2, columnspan=1, sticky="ew")

app_btn.grid        (row=30, column=0)

root.mainloop()