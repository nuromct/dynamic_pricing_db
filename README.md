# Dynamic Pricing and Inventory Management System

## Overview
This project is an advanced e-commerce backend system that implements **Dynamic Pricing** strategies based on real-time **Inventory Levels**. It uses a PostgreSQL database with triggers to automatically adjust product prices when stock is low (increase price) or high (decrease price).

## Project Structure (What does each file do?)

### Backend (Python)
*   **`main.py`**: The main **FastAPI** application. It serves the API endpoints for products, orders, users, and the dashboard. It also serves the static frontend files.
*   **`database.py`**: Handles the connection to the PostgreSQL database using `psycopg2`.
*   **`generate_data.py`**: A utility script to populate the database with realistic **dummy data** (Users, Products, Orders) for testing purposes.
*   **`simulate_orders.py`**: A simulation script that creates live orders every few seconds to test the dynamic pricing logic and triggers in real-time.
*   **`apply_triggers.py`**: A helper script to apply the SQL triggers (`04_create_triggers.sql`) to the database.

### Database (SQL)
*   **`01_create_tables.sql`**: Defines the database schema (Tables: User, Product, Inventory, etc.).
*   **`02_insert_dummy_data.sql`**: Contains static sample data (optional, `generate_data.py` is preferred for large datasets).
*   **`03_sample_queries.sql`**: A collection of useful SQL queries for analytics and debugging.
*   **`04_create_triggers.sql`**: The core logic! Defines the PL/pgSQL functions and triggers for dynamic pricing.
*   **`05_user_unique_constraints.sql`**: Adds constraints to ensure data integrity.

### Frontend
*   **`static/` Folder**: Contains the HTML, CSS, and JavaScript files for the web interface.
    *   `index.html`: Admin Dashboard.
    *   `store.html`: Customer e-commerce store.

## Installation & Setup

1.  **Prerequisites**:
    *   Python 3.x
    *   PostgreSQL installed and running.

2.  **Database Setup**:
    *   Create a database named `dynamic_pricing_db`.
    *   Run the SQL scripts to set up tables and triggers.

3.  **Environment Variables**:
    *   Create a `.env` file in the root directory with your DB credentials:
        ```
        DB_HOST=localhost
        DB_NAME=dynamic_pricing_db
        DB_USER=postgres
        DB_PASSWORD=your_password
        ```

4.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn psycopg2-binary python-dotenv faker
    ```

## How to Run

1.  **Initialize Data**:
    ```bash
    python generate_data.py
    ```
    *(This will clear old data and create new users, products, and orders)*

2.  **Start the Server**:
    ```bash
    uvicorn main:app --reload
    ```
    *   Access the **Dashboard** at: `http://127.0.0.1:8000`
    *   Access the **Store** at: `http://127.0.0.1:8000/store`
    *   API Docs: `http://127.0.0.1:8000/docs`

3.  **Run Simulation (Optional)**:
    To see the dynamic pricing in action without clicking manually:
    ```bash
    python simulate_orders.py
    ```
    *   Watch the console output as orders are placed and prices change!
