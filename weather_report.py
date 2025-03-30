import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
import random

favorites = []


def get_weather_data(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        return weather_data
    except requests.exceptions.RequestException as err:
        print(f"Error fetching weather data: {err}")
        return None


def show_weather():
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city.")
        return
    update_weather(city)


def update_weather(city):
    data = get_weather_data(city)
    if data:
        try:
            name = data['name']
            desc = data['weather'][0]['description'].title()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']

            weather_info = (
                f"{name}\n"
                f"{desc}\n"
                f"Temperature: {temp}°C\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind} m/s"
            )
            weather_label.config(text=weather_info)

            icon_code = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            icon_response = requests.get(icon_url, stream=True)
            if icon_response.status_code == 200:
                icon_data = Image.open(icon_response.raw)
                icon_image = ImageTk.PhotoImage(icon_data)
                icon_label.config(image=icon_image)
                icon_label.image = icon_image

            apply_color_scheme(desc.lower())
            plot_temp_graph(city)

        except Exception as e:
            weather_label.config(text="Error parsing weather data.")
            print(f"Parsing error: {e}")
    else:
        weather_label.config(text="Could not retrieve data.")


def apply_color_scheme(description):
    color_map = {
        "clear": "#87CEEB",        # Sky blue
        "cloud": "#d3d3d3",        # Light gray
        "rain": "#a4b0be",         # Muted blue-gray
        "thunder": "#57606f",      # Dark gray
        "snow": "#ffffff",         # White
        "mist": "#cfd8dc",         # Misty gray
        "fog": "#cfd8dc",          # Foggy gray
        "haze": "#f0e68c"           # Khaki yellow
    }

    bg_color = "#f5f5f5"  # Default fallback
    for key, color in color_map.items():
        if key in description:
            bg_color = color
            break

    root.configure(bg=bg_color)
    style.configure("TLabel", background=bg_color)
    style.configure("TFrame", background=bg_color)
    style.configure("TLabelframe", background=bg_color)
    style.configure("TLabelframe.Label", background=bg_color)


def plot_temp_graph(city):
    dates = []
    temps = []

    for i in range(5):
        date_obj = datetime.now(timezone.utc) - timedelta(days=i+1)
        date_str = date_obj.strftime("%b %d")
        temp = random.randint(18, 30)  # Simulated temperature

        dates.append(date_str)
        temps.append(temp)

    fig, ax = plt.subplots(figsize=(4, 2))
    ax.plot(dates[::-1], temps[::-1], marker='o')
    ax.set_title(f"5-Day Temp Trend - {city}", fontsize=10)
    ax.set_ylabel("°C")
    ax.grid(True)

    for widget in graph_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


def add_to_favorites():
    city = city_entry.get().strip()
    if city and city not in favorites:
        favorites.append(city)
        update_favorite_buttons()
    elif city in favorites:
        messagebox.showinfo("Info", f"{city} is already in favorites.")


def remove_from_favorites(city):
    if city in favorites:
        favorites.remove(city)
        update_favorite_buttons()


def update_favorite_buttons():
    for widget in fav_frame.winfo_children():
        widget.destroy()
    for city in favorites:
        container = ttk.Frame(fav_frame)
        container.pack(fill="x", pady=2)

        city_btn = ttk.Button(container, text=city, command=lambda c=city: update_weather(c))
        city_btn.pack(side=tk.LEFT, padx=(0, 5))

        del_btn = ttk.Button(container, text="🗑", width=3, command=lambda c=city: remove_from_favorites(c))
        del_btn.pack(side=tk.LEFT)


root = tk.Tk()
root.title("Modern Weather App")
root.geometry("520x700")
root.configure(bg="#f5f5f5")

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 11), background="#f5f5f5")

header = ttk.Label(root, text="🌤️ Weather App", font=("Segoe UI", 16, "bold"))
header.pack(pady=10)

search_frame = ttk.Frame(root)
search_frame.pack(pady=10)

city_entry = ttk.Entry(search_frame, width=30, font=("Segoe UI", 11))
city_entry.pack(side=tk.LEFT, padx=5)

search_btn = ttk.Button(search_frame, text="Search", command=show_weather)
search_btn.pack(side=tk.LEFT, padx=5)

refresh_btn = ttk.Button(search_frame, text="⟳", command=lambda: update_weather(city_entry.get()))
refresh_btn.pack(side=tk.LEFT)

add_fav_btn = ttk.Button(root, text="➕ Add to Favorites", command=add_to_favorites)
add_fav_btn.pack(pady=5)

weather_card = ttk.Frame(root, padding=10, style="Card.TFrame")
weather_card.pack(pady=10)

weather_label = ttk.Label(weather_card, text="Enter a city to get weather", anchor="center", justify="center")
weather_label.pack(pady=5)

icon_label = ttk.Label(weather_card)
icon_label.pack()

fav_frame = ttk.LabelFrame(root, text="Favorites", padding=10)
fav_frame.pack(pady=10)

graph_frame = ttk.Frame(root)
graph_frame.pack(pady=20)

root.mainloop()