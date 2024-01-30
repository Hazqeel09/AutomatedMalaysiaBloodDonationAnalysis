import pandas as pd
import itertools
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime


def create_message(df, year):
    df["daily"] = pd.to_numeric(df["daily"], errors="coerce")

    # Resample and aggregate by month for the specific year
    yearly_data = df[df.index.year == year]
    monthly_sums = yearly_data.resample("ME").sum()

    # Calculate month-over-month changes
    monthly_changes = (
        monthly_sums["daily"].diff().iloc[1:]
    )  # Skip the NaN value for the first month

    top_declines = monthly_changes.nsmallest(3, keep="first")
    top_increases = monthly_changes.nlargest(3, keep="first")

    decline_message = (
        f"Top 3 months with the most significant declines in donations for {year}:\n"
        + "".join(
            [
                f"{idx+1}. {month.strftime('%B')} ({change:+.0f})\n"
                for idx, (month, change) in enumerate(top_declines.items())
            ]
        )
    )

    increase_message = (
        f"Top 3 months with the most significant increases in donations for {year}:\n"
        + "".join(
            [
                f"{idx+1}.{month.strftime('%B')} ({change:+.0f})\n"
                for idx, (month, change) in enumerate(top_increases.items())
            ]
        )
    )

    return f"{decline_message}\n{increase_message}"


def create_image_and_captions(df):
    images_and_captions = []

    df["daily"] = pd.to_numeric(df["daily"], errors="coerce")

    current_year = datetime.now().year
    start_year = current_year - 6
    df = df[df["date"].dt.year >= start_year]

    # Set the date as the index
    df.set_index("date", inplace=True)

    markers = itertools.cycle(("+", "o", "*", "s", "x", "D", "^"))
    line_styles = itertools.cycle((":", "-.", "-"))

    cmap = plt.get_cmap("gnuplot2")

    for year in df.index.year.unique():
        if str(year) == str(datetime.now().year):
            continue
        plt.figure(figsize=(16, 8))

        # Create the primary y-axis
        ax1 = plt.gca()
        ax1.set_ylabel("Blood Donations (Normal Range)")

        # Create the secondary y-axis
        ax2 = ax1.twinx()
        ax2.set_ylabel("Blood Donations (Large Range)")

        num_hospitals = len(df["hospital"].unique())

        caption = create_message(df, year)

        for i, hospital in enumerate(df["hospital"].unique()):
            color_index = i / (num_hospitals - 1) * 0.85

            hospital_yearly_data = df[
                (df.index.year == year) & (df["hospital"] == hospital)
            ]

            monthly_data = hospital_yearly_data.resample("ME").sum()

            # Plotting for each hospital
            if hospital == "Pusat Darah Negara":
                # Plot on secondary y-axis
                ax2.plot(
                    monthly_data.index.month,
                    monthly_data["daily"],
                    label=hospital + " (Large Range)",
                    color="red",
                    linestyle="-",
                    marker="x",
                )
            else:
                # Plot on primary y-axis
                ax1.plot(
                    monthly_data.index.month,
                    monthly_data["daily"],
                    label=hospital,
                    color=cmap(color_index),
                    marker=next(markers),
                    linestyle=next(line_styles),
                )

        # Plot settings
        plt.title(f"Monthly Blood Donations in {year}")
        plt.xlabel("Month")
        ax1.set_xticks(range(1, 13))  # Set x-ticks to be each month
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

        images_and_captions.append([plot_stream, caption])

    return images_and_captions


def retent_transform(donor_retent, year_range=None):
    current_year = datetime.now().year
    if year_range:
        start_year = current_year - year_range
        recent_visits = donor_retent[donor_retent["visit_date"].dt.year >= start_year]
    else:
        recent_visits = donor_retent

    # Filter for donors who visited more than once
    visit_counts_recent = recent_visits.groupby("donor_id")["visit_date"].nunique()
    frequent_donors_recent = recent_visits[
        recent_visits["donor_id"].isin(
            visit_counts_recent[visit_counts_recent > 1].index
        )
    ]

    # Calculate current age
    frequent_donors_recent["curr_age"] = (
        current_year - frequent_donors_recent["birth_date"]
    )

    # Define age ranges
    age_ranges_recent = pd.cut(
        frequent_donors_recent["curr_age"],
        bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float("inf")],
        right=False,
        labels=[
            "0-9",
            "10-19",
            "20-29",
            "30-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80-89",
            "90-99",
            "100+",
        ],
    )

    # Group by age range and count unique donors in each range
    age_range_counts_recent = frequent_donors_recent.groupby(age_ranges_recent)[
        "donor_id"
    ].nunique()

    # Creating bar plots for each age range
    plt.figure(figsize=(10, 6))
    age_range_counts_recent.plot(kind="bar")
    if year_range:
        if year_range == 1:
            title = (
                "Number of Donors by Age Range (More than one visit in the past year)"
            )
        elif year_range > 1:
            title = f"Number of Donors by Age Range (More than one visit in the past {year_range} years)"
    else:
        title = "Number of Donors by Age Range (More than one visit)"

    plt.title(title)
    plt.xlabel("Age Range")
    plt.ylabel("Number of Donors")
    plt.xticks(rotation=45)

    plot_stream = BytesIO()
    plt.savefig(plot_stream, format="png", bbox_inches="tight")
    plot_stream.seek(0)
    plt.close()

    return plot_stream, title
