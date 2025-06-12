def format_weather_Fa(weather_data: dict) -> str:
    if weather_data["status"] != "success":
        return f"## 🌤️ وضعیت آب‌وهوا\n\n❗ اطلاعاتی در دسترس نیست برای **{weather_data['location']}**."

    forecast = weather_data["forecasts"][0] if weather_data["forecasts"] else None
    if not forecast:
        return f"## 🌤️ وضعیت آب‌وهوا\n\n❗ اطلاعاتی در دسترس نیست برای **{weather_data['location']}**."

    return (
        f"## 🌤️ وضعیت آب‌وهوا در {weather_data['location'].title()}\n\n"
        f"**تاریخ:** {forecast['date']}\n"
        f"**دما:** {forecast['temperature']}°C\n"
        f"**احساس واقعی:** {forecast['feels_like']}°C\n"
        f"**رطوبت:** {forecast['humidity']}%\n"
        f"**وضعیت:** {forecast['weather']}\n"
        f"**سرعت باد:** {forecast['wind_speed']} m/s\n"
        f"**فشار هوا:** {forecast['pressure']} hPa\n"
    )


def format_news_Fa(news_data: str) -> str:
    news_md = "## 📰 اخبار امروز\n\n"
    if not news_data or "Request failed" in news_data:
        news_md += "❗ خبری در دسترس نیست."
    else:
        lines = news_data.strip().split("\n")
        for line in lines:
            news_md += f"{line}\n"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    news_md += f"\n**📅 بروزرسانی:** {now}"
    return news_md


def format_weather_En(weather_data: dict) -> str:
    if weather_data["status"] != "success":
        return f"## 🌤️ Weather Status\n\n❗ No weather data available for **{weather_data['location']}**."

    forecast = weather_data["forecasts"][0] if weather_data["forecasts"] else None
    if not forecast:
        return f"## 🌤️ Weather Status\n\n❗ No weather data available for **{weather_data['location']}**."

    return (
        f"## 🌤️ Weather in {weather_data['location'].title()}\n\n"
        f"**Date:** {forecast['date']}  \n"
        f"**Temperature:** {forecast['temperature']}°C  \n"
        f"**Feels Like:** {forecast['feels_like']}°C  \n"
        f"**Humidity:** {forecast['humidity']}%  \n"
        f"**Condition:** {forecast['weather']}  \n"
        f"**Wind Speed:** {forecast['wind_speed']} m/s  \n"
        f"**Pressure:** {forecast['pressure']} hPa"
    )


def format_news_En(news_data: str) -> str:
    news_md = "## 📰 Today's News\n\n"
    if not news_data or "Request failed" in news_data:
        news_md += "❗ No news is available."
    else:
        lines = news_data.strip().split("\n")
        for line in lines:
            news_md += f"{line}\n"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    news_md += f"\n**📅 Updated:** {now}"
    return news_md
