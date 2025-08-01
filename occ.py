#This code will find the y-offset for the open circuit correction (OCC)
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from glitch.impedance import EISSpectrumDoc

OCC_results = []

#Parse ID to extract thickness, concentration, and date
def parse_OCC_file_id(id: str = ""):

    #Split string at _
    parts = id.split("_")

    if len(parts) == 7:
        thickness_raw = parts[0]
        concentration_raw = parts[1]
        date_raw = parts[3]
    else: 
        print("Cannot parse file")
        return None, None, None


    #Clean up ID
    thickness = thickness_raw.replace("p", ".").replace("mm", " mm")
    concentration = concentration_raw.replace("p", ".").replace("M", " M NaCl")
    date = f"{date_raw[4:6]}/{date_raw[6:]}/{date_raw[:4]}"
    
    return thickness, concentration, date

INPUT_FOLDER = "/Users/andreakowal/Downloads/"
OUTPUT_FOLDER = "/Users/andreakowal/Coding/OCC"

#Data folder path
data_folder = Path(INPUT_FOLDER + "OCC/0.05 M NaCl").expanduser() 

#Short circuit correction files
SC_path = Path(INPUT_FOLDER + "OCC/07_29_25_SCTest_C01.mpt").expanduser()
sc = EISSpectrumDoc.from_eclab_mpt(SC_path)

#Processing .mpt files
for file_path in data_folder.glob("*.mpt"):
    print(f"Processing {file_path.name}")

    thickness, concentration, date = parse_OCC_file_id(file_path.stem)

    my_spectrum = EISSpectrumDoc.from_eclab_mpt(file_path)
    my_spectrum.background_correct(scc=sc.cycles_raw[0])

    #Plot
    fig = go.Figure()

    #Create empty lists to store values
    all_reals = []
    all_imags = []
    all_freqs = []

    #Go through loops in data file 
    for i, cycle in enumerate(my_spectrum.cycles_raw):
        mask = cycle.frequencies <= 100_000 #filtering out high frequencies
        freqs_filtered = cycle.frequencies[mask]
        impedance_filtered = cycle.impedance[mask]

        Z_real = impedance_filtered.real
        Z_imag = impedance_filtered.imag

        if i == 0:
            all_freqs = freqs_filtered #store frequenices

        all_reals.append(Z_real)
        all_imags.append(Z_imag)

        #Plot data for each loop
        fig.add_trace(go.Scatter(
                x=Z_real,
                y=Z_imag,
                mode='markers',
                name=f'Loop {i+1}'))
        
    #Average points across loops
    real_array = np.vstack(all_reals)
    imags_array = np.vstack(all_imags)

    average_real = np.mean(real_array, axis = 0)
    average_imaginary = np.mean(imags_array, axis = 0)

   #Find lowest x and y
    min_index = np.argmin(average_imaginary)
    min_x = average_real[min_index]
    min_y = average_imaginary[min_index]

    #Save OCC results
    OCC_results.append(({
        "Thickness (mm)": thickness,
        "Concentration (M)": concentration,
        "Lowest X (Ohm)": min_x,
        "Lowest Y (Ohm)": min_y
    }))
    #Add averaged points to plot
    fig.add_trace(go.Scatter(
        x = average_real,
        y = average_imaginary,
        mode = 'markers',
        name = 'Average',
        marker = dict(color="black", size = 6, symbol = "circle")))
    
    #Create graph title
    graph_title = f"{thickness} | {concentration}<br><span style='font-size:14px'>{date}</span>"

    fig.update_layout(
        title= graph_title,
        xaxis_title='Re{Z} (Ohm)',
        yaxis_title='-Im{Z} (Ohm)',
        xaxis=dict(scaleanchor="y", scaleratio=1),
        width=700,
        height=600)

    fig.show()
    
#Create final data table with values
df_results = pd.DataFrame(OCC_results).sort_values(by="Thickness (mm)")
print(df_results)


#Convert thickness from string to numeric value
df_results["Thickness"] = (
    df_results["Thickness (mm)"].str.replace(" mm", "", regex=False).astype(float))

#Create y-Offset vs. Thickness (mm) graph
y_offset_fig = go.Figure()
y_offset_fig.add_trace(go.Scatter(
    x = df_results["Thickness"],
    y = df_results["Lowest Y (Ohm)"],
    mode = 'markers+lines'
))

y_offset_fig.update_layout(
    title = f"{df_results['Concentration (M)'].iloc[0]} OCC y-Offset",
    xaxis_title = "Thickness (mm)",
    yaxis_title = "y-Offset (Ohm)",
    width = 700,
    height = 600)

#Create linear trendline for y-Offset
x = df_results["Thickness"]
y = df_results["Lowest Y (Ohm)"]

if x.size < 2:
    print("Need at least two points to fit a line")

#Fit y = mx*b
m, b = np.polyfit(x, y, 1)

#Compute R^2
y_hat = m * x + b
ss_res = np.sum((y - y_hat)**2)
ss_tot = np.sum((y - np.mean(y))**2)
r2 = 1 - ss_res/ss_tot if ss_tot > 0 else np.nan

line_x = np.linspace(x.min(), x.max(), 100)

line_y = m*line_x + b

y_offset_fig.add_trace(go.Scatter(
    x=line_x,
    y=line_y,
    mode='lines',
    name=f"Linear fit (R²={r2:.4f})",
    line = dict(color = "black", dash = "dash", width = 2)
))

y_offset_fig.show()

#Predict y-Offset for a given thickness

def predict_y_offset(membrane_thickness):
    return m * membrane_thickness + b

thickness = 0.067 

y_offset = (predict_y_offset(thickness))

print(f"The y offset for {thickness:g} mm is {y_offset:.6g} Ohms")

