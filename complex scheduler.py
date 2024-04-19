import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import sqlite3

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize the scheduler
scheduler = BackgroundScheduler(timezone="Etc/GMT-2")

# Connect to SQLite database
conn = sqlite3.connect('jobs.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table to store job start times if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS jobs
                  (id TEXT PRIMARY KEY, start_time TEXT)''')
conn.commit()

# Retrieve job start times from the database
cursor.execute('SELECT * FROM jobs')
rows = cursor.fetchall()
job_start_times = {row[0]: row[1] for row in rows}

# Define a global variable to store the execution status
execution_status = ""

# Define a function to perform the scheduled task
def scheduled_task(job_id):
    global execution_status
    execution_status = f"Scheduled task {job_id} executed at {datetime.now()}"
    print(execution_status)
    # Update the layout to display the execution status
    app.layout = html.Div([
        html.Div(id='job-list', children=[
            html.H2("List of Jobs"),
            html.Ul(id='job-ul', children=[html.Li(f"Job ID: {job_id}, Scheduled Time: {scheduled_time}") for job_id, scheduled_time in job_start_times.items()])
        ]),
        dcc.Input(id='job-id-input', type='text', placeholder='Enter job ID'),
        dcc.Input(id='scheduled-time-input', type='text', placeholder='Enter scheduled time (e.g., 09:00)'),
        html.Button('Schedule Task', id='schedule-button'),
        html.Div(id='output-container-button'),
        html.Div(id='execution-status', children=execution_status)  # Add this div to display the execution status
    ])

# Define a function to add a new job to the scheduler
def add_job_to_scheduler(job_id, scheduled_time):
    # Convert the scheduled time string to a time object
    scheduled_time_obj = datetime.strptime(scheduled_time, '%H:%M')
    
    # Generate the cron expression for the provided time (hour and minute)
    cron_expression = f"{scheduled_time_obj.minute} {scheduled_time_obj.hour} * * *"
    
    # Add the job to the scheduler
    scheduler.add_job(scheduled_task, CronTrigger.from_crontab(cron_expression), args=[job_id])

# Update the layout to display the execution status and current jobs
app.layout = html.Div([
    html.Div(id='job-list', children=[
        html.H2("List of Jobs"),
        html.Ul(id='job-ul', children=[html.Li(f"Job ID: {job_id}, Scheduled Time: {scheduled_time}") for job_id, scheduled_time in job_start_times.items()])
    ]),
    dcc.Input(id='job-id-input', type='text', placeholder='Enter job ID'),
    dcc.Input(id='scheduled-time-input', type='text', placeholder='Enter scheduled time (e.g., 09:00)'),
    html.Button('Schedule Task', id='schedule-button'),
    html.Div(id='output-container-button'),
    html.Div(id='execution-status')  # Add this div to display the execution status
])

# Define callback to schedule the task and update the job list
@app.callback(
    Output('job-list', 'children'),
    [Input('schedule-button', 'n_clicks')],
    [Input('job-id-input', 'value'),
     Input('scheduled-time-input', 'value')]
)
def schedule_task(n_clicks, job_id, scheduled_time):
    if n_clicks:
        if job_id and scheduled_time:
            # Store job start time in the database
            with conn:
                cursor.execute('INSERT OR REPLACE INTO jobs (id, start_time) VALUES (?, ?)', (job_id, scheduled_time))
            
            # Add the job to the scheduler
            add_job_to_scheduler(job_id, scheduled_time)
            
            # Update the job list display
            cursor.execute('SELECT * FROM jobs')
            rows = cursor.fetchall()
            job_start_times.update({row[0]: row[1] for row in rows})
            
            return [
                html.H2("List of Jobs"),
                html.Ul(id='job-ul', children=[html.Li(f"Job ID: {job_id}, Scheduled Time: {scheduled_time}") for job_id, scheduled_time in job_start_times.items()])
            ]
    return []

# Update the execution status in the Dash app
@app.callback(
    Output('execution-status', 'children'),
    [Input('schedule-button', 'n_clicks')]
)
def update_execution_status(n_clicks):
    if n_clicks:
        return html.Div(execution_status)
    else:
        return html.Div()

# Start the scheduler when the Dash app is run
if __name__ == '__main__':
    # Start the scheduler
    scheduler.start()
    
    # Run the Dash app
    app.run_server(debug=True)
