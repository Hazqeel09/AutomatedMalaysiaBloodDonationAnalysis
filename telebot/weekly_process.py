import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from io import BytesIO
import itertools

def corr_matrix(df, col_name):
    pivoted_data = df.pivot(index='date', columns=col_name, values='daily')

    corr_matrix = pivoted_data.corr()

    avg_corr = corr_matrix.mean().sort_values()

    top_3 = avg_corr.tail(3).index.tolist()
    bottom_3 = avg_corr.head(3).index.tolist()
    return top_3, bottom_3


def donation_amnt(donate_state):
    malaysia_donation = donate_state[donate_state.state == "Malaysia"]

    # Find the latest available date in the dataset
    latest_date = malaysia_donation['date'].max()

    prev_week = latest_date - pd.Timedelta(days=6)

    # Filter data for the current week
    this_weeks_data = malaysia_donation[(malaysia_donation['date'] >= prev_week) & 
                                        (malaysia_donation['date'] <= latest_date)]

    # Filter data for the latest available date
    todays_data = malaysia_donation[malaysia_donation['date'] == latest_date]

    # Extract blood type columns
    blood_type_columns = ['blood_a', 'blood_b', 'blood_o', 'blood_ab']

    week_colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightsalmon']
    today_colors = ['blue', 'green', 'red', 'salmon']

    plt.figure(figsize=(12, 8))

    for i, blood_type in enumerate(blood_type_columns):

        type_of_blood = blood_type.split("_")[-1].upper()

        # This week's data
        week_values = this_weeks_data[blood_type].values
        plt.bar(type_of_blood, week_values.sum(), color=week_colors[i], label=f'This Week {type_of_blood}', bottom=0)
        
        # Today's data
        today_values = todays_data[blood_type].values
        plt.bar(type_of_blood, today_values, color=today_colors[i], label=f'Today {type_of_blood}', bottom=0)

    plt.title(f"This Week [{prev_week.strftime('%d-%m-%Y')} - {latest_date.strftime('%d-%m-%Y')}] and Today [{latest_date.strftime('%d-%m-%Y')}] Blood Donation", fontsize=15)
    plt.xlabel('Blood Type', fontsize=12)
    plt.ylabel('Number of Donations', fontsize=12)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_stream = BytesIO()
    plt.savefig(plot_stream, format="png", bbox_inches="tight")
    plot_stream.seek(0)
    plt.close()

    return plot_stream, f"This Week\n[{prev_week.strftime('%d-%m-%Y')} - {latest_date.strftime('%d-%m-%Y')}]\nand\nToday\n[{latest_date.strftime('%d-%m-%Y')}]\nBlood Donation"


