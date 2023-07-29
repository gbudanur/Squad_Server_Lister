import os
import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox

SERVER_INFO_ENDPOINT = "https://api.steampowered.com/IGameServersService/GetServerList/v1/"
SERVER_CACHE_FILE = os.path.join(os.path.dirname(__file__), "server_cache.json")

def get_api_key():
    api_key = input("Enter your Steam API key: ").strip()
    return api_key

def get_server_info(api_key, server_ip):
    try:
        params = {
            "key": api_key,
            "filter": f"addr\\{server_ip}"
        }
        response = requests.get(SERVER_INFO_ENDPOINT, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the API call: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding API response: {e}")
        return None

def format_map_name(map_name):
    parts = map_name.split("_")
    return f"Map: {parts[0]} {parts[2]} {parts[1]}"

def display_server_info(server_info, text_box):
    if server_info and "response" in server_info and "servers" in server_info["response"]:
        server_data = server_info["response"]["servers"][0]
        server_name = server_data["name"]
        player_count = server_data["players"]
        max_players = server_data["max_players"]
        waiting_players = max(0, player_count - max_players)
        map_name = format_map_name(server_data["map"])

        if waiting_players > 0:
            player_count_str = f"{max_players}/{max_players} +{waiting_players} in queue"
        else:
            player_count_str = f"{player_count}/{max_players}"

        text_box.insert(tk.END, f"Server Name: {server_name}\n")
        text_box.insert(tk.END, f"Players: {player_count_str}\n")
        text_box.insert(tk.END, f"{map_name}\n\n")
    else:
        text_box.insert(tk.END, "Server not found or invalid response.\n\n")

def save_data(api_key, server_ips):
    data = {
        "api_key": api_key,
        "server_ips": list(server_ips),
    }
    with open(SERVER_CACHE_FILE, "w") as file:
        json.dump(data, file)

def load_data():
    try:
        with open(SERVER_CACHE_FILE, "r") as file:
            data = json.load(file)
            api_key = data.get("api_key")
            server_ips = set(data.get("server_ips", []))
            return api_key, server_ips
    except FileNotFoundError:
        return None, set()

def add_server():
    global API_KEY, entry

    server_ip = entry.get()
    server_info = get_server_info(API_KEY, server_ip)

    if server_info:
        server_list.insert(tk.END, f"Server IP: {server_ip}")
        display_server_info(server_info, server_list)
        server_list.insert(tk.END, "")  

        server_ips.add(server_ip)
        save_data(API_KEY, server_ips)
    else:
        messagebox.showerror("Error", "Server not found or invalid response.")

def quit_app():
    save_data(API_KEY, server_ips)
    root.destroy()

def update_server_info():
    server_list.delete(0, tk.END)  
    for server_ip in server_ips:
        server_info = get_server_info(API_KEY, server_ip)
        server_list.insert(tk.END, f"Server IP: {server_ip}")
        display_server_info(server_info, server_list)
        server_list.insert(tk.END, "")  

    root.after(15000, update_server_info)

def create_gui():
    global root, entry, server_list

    root = tk.Tk()
    root.title("burulma momenti iftiharla sunar")

    style = ttk.Style(root)
    style.theme_use("clam")

    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    label = ttk.Label(main_frame, text="Enter Server IP:")
    label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    entry = ttk.Entry(main_frame, width=20)
    entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    add_button = ttk.Button(main_frame, text="Add Server", command=add_server)
    add_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    server_list = tk.Listbox(main_frame, width=60, height=15, selectmode=tk.SINGLE)
    server_list.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    quit_button = ttk.Button(main_frame, text="Quit", command=quit_app)
    quit_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(1, weight=1)

    for server_ip in server_ips:
        server_info = get_server_info(API_KEY, server_ip)
        server_list.insert(tk.END, f"Server IP: {server_ip}")
        display_server_info(server_info, server_list)
        server_list.insert(tk.END, "") 

    root.after(15000, update_server_info)

    root.mainloop()

if __name__ == "__main__":
    API_KEY, server_ips = load_data()
    if API_KEY is None:
        API_KEY = get_api_key()
    create_gui()
