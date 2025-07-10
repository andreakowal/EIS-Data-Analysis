#Take membrane ID string from Drop Exp. and return a dictionary populated with the relevant conditions

def parse_drop_file_id(id: str = ""):

    #split the ID string at _
    parts = id.split("_")


    if len(parts) == 10: #With drop concentration
        soak_conc_raw = parts[0]
        salt = parts[1]
        drop_conc_raw = parts[2]
        membrane_id= parts[3]
        replicate_raw = parts[4]
        membrane = parts[5]
        date_raw = parts[6]
        drop_conc = drop_conc_raw.replace("p", ".").replace("M", " M").replace("D", "")  #clean up drop conc

    else: #Without drop concentration
        drop_conc = None
        soak_conc_raw = parts[0]
        salt = parts[1]
        membrane_id = parts[2]
        replicate_raw = parts[3]
        membrane = parts[4]
        date_raw = parts[5]

    #Cleaning up to make it look nicer
    soak_conc = soak_conc_raw.replace("p", ".").replace("M", " M")
    replicate = replicate_raw.replace("R", "")
    date = f"{date_raw[4:6]}/{date_raw[6:]}/{date_raw[:4]}"
    
    #Building dictionary in desired order
    return_dict = {"Salt": salt, "Membrane": membrane,
    "Membrane ID": membrane_id,
    "Replicate": replicate,
    "Soak Concentration (M)": soak_conc,}
    
    if drop_conc is not None:
        return_dict["Drop Concentration (M)"] = drop_conc
    
    return_dict["Date"] = date
    
    return return_dict

#test run
#print(parse_drop_file_id("0p1M_NaCl_D0p1M_01_R1_FAS50_20250407_C01_GEIS_C01.mpt")) 