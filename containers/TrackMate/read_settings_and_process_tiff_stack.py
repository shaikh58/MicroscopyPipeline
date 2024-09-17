import os
import sys
# from time import sleep

from java.io import File
from java.lang import System

from ij import IJ
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.io import TmXmlReader, TmXmlWriter, CSVExporter


# We have to do the following to avoid errors with UTF8 chars generated in
# TrackMate that will mess with our Fiji Jython.
reload(sys)
sys.setdefaultencoding("utf-8")

# -----------------
# Read data stack
# -----------------
segmented_path = "/Volumes/talmo/mustafa/TrackMate-Python/simulated-segmented"
tracked_path = "/Volumes/talmo/mustafa/TrackMate-Python/tracked-simulated-segmentations"
settings_path = "/Users/main/Documents/GitHub/MicroscopyPipeline/models/trackmate/trackmate_settings_lysosomes.xml"
# settings_path = "/Users/mustafashaikh/Documents/mot/MicroscopyPipeline/models/trackmate/trackmate_settings_lysosomes.xml"

for segmented_file in os.listdir(segmented_path):
    if not segmented_file.endswith(".tif"):
        continue
    # Get currently selected image
    print(segmented_file)
    imp = IJ.openImage(os.path.join(segmented_path,segmented_file))
    print("data read successfully")

    # -----------------
    # Read settings from XML
    # -----------------
    print("Reading settings from: " + settings_path)
    file = File(settings_path)
    reader = TmXmlReader(file)
    if not reader.isReadingOk():
        sys.exit(reader.getErrorMessage())
    print("Settings read successfully")
    # -----------------
    # Get a full model
    # -----------------

    model = reader.getModel()
    model.setLogger(Logger.IJ_LOGGER)

    settings = reader.readSettings(imp)

    # -------------------
    # Instantiate plugin
    # -------------------

    trackmate = TrackMate(model, settings)

    # --------
    # Process
    # --------
    # sleep(360)
    ok = trackmate.checkInput()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))

    ok = trackmate.process()
    if not ok:
        sys.exit(str(trackmate.getErrorMessage()))

    # Echo results with the logger we set at start:
    model.getLogger().log(str(model))

    # --------
    # Write Results
    # --------
    print("writing results.xml")
    f = File(os.path.join(tracked_path, segmented_file[:-4]+ ".xml"))
    xml_writer = TmXmlWriter(f)

    xml_writer.appendModel(model)
    xml_writer.appendSettings(settings)
    xml_writer.writeToFile()
    print("finished writing results.xml")

    print("writing results.csv")
    reader = TmXmlReader(f)
    model = reader.getModel()
    out_file_csv = os.path.join(tracked_path, segmented_file[:-4]+ ".csv")
    only_visible = True
    CSVExporter.exportSpots( out_file_csv, model, only_visible )

System.exit(0)
