#GUI Window Application for 3D scanner control
#Developer:ARV
#Component: Arduino based 3d scanner system 
#Interface: Serial Communication over USB UART COM Port



#MODULES IMPORT
import PySimpleGUI as sg
import serial
import time
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib


#INITIALIZATION COMPONENT

#Plotting variables

fig = plt.figure()
ax=plt.axes(projection='3d')
theta=np.linspace(0, 2*np.pi, 64)
delta=np.linspace(0,np.pi/4,8)
#UI variables
button_list=('CONNECT','REMOVE','SET','START','STOP','RESET','>','+','-','O','D','<')
obj_type=''




#GUI SUPPORT PROCEDURE
def bt_disable(*args):
    if args[0]=='ALL':
        for but in button_list:
            window.Element(but).update(disabled=True)
        
    else:
        for but in args:
            window.Element(but).update(disabled=True)
    window.finalize()

def bt_enable(*args):
    if args[0]=='ALL':
        for but in button_list:
            window.Element(but).update(disabled=False)
    else:
        for but in args:
            window.Element(but).update(disabled=False)
    window.finalize()
    

def ui_msg(msg):
    window.Element('-MSG-').update(msg)
    window.finalize()
    
    



#3D SCAN PROCEDURES

matplotlib.use("TkAgg") # Activate Tkinter Canvas integrate Matplot

figure_canvas_agg=None

#Delete existing plot on canvas
def delete_figure_agg(figure_agg):
        figure_agg.get_tk_widget().forget()

#Plot update on canvas
def draw_figure(canvas, figure):
    global figure_canvas_agg
    if figure_canvas_agg:
        delete_figure_agg(figure_canvas_agg)
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

#Plotting data processing function
def D3plotdata(row,ht_in,ht_fin):
    z = np.linspace(ht_in, ht_fin, 64)
    theta_grid,z_grid=np.meshgrid(theta,z)
    if obj_type=='CYLINDRICAL' or obj_type=='CYLINDRICAL\r\n':
        r=np.average(row)
    elif obj_type=='CUBIC'or obj_type=='CUBIC\r\n':
        tmp=row[::16]
        dia=np.average(tmp)
        print(dia)
        t1=dia/np.cos(delta)
        print(t1)
        t2=t1[::-1]
        t3=np.concatenate((t1,t2))
        r=np.concatenate((t3,t3,t3,t3))
    elif obj_type=='IRREGULAR' or obj_type=='IRREGULAR\r\n':
        r=np.reshape((np.repeat(row,64)),(64,64))
    x_grid = r*np.cos(theta_grid) + 0.2
    y_grid = r*np.sin(theta_grid) + 0.2
    return x_grid,y_grid,z_grid
    

#plot support function
def D3plot():
    #set plot
    plt.clf()
    ax=plt.axes(projection='3d')
    #retrieve csv file data
    with open(filename,'r',newline='') as csvf:
        next(csvf)
        data=csv.reader(csvf,quoting=csv.QUOTE_NONNUMERIC)
        h_in=0.2
        for row in data:
            x,y,z=D3plotdata(row,h_in,h_in+0.5)
            ax.plot_wireframe(x,y,z,alpha=0.1, color='r')
            #plt.draw()
            #plt.pause(0.1)
            h_in+=0.5
    return

#Scans serial port for data from 3D scanner system
def Scan():
    r=[]
    ctr=0
    r_d=''
    ST.write(b'q')
    global FL_DONE
    while ctr<64:
        r_d=ST.readline()
        val=float(r_d)
        if val<0:
            val=0
        if val>100:
            FL_DONE=True
            print('Complete')
            return
        r.append(round(val,2))
        ctr=ctr+1
    with open(filename,'a',newline='') as csvfile:
        writer=csv.writer(csvfile,delimiter=',')
        writer.writerow(r)
    D3plot()
    draw_figure(window["canvas"].TKCanvas, fig)


#GUI DESIGN

col_scan=[[sg.Button('CONNECT',button_color=('white','blue'),size=(9,2)),
           sg.Button('REMOVE',button_color=('white','red'),size=(9,2),disabled=True)],
          [sg.Text('AXIS CENTRE (0-255)',size=(16,1)),sg.Input(size=(6,1),key='-CTR-'),sg.Text('mm'),
           sg.Button('SET',button_color=('white','green'),size=(5,1),disabled=True)],[sg.Text('OBJECT TYPE',size=(12,1)),
          sg.Radio('Cylindrical',"TYPE",default=True,key='-C-',size=(12,1)),
          sg.Radio('Cubic',"TYPE",default=True,key='-S-',size=(6,1)),sg.Radio('Irregular',"TYPE",default=True,key='-I-',size=(10,1))],
          [sg.Button('START',button_color=('white','green'),size=(7,2),disabled=True),
           sg.Button('STOP',button_color=('white','red'),size=(7,2),disabled=True),
           sg.Button('RESET',button_color=('white','blue'),size=(7,2),disabled=True)]]

theta_axis=[[sg.Button('<',button_color=('black','yellow'),size=(2,1),disabled=True),
           sg.Button('>',button_color=('black','yellow'),size=(2,1),disabled=True)]]

z_axis=[[sg.Button('+',button_color=('black','yellow'),size=(2,1),disabled=True),
         sg.Button('-',button_color=('black','yellow'),size=(2,1),disabled=True),
         sg.Button('O',button_color=('black','yellow'),size=(2,1),disabled=True)]]

