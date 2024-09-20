import streamlit as st
import pandas as pd
import mysql.connector
import openai
from mysql.connector import Error
import subprocess
import os
import sys
import json
import pydeck as pdk
import difflib
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Page configuration
st.set_page_config(page_title="Real World AI-dvertising with SingleStore x GCP", layout="wide")

# Connection details
config = {
    'user': 'admin',
    'password': os.getenv('PASSWORD'),
    'host': os.getenv('HOST'),
    'port': os.getenv('PORT'),
    'database': 'inventory_db'
}
print(config)

def get_db_connection():
    conn = mysql.connector.connect(**config)
    return conn

# Sidebar for navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Map", "Analytics", "Chat with Data"])

# Function to display map
def display_map():
    st.title("Real-time Map")

    # Fetch data from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT Latitude, Longitude, Location_Name
    FROM inventory_table
    WHERE Latitude IS NOT NULL AND Longitude IS NOT NULL
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    if not data:
        st.write("No data available")
        return

    # Set the viewport location to the first data point
    first_location = data[0]
    view_state = pdk.ViewState(
        latitude=first_location['Latitude'],
        longitude=first_location['Longitude'],
        zoom=10,
        pitch=0
    )

    # Create the pydeck layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["Longitude", "Latitude"],
        get_color=[200, 30, 0, 160],
        get_radius=100,
    )

    # Render the deck.gl map
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state
    ))

# Function to display analytics
def display_analytics():
    st.title("Analytics and Reporting")

def get_all_table_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def query_count_by_province():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
        SELECT Province, COUNT(*) as count
        FROM inventory_table
        GROUP BY Province
        ORDER BY count DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            response = "Count of rows per province:\n\n"
            for province, count in results:
                response += f"{province}: {count}\n"
            return response
        else:
            return "No data found for provinces."
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

def query_table_count(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get all table names
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Find the closest matching table name
        closest_match = difflib.get_close_matches(table_name, tables, n=1, cutoff=0.6)
        
        if closest_match:
            actual_table_name = closest_match[0]
            query = f"SELECT COUNT(*) FROM {actual_table_name}"
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return f"The table '{actual_table_name}' has {result} rows."
        else:
            return f"No matching table found for '{table_name}'."
    except Error as e:
        return f"An error occurred: {e}"
    finally:
        cursor.close()
        conn.close()

functions = [
    {
        "name": "query_table_count",
        "description": "Query the count of rows in a specified table",
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "The name of the table to count rows from"
                }
            },
            "required": []
        }
    },
    {
        "name": "query_count_by_province",
        "description": "Query the count of rows per province in the inventory table",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def process_user_input(user_input):
    tables = get_all_table_names()
    table_info = ", ".join(tables)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are an assistant that helps query a database. The available tables are: {table_info}. You can provide row counts for tables and count of rows per province in the inventory table. Use the query_table_count function for general row counts and query_count_by_province function for province-specific counts."},
            {"role": "user", "content": user_input}
        ],
        functions=functions,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])

        if function_name == "query_table_count":
            result = query_table_count(**function_args)
            return result
        elif function_name == "query_count_by_province":
            result = query_count_by_province()
            return result
    else:
        return message.content

# Function to display search
def display_search():
    st.title("Chat with your data")

    # Display available tables
    tables = get_all_table_names()
    st.write(f"Available tables: {', '.join(tables)}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = process_user_input(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Navigation logic
if section == "Map":
    display_map()
elif section == "Analytics":
    display_analytics()
elif section == "Chat with Data":
    display_search()