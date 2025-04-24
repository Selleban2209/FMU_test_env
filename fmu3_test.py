import os
import sys
from fmpy import read_model_description, extract
from fmpy.fmi3 import FMU3Slave  # Use FMU3Slave for FMI 3.0
from fmpy.fmi3 import printLogMessage
#from fmu_logger import setup_logging
import logging
import re 


ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def setup_logging():
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler('fmu_simulation.log'),  # Log file
            logging.StreamHandler()                     # Console
        ]
    )
    return logging.getLogger()

logger = setup_logging()

def custom_logger(instance_environment ,status, category, message):
    """Redirect FMI logs to Python's logging system."""
    # Map FMI status to Python log levels
    if isinstance(category, bytes):
        category = category.decode('utf-8')
    if isinstance(message, bytes):
        message = message.decode('utf-8')
    
    # Remove ANSI escape sequences
    #clean_message = ansi_escape.sub('', message)
    level_mapping = {
        'OK': logging.INFO,
        'Warning': logging.WARNING,
        'Error': logging.ERROR,
        'Fatal': logging.CRITICAL
    }
    #print("status: ", status)
    log_level = level_mapping.get(status, logging.INFO)
    
    logger.log(log_level, f"[{category}] {message}")

def setup_fmu3_slave(fmu_path, unzip_directory="unzip_dir"):
    """
    Set up and initialize an FMU using fmpy for FMI 3.0 (FMU3Slave).

    Parameters:
        fmu_path (str): Path to the FMU file.
        unzip_directory (str): Directory to extract the FMU. Default is 'unzip_dir'.

    Returns:
        model_description: The parsed model description.
        fmu3_slave: The initialized FMU3Slave instance.
        unzip_dir: The directory where the FMU was extracted.
    """
 
    # Step 1: Read the model description
    model_description = read_model_description(fmu_path)

    # Step 2: Extract the FMU
    unzip_dir = os.path.abspath(extract(fmu_path, unzip_directory))

    # Ensure binaries path exists
    current_time = 0.0
    stop_time = 1.0
    step_size = 1e-1
    log_level=2
    # Step 3: Instantiate the FMU3Slave
    fmu3_slave = FMU3Slave(
        guid=model_description.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=model_description.coSimulation.modelIdentifier,
        instanceName="instance1",

       
    )  
    
    vrs = {var.name: var.valueReference for var in model_description.modelVariables}
    #print( "vsr: ", vrs)
    #print("Extracted to:" + unzip_dir)
    fmu3_slave.instantiate(
        loggingOn=True,  # Enable FMU logging
        logMessage=custom_logger  # Use our custom logger
    )
    
    fmu3_slave.setString([vrs['rtlola_spec']], ["specifications/bouncing_ball_spec.lola", "h"])
    fmu3_slave.enterInitializationMode(startTime=0.0, stopTime=stop_time)
    fmu3_slave.exitInitializationMode()

    print("FMU3Slave setup complete.")
    h_ref = None
    spec_ref = None
    
    # Step 4: Set up the FMU3Slave and run the simulation
    flip = False 
    while current_time < stop_time - step_size:
        fmu3_slave.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)
        #print(f"FMU State After doStep: {fmu3_slave.state}")  # Print FMU state after stepping
        h_value = fmu3_slave.getFloat64([vrs['h']])[0]
        #print("Current height:", h_value)
        
        raw = fmu3_slave.getString([vrs["rtlola_output"]])[0]
        #print("Raw output:", raw)
        if not flip:
            #fmu3_slave.setFloat64([vrs['h']], [10])
            fmu3_slave.setString([vrs['rtlola_spec']], ["specifications/new_ball_spec.lola", "h", "v"])
            flip = True
        #print("Current height:", h_value)
        print()
       
        current_time += step_size
    
    return model_description, fmu3_slave, unzip_dir

# Example usage (replace 'your_model.fmu' with the actual FMU file path):
if __name__ == "__main__":
    # Set up logging
   
    
    fmu_file_path = "BouncingBall.fmu"
    
    if not os.path.exists(fmu_file_path):
        print(f"Error: FMU file '{fmu_file_path}' not found.")
    else:
        try:
            model_desc, fmu3, extract_dir = setup_fmu3_slave(fmu_file_path)
            print("Model Name:", model_desc.modelName)
            print("Extracted to:", extract_dir)
        except Exception as e:
            print("An error occurred:", e)
        finally:    
            fmu3.terminate()
            fmu3.freeInstance()
    