col_control=[[sg.Frame('\u03b8 axis',theta_axis)],[sg.Frame('Z axis',z_axis)],
             [sg.Button('D',button_color=('black','yellow'),size=(4,2),disabled=True)]]

reload_plot=[[sg.FileBrowse('Browse',initial_folder='E:\Python_files\Scan_Data',key='-FPATH-',button_color=('white','grey'),size=(7,2)),
              sg.Button('PLOT',button_color=('black','yellow'),size=(9,2),disabled=False)]]

layout=[[sg.Canvas(size=(250,250), background_color='black', key= 'canvas'),sg.Frame('SCANNER',col_scan),
         sg.Frame('CONTROL',col_control,element_justification ="center")],[sg.Frame('RE-PLOT',reload_plot)],
        [sg.Input('Please connect the device',key='-MSG-',justification='center')]]



window = sg.Window('3D SCAN', layout,return_keyboard_events=True)

#Flag Variables
FL_CON=False
FL_SCAN=False
FL_DONE=False
STOP_CD=0
init_ctr=0
z_ctr=0
STATE='STOP'

#Main processing function
while True:
    event, values = window.read(timeout=100)
    if event=='CONNECT':
        #disable connect button till connection
        bt_disable('CONNECT')
        #Establishing Serial Connection
        try:
            ST=serial.Serial('COM3',9600,timeout=5)
            FL_CON=True
        except serial.serialutil.SerialException:
            ui_msg('Error!!Device Not found, try again')
            bt_enable('CONNECT')
        if FL_CON==True:
            ui_msg('Connected!! Please wait...')
            time.sleep(10)
            ST.write(b'C')
            rcv=str(ST.readline(),encoding='ASCII')
            if rcv=='READY\r\n':
                ui_msg('Ready to Scan') 
                bt_enable('REMOVE','SET','START','STOP','RESET','>','D','+','-','O','<')
            else:
                ST.close()
                ui_msg('Error!!Device not ready, try again')
                bt_enable('CONNECT')
                FL_CON=False
    if event=='REMOVE':
        ST.close()
        ui_msg('Please connect the device')
        bt_enable('CONNECT')
        FL_CON=False
        bt_disable('REMOVE','SET','START','STOP','RESET','>','D','+','-','O','<')
    if event in (None, 'Exit'):
        break
    if event=='+':
        ST.write(b'u')
        ui_msg('Elevation Active....')
    if event=='-':
        ST.write(b'l')
        ui_msg('Delevation Active....')
    if event=='O':
        ST.write(b'p')
        ui_msg('Ready to Scan')
    if event=='>':
        ST.write(b'r')
    if event=='<':
        ST.write(b's')
    if event=='D':
        ST.write(b'd')
        rcv=ST.readline()
        msg='Distance=>'+rcv.decode()+'cm'
        ui_msg(msg)
    if event=='SET':
        ST.write(b'S')
        rcv=str(ST.readline(),encoding='ASCII')
        global cnt
        if rcv=='SET\r\n':
            cnt=bytes([int(values['-CTR-'])])
            ST.write(cnt)
            cnt=float(values['-CTR-'])/10
            ui_msg('Centre point changed')
    if event=='RESET':
        if figure_canvas_agg:
            delete_figure_agg(figure_canvas_agg)
            figure_canvas_agg=None
    if FL_SCAN==True:
        fn_ctr=time.perf_counter()
        diff=fn_ctr-init_ctr
        if diff>STOP_CD and STOP_CD==17:
            STATE='SCAN'
        elif diff>STOP_CD and STOP_CD!=17:
            ui_msg('Ready to Scan') 
            bt_enable('REMOVE','SET','START','STOP','RESET','>','D','+','-','O','<')
            FL_SCAN=False
            FL_DONE=False
            z_ctr=0
    if event=='START' or STATE=='SCAN':
        FL_SCAN=True
        if values['-C-']:
            obj_type='CYLINDRICAL'
        elif values['-S-']:
            obj_type='CUBIC'
        elif values['-I-']:
            obj_type='IRREGULAR'
        if STATE=='STOP':
            global filename
            tim=datetime.datetime.now()
            filename=tim.strftime("D%d%m%yT%H%M")
            filename='E:\Python_files\Scan_Data\SCAN_' + filename + '.csv'
            with open(filename,'w',newline='') as csvfile:
                writer=csv.writer(csvfile,delimiter=',')
                writer.writerow([obj_type])
        STATE=''
        ui_msg('Scanning Please Wait...')
        bt_disable('ALL')
        STOP_CD=17
        Scan()
        if FL_DONE==False:
            z_ctr+=1
            init_ctr=time.perf_counter()
            ui_msg('Want to terminate? Press stop')
            bt_enable('STOP')
        window.finalize()
    if event=='STOP' or FL_DONE==True:
        if FL_DONE==False:
            ST.write(b't')
        STATE='STOP'
        STOP_CD=16*z_ctr
        print(STOP_CD)
        bt_disable('STOP')
        init_ctr=time.perf_counter()
        if FL_DONE==True:
            msgE='Scan Completed...Please wait resetting'
        else:
            msgE='Scan Terminated, Please wait resetting'
        ui_msg(msgE)
        FL_DONE=False
    if event=='PLOT':
        filename=values['-FPATH-']
        with open(filename,'r',newline='') as csvf:
            obj_type=next(csvf)
        D3plot()
        draw_figure(window["canvas"].TKCanvas, fig)
        
if FL_CON==True:
    ST.close()
window.close()


    
    
    



