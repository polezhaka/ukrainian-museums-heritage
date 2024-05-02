from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import mpld3
import pygal
from pygal.style import BlueStyle, Style
            
# Define the custom style by inheriting from BlueStyle
custom_blue_style = BlueStyle(
    background='transparent'  # Set the background to transparent
)


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

    return render_template('index.html', data=unique_museums_with_location)


@app.route('/info_in_charts')
def info_in_charts():
    # Read the CSV file
    data = pd.read_csv('combined_data.csv')

    def create_barchart(data):
        # Group the data by "Museum Name" and count the occurrences
        museum_counts = data['Museum Name'].value_counts()

        # Set the size of the figure (width, height)
        plt.figure(figsize=(10, 6))

        # Create a bar chart
        plt.bar(museum_counts.index, museum_counts.values)

        # Rotate the x-axis labels by 45 degrees and align them to the right
        plt.xticks(rotation=45, ha='right')

        # Set the labels and title
        plt.xlabel('Museum Name')
        plt.ylabel('Кількість експонатів')
        plt.title('Розподіл кількості експонатів за музеями')

        # Save the chart as a PNG file
        chart_path = 'static/barchart.png'  # Save in the static folder
        plt.savefig(chart_path)
        
        # Convert the plot to mpld3 format
        mpld3_plot = mpld3.fig_to_html(plt.gcf())
        plt.close()  # Close the plot to free up memory

        return mpld3_plot, chart_path

    # Call the function to create the chart and get the path
    mpld3_plot, generated_chart_path = create_barchart(data)

    def create_compound_mpld3barchart(data):
        # Group the data by "Museum Name" and "Class" and count the occurrences
        museum_class_counts = data.groupby(['Museum Name', 'Class']).size().unstack(fill_value=0)

        # Calculate the total number of items in each museum
        museum_total_counts = museum_class_counts.sum(axis=1)

        # Sort museums based on total counts in descending order
        museum_total_counts_sorted = museum_total_counts.sort_values(ascending=False)

        # Sort the DataFrame based on the sorted museum names
        museum_class_counts_sorted = museum_class_counts.loc[museum_total_counts_sorted.index]

        # Set the size of the figure (width, height)
        plt.figure(figsize=(24, 12))

        # Plot stacked bars for the count of items in each museum
        museum_class_counts_sorted.plot(kind='bar', stacked=True)

        # Rotate the x-axis labels by 45 degrees and align them to the right
        #plt.xticks(rotation=90, ha='right')
        
        # Set the X-axis ticks to display museum names
        plt.xticks(range(len(museum_class_counts_sorted.index)), museum_class_counts_sorted.index, rotation=45, ha='right')

        # Set the labels and title
        plt.xlabel('Museum Name')
        plt.ylabel('Кількість експонатів')
        plt.title('Розподіл експонатів за музеями')

        # Save the chart as a PNG file
        compound_chart_path = 'static/compound_barchart.png'  # Save in the static folder
        plt.savefig(compound_chart_path)

        # Convert the plot to mpld3 format
        compound_mpld3_plot = mpld3.fig_to_html(plt.gcf())
        plt.close()  # Close the plot to free up memory

        return compound_mpld3_plot, compound_chart_path
    
    # Call the function to create the compound chart and get the path
    compound_mpld3_plot, compound_chart_path = create_compound_mpld3barchart(data)

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

    # Render the Pygal chart directly as a Base64 data URI
    #pygal_chart = pygal_bar_chart.render_response()

    # Pass the chart path and mpld3 plot to the template
    return render_template('barchart.html', mpld3_plot=mpld3_plot, chart_path=generated_chart_path, compound_mpld3_plot=compound_mpld3_plot, compound_chart_path=compound_chart_path, pygal_bar_chart=pygal_bar_chart)

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode


