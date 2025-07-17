import datetime


def format_weather_FA(weather_data: dict) -> str:
    if weather_data["status"] != "success":
        return f"اطلاعاتی در دسترس نیست برای {weather_data['location']}."

    forecast = weather_data["forecasts"][0] if weather_data["forecasts"] else None
    if not forecast:
        return f"اطلاعاتی در دسترس نیست برای {weather_data['location']}."

    result = f"وضعیت آب‌وهوا در {weather_data['location']}:\n"
    result += f"- تاریخ: {forecast['date']}\n"
    result += f"- دما: {forecast['temperature']} درجه سانتی‌گراد\n"
    result += f"- دمای احساس‌شده: {forecast['feels_like']} درجه سانتی‌گراد\n"
    result += f"- رطوبت: {forecast['humidity']} درصد\n"
    result += f"- وضعیت هوا: {forecast['weather']}\n"
    result += f"- سرعت باد: {forecast['wind_speed']} متر بر ثانیه\n"
    result += f"- فشار هوا: {forecast['pressure']} هکتوپاسکال\n"
    return result



def format_news_FA(news_data: str) -> str:
    if not news_data or "Request failed" in news_data or news_data.strip() == "No news found.":
        return "در حال حاضر خبری در دسترس نیست."
    lines = news_data.strip().split("\n")
    news_text = "آخرین عناوین خبری به شرح زیر است:\n"
    for line in lines:
        news_text += f"- {line}\n"
    news_text += "این اخبار به‌روز هستند."
    return news_text



def format_weather_En(weather_data: dict) -> str:
    if weather_data["status"] != "success" or not weather_data.get("forecasts"):
        return f"No weather data available for {weather_data.get('location', 'unknown')}."

    forecast = weather_data["forecasts"][0]

    return (
        f"Weather report for {weather_data['location']}:\n"
        f"- Date: {forecast['date']}\n"
        f"- Temperature: {forecast['temperature']}°C\n"
        f"- Feels Like: {forecast['feels_like']}°C\n"
        f"- Humidity: {forecast['humidity']}%\n"
        f"- Condition: {forecast['weather']}\n"
        f"- Wind Speed: {forecast['wind_speed']} m/s\n"
        f"- Pressure: {forecast['pressure']} hPa"
    )


def format_news_En(news_data: str) -> str:
    if not news_data or "Request failed" in news_data or news_data.strip() == "No news found.":
        return "No news is available right now."
    lines = news_data.strip().split("\n")
    news_text = "Here are the latest news headlines:\n"
    for line in lines:
        news_text += f"- {line}\n"
    news_text += "This news is up to date."
    return news_text


