from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import mpld3
import pygal
from pygal.style import BlueStyle, Style
from dotenv import load_dotenv
import os
            
# Define the custom style by inheriting from BlueStyle
custom_blue_style = BlueStyle(
    background='transparent'  # Set the background to transparent
)

# Load environment variables from .env file
load_dotenv()

matplotlib.use('Agg')

app = Flask(__name__)

@app.route('/')
def index():
    # Read the original CSV file
    original_data = pd.read_csv('combined_data.csv')

    # Group the original data by "Museum Name" and count the number of items for each museum
    items_by_museums = original_data.groupby('Museum Name').size().reset_index(name='ItemCount')

    # Merge the grouped data with the original data to get the "Latitude" and "Longitude" columns
    items_with_location = pd.merge(items_by_museums, original_data[['Museum Name', 'Latitude', 'Longitude']].drop_duplicates(), on='Museum Name', how='left')

    # Drop duplicates to ensure unique museums
    unique_museums_with_location = items_with_location.drop_duplicates(subset=['Museum Name', 'Latitude', 'Longitude'])

    # Convert the unique museums data to a DataFrame
    unique_museums_with_location_df = pd.DataFrame(unique_museums_with_location)

    # Save the DataFrame to a CSV file
    unique_museums_with_location_df.to_csv('unique_museums_with_location.csv', index=False)

    mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

    return render_template('index.html', data=unique_museums_with_location, mapbox_access_token=mapbox_access_token)


@app.route('/info_in_charts')
def info_in_charts():
    # Read the CSV file
    data = pd.read_csv('combined_data.csv')

    def create_compound_Pygal_barchart(data):
        # Group the data by "Museum Name" and "Class" and count the occurrences
        museum_class_counts = data.groupby(['Museum Name', 'Class']).size().unstack(fill_value=0)

        # Calculate the total number of items in each museum
        museum_total_counts = museum_class_counts.sum(axis=1)

        # Sort museums based on total counts in descending order
        museum_total_counts_sorted = museum_total_counts.sort_values(ascending=False)

        # Sort the DataFrame based on the sorted museum names
        museum_class_counts_sorted = museum_class_counts.loc[museum_total_counts_sorted.index]

        # Convert index to list for Pygal
        x_labels_major = museum_class_counts_sorted.index.tolist()

        # Create a Pygal bar chart
        pygal_bar_chart = pygal.StackedBar(
            x_label_rotation=-45,
            height=600,
            width=1200,
            rounded_bars=2,
            margin=10,
            title='Розподіл експонатів за музеями',
            #x_title='Museum Name',
            y_title='Кількість експонатів',
            style=custom_blue_style,  # Customize the chart style
            show_x_labels=False  # Hide x-axis labels
            #truncate_label=-1
        )
        pygal_bar_chart.x_labels = x_labels_major
        

        # Add data to the bar chart
        for column in museum_class_counts_sorted.columns:
            pygal_bar_chart.add(column, museum_class_counts_sorted[column])
        
        #pygal_bar_chart.render_to_file('chart-insideAFn.svg')
        pygal_bar_chart = pygal_bar_chart.render_data_uri()
        return pygal_bar_chart

    # Create the pygal barchart
    pygal_bar_chart = create_compound_Pygal_barchart(data)

    # Pass the chart path and mpld3 plot to the template
    return render_template('barchart.html', pygal_bar_chart=pygal_bar_chart)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode


