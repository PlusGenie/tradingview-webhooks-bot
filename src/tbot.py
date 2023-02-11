#!/usr/bin/env python3
"""
Reading database for Tbot on Tradingboat
"""
import sqlite3
import os
from flask import request, render_template, jsonify
from flask import g
from utils.log import get_logger
from dotenv import load_dotenv

logger = get_logger(__name__)

# Set the default path to the .env file in the user's home directory
DEFAULT_ENV_FILE_PATH = os.path.expanduser("~/.env")

# Check if the .env file exists at the default path; if not, use the fallback path
if os.path.isfile(DEFAULT_ENV_FILE_PATH):
    ENV_FILE_PATH = DEFAULT_ENV_FILE_PATH
else:
    ENV_FILE_PATH = "/home/tbot/.env"

# Load the environment variables from the chosen .env file
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)

def get_db():
    """Get the database"""
    database = getattr(g, "_database", None)
    if database is None:
        database = g._database = sqlite3.connect(
            os.environ.get("TBOT_DB_OFFICE", "/run/tbot/tbot_sqlite3")
        )
        database.row_factory = sqlite3.Row
    return database


def query_db(query, args=()):
    """Query database"""
    try:
        cur = get_db().execute(query, args)
        rows = cur.fetchall()
        unpacked = [{k: item[k] for k in item.keys()} for item in rows]
        cur.close()
    except Exception as err:
        logger.error(f"Failed to execute: {err}")
        return []
    return unpacked


def get_orders():
    """Get IBKR Orders"""
    return render_template(template_name_or_list="orders.html", title="IBKR Orders")


def get_orders_data():
    """Get IBKR Orders for AJAX"""
    rows = query_db("select * from TBOTORDERS")
    return {"data": rows}


def get_alerts():
    """Get TradingView alerts"""
    return render_template(
        template_name_or_list="alerts.html", title="TradingView Alerts to TBOT"
    )


def get_alerts_data():
    """Get TradingView alerts for AJAX"""
    rows = query_db("select * from TBOTALERTS")
    return {"data": rows}


def get_errors():
    """Get TradingView alerts"""
    return render_template(
        template_name_or_list="error.html", title="TradingView Errors to TBOT"
    )


def get_errors_data():
    """Get TradingView errors for AJAX"""
    rows = query_db("select * from TBOTERRORS")
    return {"data": rows}


def get_tbot():
    """Get the holstici view of Tbot"""
    return render_template(
        template_name_or_list="alerts_orders.html",
        title=" TradingView Alerts and IBKR Orders on TBOT",
    )


def get_ngrok():
    """Get NGROK Address"""
    addr = os.environ.get("TBOT_NGROK", "#")
    return {"data": {"address": addr}}


def get_tbot_data():
    """Get the holstici view of Tbot for AJAX"""
    query = (
        "SELECT TBOTORDERS.TIMESTAMP, TBOTORDERS.UNIQUEKEY, TBOTALERTS.TV_TIMESTAMP, "
        "TBOTALERTS.TICKER, TV_PRICE, AVGPRICE, DIRECTION, ACTION, ORDERTYPE, QTY, "
        "TBOTORDERS.POSITION, TBOTALERTS.ORDERREF, ORDERSTATUS "
        "FROM TBOTORDERS INNER JOIN TBOTALERTS ON TBOTALERTS.UNIQUEKEY=TBOTORDERS.UNIQUEKEY "
        "ORDER BY TBOTORDERS.UNIQUEKEY DESC"
    )
    rows = query_db(query)
    return {"data": rows}


def get_main():
    """Get entry point for TradingBoat"""
    if request.method == "GET":
        # Make the open-gui mode in favor of the system-level firewall.
        try:
            os.remove('.gui_key')
        except FileNotFoundError:
            pass

        return render_template(template_name_or_list="tbot_dashboard.html")


def close_connection(exception):
    """Close connection"""
    database = getattr(g, "_database", None)
    if database is not None:
        database.close()