def donation_by_state(donate_state):
    latest_date = donate_state['date'].max()

    prev_week = latest_date - pd.Timedelta(days=6)

    # Filter data for the current week
    this_weeks_data = donate_state[(donate_state['date'] >= prev_week) & 
                                        (donate_state['date'] <= latest_date)]
    
    top_3, bottom_3 = corr_matrix(this_weeks_data, "state")

    least_similar_message = (
        f"Top 3 states with the least similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(bottom_3)
            ]
        )
    )

    most_similar_message = (
        f"Top 3 states with the most similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(top_3)
            ]
        )
    )

    corr_matrix_message = f"{least_similar_message}\n\n{most_similar_message}"

    markers = ['o','*', '+', 'x']

    # Set up a grid for the subplots
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(5, 1, height_ratios=[1, 1, 1, 1, 1]) 

    # Creating subplots
    ax4 = plt.subplot(gs[0])  # Top subplot
    ax3 = plt.subplot(gs[1], sharex=ax4)
    ax2 = plt.subplot(gs[2], sharex=ax4)
    ax1 = plt.subplot(gs[3], sharex=ax4)
    ax0 = plt.subplot(gs[4], sharex=ax4)  # Bottom subplot

    num_states = len(donate_state["state"].unique())
    cmap = plt.get_cmap("gnuplot2")

    for i, state in enumerate(donate_state["state"].unique()):
        color = cmap((i / (num_states - 1)) * 0.8)
        marker = markers[i % len(markers)]
        y = this_weeks_data[this_weeks_data.state == state].daily.values
        x = this_weeks_data[this_weeks_data.state == state].date.values

        ax0.plot(x, y, marker=marker, color=color, label=state)
        ax1.plot(x, y, marker=marker, color=color)
        ax2.plot(x, y, marker=marker, color=color)
        ax3.plot(x, y, marker=marker, color=color)
        ax4.plot(x, y, marker=marker, color=color, label=state)

        ax0.set_ylim(0, 100)
        ax1.set_ylim(100, 500)
        ax2.set_ylim(500, 1000)
        ax3.set_ylim(1000, 3000)
        ax4.set_ylim(3000, 5000)

        ax0.grid(True)
        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)
        ax4.grid(True)

    # Hide x labels and tick labels for all but the bottom plot
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax4.get_xticklabels(), visible=False)

    fig.suptitle('This Week Donations by State')
    plt.xlabel('Date')
    ax4.legend(loc='upper left',bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    plt.tight_layout(rect=[0, 0, 0.85, 1]) 
    plt.subplots_adjust(hspace=.0, right=0.75)
    
    plot_stream = BytesIO()
    plt.savefig(plot_stream, format="png", bbox_inches="tight")
    plot_stream.seek(0)
    plt.close()

    return plot_stream, f"This Week Donations by State\n\n{corr_matrix_message}"

def regular_donation_by_state(donate_state):
    latest_date = donate_state['date'].max()

    prev_week = latest_date - pd.Timedelta(days=6)

    # Filter data for the current week
    this_weeks_data = donate_state[(donate_state['date'] >= prev_week) & 
                                        (donate_state['date'] <= latest_date)]
    
    top_3, bottom_3 = corr_matrix(this_weeks_data, "state")

    least_similar_message = (
        f"Top 3 states with the least similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(bottom_3)
            ]
        )
    )

    most_similar_message = (
        f"Top 3 states with the most similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(top_3)
            ]
        )
    )

    corr_matrix_message = f"{least_similar_message}\n\n{most_similar_message}"

    markers = ['o','*', '+', 'x']

    # Set up a grid for the subplots
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(5, 1, height_ratios=[1, 1, 1, 1, 1]) 

    # Creating subplots
    ax4 = plt.subplot(gs[0])  # Top subplot
    ax3 = plt.subplot(gs[1], sharex=ax4)
    ax2 = plt.subplot(gs[2], sharex=ax4)
    ax1 = plt.subplot(gs[3], sharex=ax4)
    ax0 = plt.subplot(gs[4], sharex=ax4)  # Bottom subplot

    num_states = len(donate_state["state"].unique())
    cmap = plt.get_cmap("gnuplot2")

    for i, state in enumerate(donate_state["state"].unique()):
        color = cmap((i / (num_states - 1)) * 0.8)
        marker = markers[i % len(markers)]
        y = this_weeks_data[this_weeks_data.state == state].donations_regular.values
        x = this_weeks_data[this_weeks_data.state == state].date.values

        ax0.plot(x, y, marker=marker, color=color, label=state)
        ax1.plot(x, y, marker=marker, color=color)
        ax2.plot(x, y, marker=marker, color=color)
        ax3.plot(x, y, marker=marker, color=color)
        ax4.plot(x, y, marker=marker, color=color, label=state)

        ax0.set_ylim(0, 20)
        ax1.set_ylim(20, 50)
        ax2.set_ylim(50, 100)
        ax3.set_ylim(100, 500)
        ax4.set_ylim(500, 3000)

        ax0.grid(True)
        ax1.grid(True)
        ax2.grid(True)
        ax3.grid(True)
        ax4.grid(True)

    # Hide x labels and tick labels for all but the bottom plot
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax4.get_xticklabels(), visible=False)

    fig.suptitle('This Week Regular Donors Donations based on State')
    plt.xlabel('Date')
    ax4.legend(loc='upper left',bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    plt.tight_layout(rect=[0, 0, 0.85, 1]) 
    plt.subplots_adjust(hspace=.0, right=0.75)
    
    plot_stream = BytesIO()
    plt.savefig(plot_stream, format="png", bbox_inches="tight")
    plot_stream.seek(0)
    plt.close()

    return plot_stream, f"This Week Regular Donors Donations based on State\n\n{corr_matrix_message}"

def donation_by_facility(weekly_data):
    # Extract unique dates from the weekly data
    unique_dates = weekly_data['date'].unique()
    unique_dates = np.sort(unique_dates)
    unique_dates = pd.to_datetime(unique_dates)

    top_3, bottom_3 = corr_matrix(weekly_data, "hospital")

    least_similar_message = (
        f"Top 3 facilities with the least similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(bottom_3)
            ]
        )
    )

    most_similar_message = (
        f"Top 3 facilities with the most similar correlations to all others:\n"
        + "".join(
            [
                f"{idx+1}. {state}\n" for idx, state in enumerate(top_3)
            ]
        )
    )

    corr_matrix_message = f"{least_similar_message}\n\n{most_similar_message}"

    markers = itertools.cycle(("+", "o", "*", "s", "x", "D", "^"))
    line_styles = itertools.cycle((":", "-.", "-"))

    cmap = plt.get_cmap("gnuplot2")

    plt.figure(figsize=(16, 8))

    # Create the primary y-axis
    ax1 = plt.gca()
    ax1.set_ylabel("Blood Donations (Normal Range)")

    # Create the secondary y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel("Blood Donations (Large Range)")

    num_hospitals = len(weekly_data["hospital"].unique())

    for i, hospital in enumerate(weekly_data["hospital"].unique()):
        color_index = i / (num_hospitals - 1) * 0.85

        hospital_data = weekly_data[weekly_data["hospital"] == hospital]

        # Plotting for each hospital
        if hospital == "Pusat Darah Negara":
            # Plot on secondary y-axis
            ax2.plot(
                hospital_data.date,
                hospital_data["daily"],
                label=hospital + " (Large Range)",
                color="red",
                linestyle="-",
                marker="x",
            )
        else:
            # Plot on primary y-axis
            ax1.plot(
                hospital_data.date,
                hospital_data["daily"],
                label=hospital,
                color=cmap(color_index),
                marker=next(markers),
                linestyle=next(line_styles),
            )

    # Plot settings
    plt.title("This Week Blood Donation based on Facility")
    plt.xlabel("Date")
     # Set x-ticks to be the unique dates
    ax1.set_xticks(unique_dates)
    ax1.set_xticklabels([date.strftime('%d-%m-%Y') for date in unique_dates], rotation=45)  # Formatting date and rotating labels for readability
    # ax1.set_xticks(range(1, 8))  # Set x-ticks to be each month
    ax1.grid(True)

    # Adjust primary axis legend (outside the plot)
    ax1.legend(loc="upper left", bbox_to_anchor=(1.15, 1), borderaxespad=0.0)

    # Adjust secondary axis legend (inside the plot)
    ax2.legend(loc="upper right")

    # Adjust the layout to make room for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the rect parameter as needed

    plot_stream = BytesIO()
    plt.savefig(plot_stream, format="png", bbox_inches="tight")
    plot_stream.seek(0)
    plt.close()

    return plot_stream, f"This Week Blood Donation based on Facility\n\n{corr_matrix_message}"
