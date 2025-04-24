import os
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave


def setup_fmu2_slave(fmu_path, unzip_directory="unzip_dir"):
    """
    Set up and initialize an FMU using fmpy for FMI 2.0 (FMU2Slave).

    Parameters:
        fmu_path (str): Path to the FMU file.
        unzip_directory (str): Directory to extract the FMU. Default is 'unzip_dir'.

    Returns:
        model_description: The parsed model description.
        fmu2_slave: The initialized FMU2Slave instance.
        unzip_dir: The directory where the FMU was extracted.
    """

    # Step 1: Read the model description
    model_description = read_model_description(fmu_path)

    # Step 2: Extract the FMU
    unzip_dir = os.path.abspath(extract(fmu_path, unzip_directory))
    #unzip_dir = os.path.abspath(extract(fmu_file_path))

    # Ensure binaries path exists
    
    current_time = 0.0
    stop_time = 3.0
    step_size = 1e-1

    # Step 3: Instantiate the FMU2Slave
    fmu2_slave = FMU2Slave(
        guid=model_description.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=model_description.coSimulation.modelIdentifier,
        instanceName="instance1"
    )  


    fmu2_slave.instantiate()
    fmu2_slave.setupExperiment(startTime=0.0, stopTime=3)
    fmu2_slave.enterInitializationMode()
    fmu2_slave.exitInitializationMode()

    #fmu2_slave.doStep(currentCommunicationPoint=0, communicationStepSize=1e-2)
    

    print("FMU2Slave setup complete.")
    h_ref = None
    for variable in model_description.modelVariables:
        if variable.name == 'h':  # Look for the variable named 'h'
            h_ref = variable.valueReference
            break

    if h_ref is None:
        raise ValueError("Variable 'h' not found in the FMU model description.")


    while current_time < stop_time - step_size:
        fmu2_slave.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)
        #
        h_value = fmu2_slave.getReal([h_ref])[0]
        # print("Current height:", h_value)
    #    fmu2_slave.setReal([h_ref], [10])
        current_time += step_size
        

    return model_description, fmu2_slave, unzip_dir

# Example usage (replace 'your_model.fmu' with the actual FMU file path):
if __name__ == "__main__":
    fmu_file_path = "BouncingBall.fmu"  # Replace this with your FMU file

    if not os.path.exists(fmu_file_path):
        print(f"Error: FMU file '{fmu_file_path}' not found.")
    else:
        try:
            model_desc, fmu2, extract_dir = setup_fmu2_slave(fmu_file_path)
            # print("Model Name:", model_desc.modelName)
            # print("Extracted to:", extract_dir)
            fmu2.terminate()
            fmu2.freeInstance()
        except Exception as e:
            print("An error occurred:", e)