import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import getpass
import xlsxwriter
import xlrd
import yaml
import os
import csv


def CheckIfReportExist(path, filename):
    ReportCols=Config["ReportCols"]
    file=path+filename
    if os.path.exists(path):
        if os.path.exists(file):
            pass
        else:
            with open(file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(ReportCols)
        pass
    else:
        os.makedirs(path)
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(ReportCols)

#event methods
def on_created(event):
    with open(report,'a') as f:
        writer = csv.writer(f)

        writer.writerow([Config["Action_Create"], getpass.getuser(), event.src_path, f"{event.src_path} has been modified", "by:",getpass.getuser()])
    print(f"{event.src_path} has been created!", "by:", getpass.getuser())

def on_deleted(event):
    with open(report,'a') as f:
        writer = csv.writer(f)
        writer.writerow([Config["Action_Delete"], getpass.getuser(), event.src_path, f"{event.src_path} has been modified", "by:",getpass.getuser()])
    print(f"{event.src_path} has been deleted", "by:", getpass.getuser() )

def on_modified(event):
    with open(report, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([Config["Action_Modify"], getpass.getuser(), event.src_path, f"{event.src_path} has been modified", "by:", getpass.getuser()])
    print(f"{event.src_path} has been modified", getpass.getuser())

def on_moved(event):
    with open(report, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([Config["Action_Move"], getpass.getuser(), event.src_path, f"{event.src_path} has been modified", "by:",getpass.getuser()])
    print(f"moved {event.src_path} to {event.dest_path}", getpass.getuser())


def CreateObserver(my_event_handler, path, recursive):
    print("start observer for: ", path)
    my_observer.schedule(my_event_handler, path, recursive=recursive)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
    my_observer.join()

if __name__ == "__main__":

    #Events Handler
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved


    #import config
    with open(r'Config.yaml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        Config = yaml.load(file, Loader=yaml.FullLoader)

    #set configurations
    paths=Config["Filesystem"]
    report=Config["ReportDir"]+Config["csvFile"]
    CheckIfReportExist(Config["ReportDir"], Config["csvFile"])

    #Observer

    observers=[]
    my_observer = Observer()
    for path in paths:
        my_observer.schedule(my_event_handler, path, recursive=True)
        observers.append(path)

    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for o in observers:
            o.unschedule_all()
            o.stop()
    for o in observers:
        o.join()
