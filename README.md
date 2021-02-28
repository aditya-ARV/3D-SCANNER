# 3D-SCANNER
Scans and plot the object surface morphology with lower resolution on python based window GUI application

The project comprises of two component 
1. Hardware Unit (Arduino Based) 3D scanner
2. Software GUI application (Python)

The interface between GUI and hardware is over USB_TTL port

Hardware Unit 

It need to be built using stepper motor, IR distance sensor, DC linear actuator(custom built), arduino UNO board and mechanix tool set.
Images are provided for reference

Software GUI

Python simple GUI based design.
Need to update scan folder in main processing function under "START and PLOT" event if conditions (default to my machine) for saving scanned data



