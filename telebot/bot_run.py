import os
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import pandas as pd
from io import StringIO

from process import create_image_and_captions, retent_transform
from weekly_process import donation_amnt, donation_by_state, regular_donation_by_state, donation_by_facility
from bot_send import send_telegram_message, try_send_three_times

TOKEN = os.environ.get("TOKEN")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await send_telegram_message(GROUP_CHAT_ID, "Bot Initiated")
    yield
    logging.info("Application is shutting down.")


app = FastAPI(lifespan=app_lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/etl/")
async def receive_etl(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "ERROR: Message not found.")
        await send_telegram_message(GROUP_CHAT_ID, message)

        if message == "New commit found. Triggering ETL process.":

            donor_retent = pd.read_parquet('blood_donation_retention_2024.parquet', engine='pyarrow')
            donor_retent['visit_date'] = pd.to_datetime(donor_retent['visit_date'])
            donor_retent['birth_date'] = donor_retent['birth_date'].astype(int)
            donor_retent_all_years_img, donor_retent_all_years_capt = retent_transform(donor_retent)
            await try_send_three_times(GROUP_CHAT_ID, donor_retent_all_years_img, donor_retent_all_years_capt)
            for year_range in [5, 1]: # send past 5 years trend and past year trend
                donor_retent_year_range_img, donor_retent_year_range_capt = retent_transform(donor_retent, year_range)
                await try_send_three_times(GROUP_CHAT_ID, donor_retent_year_range_img, donor_retent_year_range_capt)

            donate_fac = pd.read_json(StringIO(body.get("donate_fac")), orient="records")
            donate_fac['date'] = pd.to_datetime(donate_fac['date'])
            latest_date = donate_fac['date'].max()
            prev_week = latest_date - pd.Timedelta(days=6)
            this_weeks_data = donate_fac[(donate_fac['date'] >= prev_week) & 
                                                (donate_fac['date'] <= latest_date)].copy()
            images_and_captions = create_image_and_captions(donate_fac)
            for image_and_caption in images_and_captions:
                await try_send_three_times(GROUP_CHAT_ID, image_and_caption[0], image_and_caption[1])
            donation_by_facility_img, donation_by_facility_capt = donation_by_facility(this_weeks_data)
            await try_send_three_times(GROUP_CHAT_ID, donation_by_facility_img, donation_by_facility_capt)

            donate_state = pd.read_json(
                StringIO(body.get("donate_state")), orient="records"
            )
            donate_state['date'] = pd.to_datetime(donate_state['date'])
            donation_amnt_img, donation_amnt_capt = donation_amnt(donate_state)
            await try_send_three_times(GROUP_CHAT_ID, donation_amnt_img, donation_amnt_capt)
            donation_by_state_img, donation_by_state_capt = donation_by_state(donate_state)
            await try_send_three_times(GROUP_CHAT_ID, donation_by_state_img, donation_by_state_capt)
            regular_donation_by_state_img, regular_donation_by_state_capt = regular_donation_by_state(donate_state)
            await try_send_three_times(GROUP_CHAT_ID, regular_donation_by_state_img, regular_donation_by_state_capt)

            new_donors_fac = pd.read_json(
                StringIO(body.get("new_donors_fac")), orient="records"
            )

            new_donors_state = pd.read_json(
                StringIO(body.get("new_donors_state")), orient="records"
            )
        logging.info(f"ETL received and processed: {message}")
        return {"message": "Notification sent to Telegram"}
    except Exception as e:
        logging.error(f"Error processing ETL: {e}")
        raise e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
