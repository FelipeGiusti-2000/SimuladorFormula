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
    in_file = filedialog.askopenfilename(initialdir="./", title="Select CSV", filetypes=(("kml files","*.kml"),
                                                                                        ("csv files","*.csv"),
                                                                                        ("All files","*.*")))
    csv_label['text'] = in_file

def get_out_dir():
    global out_dir, out_dir_label
    out_dir = filedialog.askdirectory(initialdir="./", title="Select Output directory")
    out_dir_label['text'] = out_dir

def app_run():

    global in_file,out_dir, unfiltered_coords
    EARTH_RADIUS = 6371000

    # raw list of strings for each line
    raw_csv_strings = []
    # list of (lat, lon, alt) dictonaries converted to float 
    parsed_csv_coords = []
    print(in_file)
    print(out_dir)

    start = False
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

    min_lat = max_lat = mean_lat = 0.
    for data in parsed_csv_coords:
        if (data['lat'] < min_lat):
            min_lat = data['lat']
        elif (data['lat'] > max_lat):
            max_lat = data['lat']

    mean_lat = (max_lat + min_lat) / 2.

    origin = copy.deepcopy(parsed_csv_coords[0])
    #equirectangular projection
    origin['x'] = EARTH_RADIUS * origin['lon'] * cos(mean_lat)
    origin['y'] = origin['alt']
    origin['z'] = EARTH_RADIUS * origin['lat']

    unfiltered_output = open(out_dir+"/unfiltered_output.csv", "w+")
    unfiltered_output.write("x,y,z\n");

    print(str(origin['x'])+" , " + str(origin["y"])+","+ str(origin['z'])+"\n")

    for data in parsed_csv_coords:
        data['x'] = (EARTH_RADIUS * data['lon'] * cos(mean_lat))
        data['y'] = (data['alt'])
        data['z'] = (EARTH_RADIUS * data['lat'])

        data['x'] -= origin['x']
        data['y'] -= origin['y']
        data['z'] -= origin['z']
        print("data - origem: " + str(data['x']) + "-" + str(origin['x']) + " = " + str(data['x']-origin['x']))

        #print(str(data['x']) +',' + str(data['y'])+',' + str(data['z']) + "\n")
        unfiltered_output.write(str(data['x']) +',' + str(data['y'])+',' + str(data['z']) + "\n")

    unfiltered_output.close()




    

def clicked(value):
    debug_label['text'] = value
    #debug_label.pack(side=LEFT)

def popupmsg(msg):
    popup = Tk()
    popup.wm_title("!")
    label = Label(popup, text=msg, font=("Comic Sans", 20))
    label.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()



csv_format = IntVar()
csv_format.set(0)

introLabel =    Label(root, text="Formats")

csv_btn =       Button(root, text="Escolha o csv", command=get_csv_filename)
out_dir_btn =   Button(root, text="Escolha o diretorio de output", command=get_out_dir)
app_btn =       Button(root, text="Executar", command=app_run)

csv_label =     Label(root, text="          ", bg="#ffffff")
out_dir_label = Label(root, text="          ", bg="#ffffff")


introLabel.grid     (row=0,  column=0)
for _text, _value in FORMATS:
    temp = Radiobutton(root, text=_text, variable=csv_format, value=_value)
    temp.grid(column=0)

csv_label.grid      (row=21, column=0, columnspan=1, sticky="ew")
csv_btn.grid        (row=21, column=1, columnspan=1)

out_dir_label.grid  (row=22, column=0, columnspan=1, sticky="ew")
out_dir_btn.grid    (row=22, column=1, columnspan=1)

app_btn.grid        (row=23, column=0)

root.mainloop()