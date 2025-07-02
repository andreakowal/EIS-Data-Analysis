
 #Take membrane ID string and return a dictionary populated with the relevant conditions

def parse_mem_id(id: str = ""):

    #split the ID string at _
    parts = id.split("_")

    #splitting the soaking concentration from the salt
    soak_conc_raw = parts[0]
    molar_index = soak_conc_raw.find("M")
    if molar_index != -1:
        soak_conc = soak_conc_raw[:molar_index + 1]
        salt = soak_conc_raw[molar_index + 1:]
    else:
        soak_conc = soak_conc_raw
        salt = "None"

    if len(parts) == 7: #With dip concentration
        dip_conc_raw = parts[1]
        membrane_id_raw = parts[2]
        replicate_raw = parts[3]
        membrane = parts[4]
        date_raw = parts[5]
        dip_conc = dip_conc_raw.replace("p", ".").replace("M", " M").replace("D", "")  #clean up dip conc

    else: #Without dip concentration
        dip_conc = None
        membrane_id_raw = parts[1]
        replicate_raw = parts[2]
        membrane = parts[3]
        date_raw = parts[4]

    #Cleaning up to make it look nicer
    soak_conc_clean = soak_conc.replace("p", ".").replace("M", " M")
    membrane_id = membrane_id_raw.replace("M", "")
    replicate = replicate_raw.replace("R", "")
    date = f"{date_raw[4:6]}/{date_raw[6:]}/{date_raw[:4]}"
    
    #Building dictionary in desired order
    return_dict = {"Salt": salt, "Membrane": membrane,
    "Membrane ID": membrane_id,
    "Replicate": replicate,
    "Soak Concentration (M)": soak_conc_clean,}
    
    if dip_conc is not None:
        return_dict["Dip Concentration (M)"] = dip_conc
    
    return_dict["Date"] = date
    
    return return_dict

#print(parse_mem_id("40mMCoCl2_M02_R1_FKS50_20250424_C01")) 